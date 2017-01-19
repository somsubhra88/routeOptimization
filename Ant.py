# Calculation of Time Matrix, Load Data and Slot Data
from distanceMatrix import distanceMatrix
from antFunctions import nextHub, path, detailPath, routeEntry, updateRoute
import pickle
from copy import deepcopy
from datetime import timedelta
import csv
from math import exp, fabs, ceil

# distanceMatrix('BHI6.csv', {'lat': 19.237481, 'lng': 73.034974}) # Bhiwandi
# distanceMatrix('KOL6.csv', {'lat': 22.739977, 'lng': 88.317647}) #Kolkata
# distanceMatrix('KUD_7.csv', {'lat': 12.8852659, 'lng': 77.6533668}) #Kudlu
# distanceMatrix('MAN_9.csv', {'lat': 28.714921, 'lng': 77.315002}) #Mandoli
# distanceMatrix('CHV_10.csv', {'lat': 19.110976, 'lng': 72.893396}) #Chandivali

trackingID = pickle.load(open('trackingID.p', 'rb'))
LatLngData = pickle.load(open('LatLngData.p', 'rb'))
timeMatrix = pickle.load(open('timeMatrix.p', 'rb'))
slotData = pickle.load(open('slotData.p', 'rb'))
loadData = pickle.load(open('loadData.p', 'rb'))
addressDetail = pickle.load(open('addressDetail.p', 'rb'))

# Introducing Sink
trackingID.append('Sink')
timeMatrix['Sink'] = timeMatrix['Hub']
for i in trackingID[:-1]:
    timeMatrix[i]['Sink'] = timeMatrix[i]['Hub']

# Taking the Average Time
avg = 0
for i in trackingID[:-1]:
    for j in trackingID[1:]:
        if timeMatrix[i][j] > 2:
            avg += 2
        else:
            avg += timeMatrix[i][j]
avg /= len(trackingID) * len(trackingID)
# Putting Cut Off Time Matrix
for i in trackingID[:-1]:
    for j in trackingID[1:]:
        if 2 < timeMatrix[i][j] <= 2.5:
            timeMatrix[i][j] = 2
        elif timeMatrix[i][j] > 2.5:
            timeMatrix[i][j] = 1 + avg
# ----------------------------------------------------------------------------------------------------------------------

# Global Variable

# Business Constraints
deliveryTime = 0.25  # Delivery Time in Hours
Q = [130, 130] # Capacity Limit
T = 7.5  # Travel Time Limit
saLimit = 0.85  # Slot Adherence Limit
maxOrders = 100

# Algorithm Parameters
alpha = 1  # Transition Matrix Parameter - power of Pheromone
beta = 3  # Transition Matrix Parameter - power of Cost
lamda = 2000  # Slot Adherence Factor
saImp = 1 # 0 for without Slot Adherence Importance
q = 100  # Pheromone Calculation Parameter
rho = 0.1  # Evaporation Constant
maxIT = 2000  # Maximum Iteration
# bestNoOfAnts = len(Q)-1 + ceil((sum(loadData.values()) - sum(Q[:-1]))/(Q[len(Q)-1]-10)) + 4 # Same as No of Vans
bestNoOfAnts = 7
# ----------------------------------------------------------------------------------------------------------------------
# Creation of feasible Matrix
confusionMatrix = {}
for s in trackingID[:-1]:
    confusionMatrix[s] = {}
    for d in trackingID[1:]:
        confusionMatrix[s][d] = None

for source in trackingID[1:-1]:
    for destination in trackingID[1:-1]:
        t_sd = timeMatrix[source][destination]
        # Source Slot Start Time and End Time
        sStartTime = float(slotData[source]['start'].time().hour)
        sEndTime = float(slotData[source]['end'].time().hour)
        # Destination Slot Start Time and End Time
        dStartTime = float(slotData[destination]['start'].time().hour)
        dEndTime = float(slotData[destination]['end'].time().hour)

        if (dStartTime <= sStartTime + t_sd + deliveryTime <= dEndTime or
                        dStartTime <= sEndTime + t_sd + deliveryTime <= dEndTime):
            confusionMatrix[source][destination] = 1
        else:
            confusionMatrix[source][destination] = 0
for i in trackingID[1:-1]:
    confusionMatrix[i][i] = 0
# Creation of Pheromone Matrix, putting a constant Pheromone over all the possible nodes
Tau = {}
for s in trackingID[:-1]:
    Tau[s] = {}
    for d in trackingID[1:]:
        if s != d:
            if confusionMatrix[s][d] == 0:
                Tau[s][d] = 0
            else:
                Tau[s][d] = 50
        else:
            Tau[s][d] = 0
# Shouldn't travel directly Hub to Sink
Tau['Hub']['Sink'] = 0

# Creation of Transition Matrix
transitionMatrix = {}
for s in trackingID[:-1]:
    transitionMatrix[s] = {}
    for d in trackingID[1:]:
        try:
            transitionMatrix[s][d] = ((Tau[s][d]) ** alpha) * ((1 / (timeMatrix[s][d] + 1 / 60)) ** beta) / \
                                     sum(((Tau[s][h]) ** alpha) * ((1 / (timeMatrix[s][h] + 1 / 60)) ** beta) for h in
                                         trackingID[1:])
        except ZeroDivisionError:
            transitionMatrix[s][d] = 0

# ----------------------------------------------------------------------------------------------------------------------
# Iteration Parameters
cost = [['Iteration Number', 'Travel Time']]
bestCost = 9999
bestCostOnly = 9999
bestSlotAdherence = 0

# Start of Iteration
for iteration in range(maxIT):
    # Slot Adherence Dictionary
    slotAdherence = {}
    for i in trackingID:
        slotAdherence[i] = 0

    nodeList = []
    print("Iteration Number " + str(iteration))
    # Creation of Decision Matrix
    decisionMatrix = {}
    ant = 0
    while len(nodeList) != len(trackingID) - 2:
        # Defining the Decision Matrix for current Ant
        decisionMatrix[ant] = {}
        for i in trackingID[:-1]:
            decisionMatrix[ant][i] = {}
            for j in trackingID[1:]:
                decisionMatrix[ant][i][j] = 0
        lastNode = 'Hub'
        while lastNode != 'Sink':
            # Current Travel time Excluding Return Time
            TT = sum(decisionMatrix[ant][i][j] * timeMatrix[i][j] for i in trackingID[:-1] for j in trackingID[1:]) + \
                 sum(decisionMatrix[ant][i][j] for i in trackingID[:-1] for j in trackingID[1:]) * deliveryTime
            # Total Capacity
            capacity = sum(
                sum(decisionMatrix[ant][i][j] for j in trackingID[1:]) * loadData[i] for i in trackingID[1:-1])
            # No of Orders
            noOfOrders = sum(decisionMatrix[ant][i][j] for i in trackingID[:-1] for j in trackingID[1:])
            # Time Travel Constraints and Capacity Constraints
            if TT > T or capacity > Q[min(ant,(len(Q) - 1))] or noOfOrders > maxOrders:
                # print('TT ' + str(TT) + ' and Capacity ' + str(capacity))
                nextNode = 'Sink'
            else:
                nextNode = nextHub(transitionMatrix[lastNode], nodeList)
            # Slot Adherence Check
            if lastNode == 'Hub':
                endTime = slotData[nextNode]['start'] + timedelta(hours=deliveryTime)
            else:
                endTime = endTime + timedelta(hours=timeMatrix[lastNode][nextNode] + deliveryTime)
            if nextNode != 'Sink' and slotData[nextNode]['start'].hour <= endTime.hour <= slotData[nextNode]['end'].hour:
                slotAdherence[nextNode] = 1

            if nextNode != 'Sink':
                nodeList.append(nextNode)
            # Update the Decision Matrix
            decisionMatrix[ant][lastNode][nextNode] = 1
            # Replace the Last node with Next Node
            lastNode = deepcopy(nextNode)
            # End of While Loop for current Ant
        ant += 1
        # End of While Loop all nodes are visited
    noOfAnts = len(decisionMatrix)
    # Update the Pheromone Matrix
    for s in trackingID[:-1]:
        for d in trackingID[1:]:
            L_k = 0
            for k in range(noOfAnts):
                if decisionMatrix[k][s][d] != 0:
                    L_k = sum(decisionMatrix[k][l][m] * timeMatrix[l][m] for l in trackingID[:-1] for m in trackingID[1:])
                    noOfDels = sum(decisionMatrix[k][l][m] for l in trackingID[:-1] for m in trackingID[1:]) - 1
                    slotAdheredOrder = 0
                    for y in trackingID[1:-1]:
                        if sum(decisionMatrix[k][x][y] for x in trackingID[:-1]) == 1 and slotAdherence[y] == 1:
                            slotAdheredOrder += 1
                    break
            if L_k == 0:
                delta_Tau = 0
            elif saLimit - 0.02 <= slotAdheredOrder / noOfDels <= saLimit + 0.4:
                delta_Tau = q / L_k + lamda / exp(fabs(saLimit - slotAdheredOrder / noOfDels))
            else:
                delta_Tau = q / L_k
            Tau[s][d] = (1 - rho) * Tau[s][d] + rho * delta_Tau * ( 1 + saImp * slotAdherence[d])

    # Update the Transition Matrix
    for s in trackingID[:-1]:
        for d in trackingID[1:]:
            transitionMatrix[s][d] = ((Tau[s][d]) ** alpha) * ((1 / (timeMatrix[s][d] + 1 / 60)) ** beta) / \
                                     sum(((Tau[s][h]) ** alpha) * ((1 / (timeMatrix[s][h] + 1 / 60)) ** beta) for h in
                                         trackingID[1:])

    currentCost = sum(decisionMatrix[k][i][j] * timeMatrix[i][j] for k in range(noOfAnts) for i in trackingID[: -1]
                      for j in trackingID[1:]) + sum(decisionMatrix[k][i][j] for k in range(noOfAnts) \
                                                     for i in trackingID[: -1] for j in trackingID[1:]) * deliveryTime
    cost.append([iteration, currentCost])
    if currentCost < bestCost and slotAdheredOrder / noOfDels > bestSlotAdherence and noOfAnts <= bestNoOfAnts:
        bestDecisionMatrix = deepcopy(decisionMatrix)
        bestCost = deepcopy(currentCost)
        bestSlotAdherence = slotAdheredOrder / noOfDels
        bestNoOfAnts = noOfAnts
    if currentCost < bestCostOnly and noOfAnts <= bestNoOfAnts:
        bestDecisionMatrixOnly = deepcopy(decisionMatrix)
        bestCostOnly = deepcopy(currentCost)

# End of Iteration
# ----------------------------------------------------------------------------------------------------------------------
# Cost Trend
csv.register_dialect('customDialect', delimiter=',', quotechar='"', doublequote=True, skipinitialspace=True,
                     lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
with open('Cost Trend.csv', 'w') as costTrend:
    dataWriter = csv.writer(costTrend, dialect='customDialect')
    for row in cost:
        dataWriter.writerow(row)

# Finding the Route String
route = path(decisionMatrix)
# Update the Route
route = updateRoute(route,timeMatrix, slotData, deliveryTime)
# No of Nodes Visited
uniqueNodes = routeEntry(route)
print("No of Nodes Visited " + str(len(uniqueNodes) - 2))
detailPath = detailPath(route, LatLngData, slotData, timeMatrix, loadData, deliveryTime, addressDetail, 'Last Output')

# Best Case Scenario
try:
    bestRoute = path(bestDecisionMatrix)
    # Update the Route
    bestRoute = updateRoute(bestRoute, timeMatrix, slotData, deliveryTime)
    from antFunctions import detailPath
    detailPath = detailPath(bestRoute, LatLngData, slotData, timeMatrix, loadData, deliveryTime, addressDetail, 'Optimized Output')
except NameError:
    print('Best Decision Matrix is not Defined')

# Best Cost Only Scenario
try:
    bestRouteOnly = path(bestDecisionMatrixOnly)
    # Update the Route
    bestRouteOnly = updateRoute(bestRouteOnly, timeMatrix, slotData, deliveryTime)
    from antFunctions import detailPath
    detailPath = detailPath(bestRouteOnly, LatLngData, slotData, timeMatrix, loadData, deliveryTime, addressDetail, 'Best Cost Output')
except NameError:
    print('Best Decision Matrix is not Defined')
