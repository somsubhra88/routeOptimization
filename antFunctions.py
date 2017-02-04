def nextHub(prob, nodeList):
    from random import random
    from copy import deepcopy
    prob = deepcopy(prob)
    # Removing the Visited Keys
    for r in nodeList:
        del prob[r]
    del prob['Sink']
    try:
        multiplicationFactor = 1/sum(prob.values())
    except ZeroDivisionError:
        return 'Sink'
    else:
        # Updating the probabilities
        for k in prob.keys():
            prob[k] *= multiplicationFactor

        RND = random()
        cumProb = 0

        for i in list(prob.keys()):
            cumProb += prob[i]
            if cumProb > RND:
                return i
# Getting the Route
def path(decisionMatrix):
    noOfVan = len(decisionMatrix)
    Route = {}
    for k in range(noOfVan):
        Route[k] = ['Hub']
        nextTrackingID = None
        iterationCheck = 0
        while nextTrackingID != 'Sink':
            iterationCheck += 1
            currentTrackingID = Route[k][len(Route[k])-1]
            try:
                idx = list(decisionMatrix[k][currentTrackingID].values()).index(1)
            except ValueError:
                break
            else:
                nextTrackingID = list(decisionMatrix[k][currentTrackingID].keys())[idx]
                Route[k].append(nextTrackingID)
            if iterationCheck > 30:
                print("Route is not ending at Hub")
                break
    return Route

def routeEntry(route):
    touredTID = set()
    for i in range(len(route)):
        touredTID  = touredTID | set(route[i])
    return touredTID

def detailPath(route, LatLngData, slotData, timeMatrix, loadData, deliveryTime, addressDetail, directory, fileName):
    from datetime import timedelta
    import csv
    noOfVans = len(route)
    detailPath = [['Van No', 'Start Node', 'Start Latitude', 'Start Longitude', 'End Node', 'End Latitude',
                   'End Longitude','Slot Start Time', 'Slot End Time','Time to Travel','Hitting Time','Slot Adherence',
                   'Load','Pincode','City','State','Address Line 1','Address Line 2']]
    for v in range(noOfVans):
        currentRoute = route[v]
        for s in range(len(currentRoute)-1):
            frm = currentRoute[s]
            Lat_frm = LatLngData[frm]['lat']
            Lng_frm = LatLngData[frm]['lng']

            to = currentRoute[s+1]
            if to != 'Sink':
                Lat_to = LatLngData[to]['lat']
                Lng_to = LatLngData[to]['lng']
            else:
                Lat_to = LatLngData['Hub']['lat']
                Lng_to = LatLngData['Hub']['lng']

            if to != 'Sink':
                slotStartTime = slotData[to]['start']
                slotEndTime = slotData[to]['end']
            else:
                slotStartTime = None
                slotEndTime = None

            t_ij = round(timeMatrix[frm][to], 2)

            if frm == 'Hub':
                hittingTime = slotStartTime + timedelta(hours = deliveryTime)
            else:
                hittingTime = hittingTime + timedelta(hours = t_ij + deliveryTime)

            if to == 'Sink':
                slotAdherence = None
            elif slotStartTime.time() <= hittingTime.time() <= slotEndTime.time():
                slotAdherence = 1
            else:
                slotAdherence = 0

            if to == 'Sink':
                load = None
            else:
                load = loadData[to]

            if to == 'Sink':
                pincode = None
                city = None
                state = None
                addr1 = None
                addr2 = None
            else:
                pincode = addressDetail[to]['address_pincode']
                city = addressDetail[to]['address_city']
                state = addressDetail[to]['address_state']
                addr1 = addressDetail[to]['address_line1']
                addr2 =addressDetail[to]['address_line2']

            detailPath.append([v+1, frm, Lat_frm, Lng_frm, to, Lat_to, Lng_to, slotStartTime, slotEndTime, t_ij,
                               hittingTime, slotAdherence, load, pincode, city, state, addr1, addr2])

    csv.register_dialect('customDialect',delimiter=',', quotechar='"', doublequote=True,skipinitialspace=True,
                         lineterminator='\n',quoting=csv.QUOTE_MINIMAL)
    with open(directory + 'Detail Path - ' + str(fileName) + '.csv','w') as detailPathCSV:
        dataWriter = csv.writer(detailPathCSV, dialect = 'customDialect')
        for row in detailPath:
            dataWriter.writerow(row)

    return detailPath

def routeMetrics(route,timeMatrix, slotData, deliveryTime):
    from datetime import timedelta
    noOfVans = len(route)
    currentTotalCost = 0
    currentSlotAdherence = 0
    for k in range(noOfVans):
        for i in range(len(route[k]) - 1):
            currentTotalCost += timeMatrix[route[k][i]][route[k][i + 1]] + deliveryTime
            if route[k][i + 1] != 'Sink':
                startTime = slotData[route[k][i + 1]]['start']
                endTime = slotData[route[k][i + 1]]['end']
            if route[k][i] == 'Hub':
                hittingTime = startTime + timedelta(hours = deliveryTime)
            else:
                hittingTime = hittingTime + timedelta(hours= timeMatrix[route[k][i]][route[k][i + 1]] + deliveryTime)
            if route[k][i + 1] != 'Sink' and startTime.hour <= hittingTime.hour <= endTime.hour:
                currentSlotAdherence += 1
    currentTotalCost -= noOfVans * deliveryTime
    return {'cost': currentTotalCost , 'slotAdherence': currentSlotAdherence }

def updateRoute(route,timeMatrix, slotData, deliveryTime):
    from copy import deepcopy
    route = deepcopy(route)
    chkRoute = deepcopy(route)
    currentCost = routeMetrics(route,timeMatrix, slotData, deliveryTime)['cost']
    currentSA = routeMetrics(route, timeMatrix, slotData, deliveryTime)['slotAdherence']
    noOfVans = len(chkRoute)
    for k in range(noOfVans):
        chkRoute = deepcopy(route)
        currentRoute = deepcopy(chkRoute[k])
        for i in range(2,len(currentRoute)-1):
            newCurrentRoute = currentRoute[i:-1] + currentRoute[1:i]
            newCurrentRoute.insert(0,'Hub')
            newCurrentRoute.append('Sink')
            chkRoute[k] = newCurrentRoute
            chkCost = routeMetrics(chkRoute,timeMatrix, slotData, deliveryTime)['cost']
            chkSA = routeMetrics(chkRoute,timeMatrix, slotData, deliveryTime)['slotAdherence']
            if 1.01 * currentCost >= chkCost and  currentSA < chkSA:
                route = chkRoute
                currentCost = chkSA
                currentSA = chkSA

    return route
