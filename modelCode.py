# Calculation of Time Matrix, Load Data and Slot Data
# from distanceMatrix import distanceMatrix
from path import path
from pulp import *
import pickle


# distanceMatrix('BHI_05_04_2016.csv', {'lat': 19.237481, 'lng': 73.034974})

trackingID = pickle.load(open('trackingID.p', 'rb'))
trackingID.append('Sink')
timeMatrix = pickle.load(open('timeMatrix.p', 'rb'))
slotData = pickle.load(open('slotData.p', 'rb'))
loadData = pickle.load(open('loadData.p', 'rb'))

# Putting Cut Off Time Matrix
timeMatrix['Sink'] = timeMatrix['Hub']
for i in trackingID[ :-1]:
    timeMatrix[i]['Sink'] = timeMatrix[i]['Hub']

for i in trackingID[ :-1]:
    for j in trackingID[1: ]:
        if timeMatrix[i][j] > 2:
            timeMatrix[i][j] = 2
# --------------------------------------------------------------------------------------------------
# Assigning the Problem
prob = LpProblem("RouteOptimization", LpMinimize)
noOfVan = 8
deliveryTime = 0.25

# Creation of feasible Matrix
confusionMatrix = {}
for s in trackingID:
    confusionMatrix[s] = {}
    for d in trackingID:
        confusionMatrix[s][d] = None

for source in trackingID[1:-1]:
    for destination in trackingID[1:-1]:
        if ((float(slotData[destination]['start'].time().hour) <= float(slotData[source]['end'].time().hour) + timeMatrix[source][destination] + deliveryTime <= float(slotData[destination]['end'].time().hour)) or
            (float(slotData[destination]['start'].time().hour) <= float(slotData[source]['start'].time().hour) + timeMatrix[source][destination] + deliveryTime <= float(slotData[destination]['end'].time().hour))):
            confusionMatrix[source][destination] = 1
        else:
            confusionMatrix[source][destination] = 0
for i in trackingID:
    confusionMatrix[i][i] = 0
# --------------------------------------------------------------------------------------------------
# Decision Variable - Edge Variables
X = LpVariable.dicts("X", [(i, j, k)
                           for i in trackingID[:-1]
                           for j in trackingID[1:]
                           for k in range(noOfVan)], 0, 1, LpBinary)


# Sequence Number in which city i visited
U = LpVariable.dicts("U", [(i, k) for i in trackingID[:-1] for k in range(noOfVan)],
                     lowBound = 0, upBound = 20,cat = LpInteger)

# --------------------------------------------------------------------------------------------------
# Objective
prob += lpSum(timeMatrix[i][j] * X[(i, j, k)] for i in trackingID[:-1] for j in trackingID[1:] for k in range(noOfVan)) + \
        (len(trackingID)-1)*deliveryTime

# CONSTRAINTS
# --------------------------------------------------------------------------------------------------
# Based on confusion matrix force fitting the decision variables this will ensures the Slot Adherence as well
for i in trackingID[:-1]:
    for j in trackingID[1:]:
        if confusionMatrix[i][j] == 0:
            for k in range(noOfVan):
                prob += X[i, j, k] == 0

# Each vehicle will leave the depot and arrive at a determined customer
for k in range(noOfVan):
    # All the Route should start from the Hub
    prob += lpSum(X[('Hub', j, k)] for j in trackingID[1:]) == 1
    # All the Route should end at Sink
    prob += lpSum(X[(i, 'Sink', k)] for i in trackingID[:-1]) == 1
    # Removing Hub to direct Sink Connection
    prob += X['Hub','Sink',k] == 0

# Entrance and Exit flows, guarantees that each vehicle will leave a determined customer and arrive back to the depot
for p in trackingID[1:-1]:
    for k in range(noOfVan):
        prob += lpSum(X[i, p, k] for i in trackingID[:-1]) - lpSum(X[p, j, k] for j in trackingID[1:]) == 0

# Exactly one Van can approach to a delivery location and leaves the Delivery Location after service
for i in trackingID[1:-1]:
    for k in range(noOfVan):
        prob += X[(i, i, k)] == 0

for j in trackingID[1:-1]:
    prob += lpSum(X[(i, j, k)] for i in trackingID[:-1] for k in range(noOfVan)) == 1

for i in trackingID[1:-1]:
    prob += lpSum(X[(i, j, k)] for j in trackingID[1:] for k in range(noOfVan)) == 1

# Capacity Constraints
for k in range(noOfVan):
    prob += lpSum(lpSum(X[(i, j, k)] for j in trackingID[1:]) * loadData[i] for i in trackingID[1:-1]) <= 135
    # prob += lpSum(lpSum(X[(i, j, k)] for j in trackingID[1:]) * loadData[i] for i in trackingID[1:-1]) >= 120

# Total Travel Time Constraints
for k in range(noOfVan):
    prob += lpSum(X[i, j, k] * timeMatrix[i][j] for i in trackingID[ :-1] for j in trackingID[1:]) +\
            lpSum(X[i, j, k] for i in trackingID[ :-1] for j in trackingID[1:]) * deliveryTime <= 8

# Sub-Tour Initial Constraints
for k in range(noOfVan):
    prob += U['Hub',k] == 1

for i in trackingID[1:-1]:
    for k in range(noOfVan):
        prob += U[i,k] >= 2

# Sub-Tour Elimination
for i in trackingID[:-1]:
    for j in trackingID[1:-1]:
        if i != j:
            for k in range(noOfVan):
                if confusionMatrix[i][j] == 1:
                    prob += U[i, k] - U[j, k] + (len(trackingID)-2) * X[i,j,k] <= (len(trackingID)-3)

# --------------------------------------------------------------------------------------------------
# Solving
status = prob.solve()
print("Status:", LpStatus[status])

# The optimised objective function value is printed to the screen
print("Total Travel Time = ", value(prob.objective))

# --------------------------------------------------------------------------------------------------
# Post Processing
if LpStatus[status] == 'Optimal':
    decisionMatrix = {}
    for k in range(noOfVan):
        decisionMatrix[k] = {}
        for i in trackingID[:-1]:
            decisionMatrix[k][i] = {}
            for j in trackingID[1:]:
                if X[i, j, k].value() != 0:
                    decisionMatrix[k][i][j] = 1
                else:
                    decisionMatrix[k][i][j] = 0

    route = path(decisionMatrix)
for i in trackingID[:-1]:
    print("\n")
    for j in trackingID[1:]:
        print(decisionMatrix[0][i][j],end=" ")
