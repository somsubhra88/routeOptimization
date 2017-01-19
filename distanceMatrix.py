def distanceMatrix(file, Hub):
    from geoCodeAPI import point, distance
    from datetime import datetime
    import pickle
    import csv
    import os.path
    inputFile = open(str(file), 'r')
    data = csv.reader(inputFile)
    headers = next(data)

    column = {}
    for h in headers:
        column[h] = []

    for row in data:
        for h, v in zip(headers, row):
            column[h].append(v)

    # Considering the node 0 is the Hub
    column['tracking_id'].insert(0, 'Hub')

    ### Saving The Tracking IDs to use in the Optimization Model
    trackingID = column['tracking_id']
    pickle.dump(trackingID, open("trackingID.p", "wb"))

    # Creating a Blank Dictionary Lat-Lng Data
    LatLngData = {}
    LatLngData = {'Hub': Hub}

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

    pickle.dump(addressDetail, open("addressDetail.p", "wb"))

    # Resolving Lat-Lng
    if os.path.exists('LatLngData.p'):
        LatLngData = pickle.load(open('LatLngData.p', 'rb'))
    else:
        for i in range(1, len(column['tracking_id'])):
            print(column['tracking_id'][i])
            LatLngData[column['tracking_id'][i]] = point(column['address_line1'][i - 1],
                                                     column['address_line2'][i - 1],
                                                     column['address_pincode'][i - 1],
                                                     column['address_city'][i - 1],
                                                     column['address_state'][i - 1])
        ### Saving the Lat Lng Data
        pickle.dump(LatLngData, open("LatLngData.p", "wb"))

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
        idx = column['tracking_id'][1:].index(tID)
        pinCode = column['address_pincode'][idx]
        if pinCode in beatCol['Pin Code']:
            beatInf[tID] = beatCol['Beat'][beatCol['Pin Code'].index(pinCode)]
        else:
            print('Beat Information is Missing for ' + pinCode)
            pinCodeDiff = []
            pinCodeDiff[:] = [ abs(x - int(pinCode)) for x in list(map(int, beatCol['Pin Code']))]
            beatInf[tID] = beatCol['Beat'][pinCodeDiff.index(min(pinCodeDiff))]


    # Saving The Beat Data
    pickle.dump(beatInf, open("beatInf.p", "wb"))

    # Forming the Time Matrix
    if os.path.exists('timeMatrix.p'):
        timeMatrix = pickle.load(open('timeMatrix.p', 'rb'))
    else:
        timeMatrix = {}
        for s in column['tracking_id']:
            timeMatrix[s] = {}
            for d in column['tracking_id']:
                timeMatrix[s][d] = None

    for source in column['tracking_id']:
        for destination in column['tracking_id']:
            print("Source -> " + source + " Destinations -> " + destination)
            if (source == destination):
                timeMatrix[source][destination] = 0
            else:
                if (timeMatrix[destination][source] is not None):
                    timeMatrix[source][destination] = timeMatrix[destination][source]
                else:
                    timeMatrix[source][destination] = distance(LatLngData[source], LatLngData[destination])
                    pickle.dump(timeMatrix, open("timeMatrix.p", "wb"))
    # Saving the Time Matrix
    pickle.dump(timeMatrix, open("timeMatrix.p", "wb"))
    # Slot Data
    slotData = {}
    for tID in column['tracking_id'][1:]:
        idx = column['tracking_id'][1:].index(tID)
        slotData[tID] = {'start': datetime.strptime(column['slot_start_dt'][idx], '%d-%m-%Y %H.%M'),
                         'end': datetime.strptime(column['slot_end_dt'][idx], '%d-%m-%Y %H.%M')}
    # Saving the Slot Data
    pickle.dump(slotData, open("slotData.p", "wb"))
    # Load Data
    loadData = {}
    for tID in column['tracking_id'][1:]:
        idx = column['tracking_id'][1:].index(tID)
        loadData[tID] = float(column['fsn_length'][idx]) * float(column['fsn_breadth'][idx]) * float(
            column['fsn_height'][idx]) / 12 ** 3
    # Saving The Load Data
    pickle.dump(loadData, open("loadData.p", "wb"))
