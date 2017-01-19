def path(decisionMatrix):
    noOfVan = len(decisionMatrix)
    Route = {}
    for k in range(noOfVan):
        Route[k] = ['Hub']
        nextTrackingID = None
        while nextTrackingID != 'Sink':
            currentTrackingID = Route[k][len(Route[k])-1]
            try:
                idx = list(decisionMatrix[k][currentTrackingID].values()).index(1)
            except ValueError:
                break
            else:
                nextTrackingID = list(decisionMatrix[k][currentTrackingID].keys())[idx]
                Route[k].append(nextTrackingID)
    return Route

def routeEntry(route):
    touredTID = set()
    for i in range(len(route)):
        touredTID  = touredTID | set(route[i])
    return touredTID