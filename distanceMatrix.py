def distanceMatrix(file, Hub):
    from geoCodeAPI import point, distance
    from dynamicBeat import dynamicBeat
    from datetime import datetime
    import pickle
    import csv
    import os.path
    from os import remove
    import progressbar
    inputFile = open(str(file), 'r')
    data = csv.reader(inputFile)
    headers = next(data)

    column = {}
    for h in headers:
        column[h] = []

    for row in data:
        for h, v in zip(headers, row):
            column[h].append(v)
    # --------------------------------------------------------------------------
    def delKeys(dict, list):
        for _ in list:
            if _ in dict:
                del(dict[_])
        return dict
    # --------------------------------------------------------------------------
    # Considering the node 0 is the Hub
    column['tracking_id'].insert(0, 'Hub')

    ### Saving The Tracking IDs to use in the Optimization Model
    trackingID = column['tracking_id']
    pickle.dump(trackingID, open("trackingID.p", "wb"))

    # Creating a Blank Dictionary Lat-Lng Data
    LatLngData = {}
    LatLngData = {'Hub': Hub}

    # Crating a progress bar for Latitude and Longitude
    bar = progressbar.ProgressBar(maxval = len(column['tracking_id']) - 1, widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()
    print('---- Latitude and Longitude Loop is started ----')
    # Resolving Lat-Lng
    unresolvedTrackingID = []
    if os.path.exists('LatLngData.p'):
        LatLngData = pickle.load(open('LatLngData.p', 'rb'))
        if set(trackingID) != set(LatLngData.keys()):
            print('Removing Old latitude and longitude pickle File as it is not amtching with the recent Tracking IDs')
            remove('LatLngData.p')
            for i in range(1, len(column['tracking_id'])):
                bar.update(i)
                try:
                    LatLngData[column['tracking_id'][i]] = point(column['address_line1'][i - 1],
                                                             column['address_line2'][i - 1],
                                                             column['address_pincode'][i - 1],
                                                             column['address_city'][i - 1],
                                                             column['address_state'][i - 1])
                except:
                    unresolvedTrackingID.append(column['tracking_id'][i])
        else:
            print('Previous latitude and longitude data is good enough to continue')
    else:
        print('There is no old data for latitude and longitude, hence creating a new one')
        for i in range(1, len(column['tracking_id'])):
            bar.update(i)
            try:
                LatLngData[column['tracking_id'][i]] = point(column['address_line1'][i - 1],
                                                         column['address_line2'][i - 1],
                                                         column['address_pincode'][i - 1],
                                                         column['address_city'][i - 1],
                                                         column['address_state'][i - 1])
            except:
                unresolvedTrackingID.append(column['tracking_id'][i])
    bar.finish()
    print('---- latitude and longitude Iteration is Done ----')
    ### Saving the Lat Lng Data
    pickle.dump(LatLngData, open("LatLngData.p", "wb"))

    # Removing the Unresolved Tracking ID's from the Tracking ID list
    trackingID = [x for x in trackingID if x not in unresolvedTrackingID]
    pickle.dump(trackingID, open("trackingID.p", "wb"))

    # Address Details
    addressDetail = {}
    for tID in column['tracking_id'][1:]:
        idx = column['tracking_id'][1:].index(tID)
        addressDetail[tID] = {'address_line1' : column['address_line1'][idx],
                              'address_line2' : column['address_line2'][idx],
                              'address_pincode' : column['address_pincode'][idx],
                              'address_city' : column['address_city'][idx],
                              'address_state' : column['address_state'][idx]
                              }

    addressDetail = delKeys(addressDetail, unresolvedTrackingID)
    pickle.dump(addressDetail, open("addressDetail.p", "wb"))

    # Forming the Time Matrix
    print('---- Time Matrix Iteration is Started ----')
    if os.path.exists('timeMatrix.p'):
        timeMatrix = pickle.load(open('timeMatrix.p', 'rb'))
        if set(trackingID) != set(timeMatrix.keys()):
            remove('timeMatrix.p')
            print('Removing the Old Time Matrix and Creating a New Blank Time Matrix')
            timeMatrix = {}
            for s in trackingID:
                timeMatrix[s] = {}
                for d in trackingID:
                    timeMatrix[s][d] = None
        else:
            print('Old Time Matrix is Good enough to continue')
    else:
        print('There is no old Time Matrix exists, hence creating a blank Time Matrix')
        timeMatrix = {}
        for s in trackingID:
            timeMatrix[s] = {}
            for d in trackingID:
                timeMatrix[s][d] = None

    # Creating a Progress Bar for Time Matrix
    bar = progressbar.ProgressBar(maxval = len(trackingID)**2, widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    barCounter = 0
    bar.start()
    print('Time Matrix creation is Started')
    for source in trackingID:
        for destination in trackingID:
            barCounter += 1
            bar.update(barCounter)

            if (source == destination):
                timeMatrix[source][destination] = 0
            else:
                if (timeMatrix[destination][source] is not None):
                    timeMatrix[source][destination] = timeMatrix[destination][source]
                else:
                    while True:
                        try:
                            dist = distance(LatLngData[source], LatLngData[destination])
                        except:
                            continue
                        else:
                            break

                    timeMatrix[source][destination] = dist
                    pickle.dump(timeMatrix, open("timeMatrix.p", "wb"))

    bar.finish()
    print('---- Time Matrix Iteration is Finished ----')
    # Saving the Time Matrix
    pickle.dump(timeMatrix, open("timeMatrix.p", "wb"))
    # Slot Data
    def try_parsing_date(text):
        for fmt in ('%m/%d/%Y %H:%M', '%d-%m-%Y %H.%M', '%Y-%m-%d %H:%M:%S'):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                pass
        raise ValueError('no valid date format found')

    slotData = {}
    missingSlot = []
    for tID in column['tracking_id'][1:]:
        idx = column['tracking_id'][1:].index(tID)
        if (column['slot_start_dt'][idx] is not None and column['slot_start_dt'][idx] != ''):
            slotData[tID] = {'start': try_parsing_date(column['slot_start_dt'][idx]), 'end': try_parsing_date(column['slot_end_dt'][idx])}
        else:
            missingSlot.append(tID)

    # Missing Slot - Converting it to Minimum Slot Start Time and Max Slot End Time
    if(len(missingSlot) > 0):
        minSlotStartTime, maxSlotEndTime = datetime.strptime('08:00', '%H:%M').time(), datetime.strptime('20:00', '%H:%M').time()
        for tID in [x for x in column['tracking_id'][1:] if x not in missingSlot]:
            if slotData[tID]['start'].time() < minSlotStartTime:
                minSlotStartTime = slotData[tID]['start'].time()
            if slotData[tID]['end'].time() > maxSlotEndTime:
                maxSlotEndTime = slotData[tID]['end'].time()

        missingSlotStart, missingSlotEnd = datetime.combine(datetime.now().date(), minSlotStartTime), datetime.combine(datetime.now().date(), maxSlotEndTime)
        for tID in missingSlot:
            slotData[tID] = {'start': missingSlotStart, 'end': missingSlotEnd}

    # Saving the Slot Data
    slotData = delKeys(slotData, unresolvedTrackingID)
    pickle.dump(slotData, open("slotData.p", "wb"))
    # Load Data
    loadData = {}
    for tID in column['tracking_id'][1:]:
        idx = column['tracking_id'][1:].index(tID)
        loadData[tID] = float(column['fsn_length'][idx]) * float(column['fsn_breadth'][idx]) * float(column['fsn_height'][idx]) / 12 ** 3
    # Saving The Load Data
    loadData = delKeys(loadData, unresolvedTrackingID)
    pickle.dump(loadData, open("loadData.p", "wb"))

    # Dynamic Beat
    pincodeList = []
    for tID in [x for x in trackingID if x not in ['Hub']]:
        pincodeList.append(addressDetail[tID]['address_pincode'])
    pincodeList = list(set(pincodeList))
    # Volumetric Load Calculation
    load = {}
    for i in pincodeList:
        load[i] = 0

    for tID in [x for x in trackingID if x not in ['Hub']]:
        load[addressDetail[tID]['address_pincode']] += loadData[tID]
    dynamicBeat(pincodeList, 'Pincode Merging.csv', load, 125)
    # Beat Mapping
    beatFile = open("Beat.csv", 'r')
    beat = csv.reader(beatFile)
    headers = next(beat)

    beatCol = {}
    for h in headers:
        beatCol[h] = []

    for row in beat:
        for h, v in zip(headers, row):
            beatCol[h].append(v)

    beatInf = {}
    for tID in column['tracking_id'][1:]:
        if tID not in unresolvedTrackingID:
            idx = column['tracking_id'][1:].index(tID)
            pinCode = column['address_pincode'][idx]
            if pinCode in beatCol['Pin Code']:
                beatInf[tID] = beatCol['Beat'][beatCol['Pin Code'].index(pinCode)]
            else:
                print('Beat Information is Missing for ' + pinCode)
                pinCodeDiff = []
                pinCodeDiff[:] = [ abs(x - int(pinCode)) for x in list(map(int, beatCol['Pin Code']))]
                beatInf[tID] = beatCol['Beat'][pinCodeDiff.index(min(pinCodeDiff))]

    beatInf = delKeys(beatInf, unresolvedTrackingID)
    # Saving The Beat Data
    pickle.dump(beatInf, open("beatInf.p", "wb"))
