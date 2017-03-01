import pickle
addressDetail = pickle.load(open('addressDetail.p', 'rb'))
trackingID = pickle.load(open('trackingID.p', 'rb'))
loadData = pickle.load(open('loadData.p', 'rb'))


# Dynamic Beat
pincodeList = []
for tID in trackingID[1:]:
    pincodeList.append(addressDetail[tID]['address_pincode'])
pincodeList = list(set(pincodeList))
load = {}
for i in pincodeList:
    load[i] = 0

for tID in [x for x in trackingID if x not in ['Hub']]:
    load[addressDetail[tID]['address_pincode']] += loadData[tID]
    
from pincodeMerging import pincodeMerge
import pandas
from pulp import lpSum, LpVariable, LpProblem, LpMinimize, LpBinary, LpStatus, value
from math import ceil
    # --------------------------------------------------------------------------------------------------

vanVolume = 125
pincodeList = list(set(pincodeList))
pincodeMerge = pincodeMerge(pincodeList).pincodeMerge
pincodeMergeDF = pandas.DataFrame.from_dict(pincodeMerge)
noOfBeats = 6
# noOfBeats = max(8,int(ceil(float(sum(load.values()))/vanVolume)))
# --------------------------------------------------------------------------------------------------
# Assigning the problem
prob = LpProblem("LoadBalancing", LpMinimize)
# --------------------------------------------------------------------------------------------------
# Descision Variables
# If i-th pincode belongs to j-th beat then x_ij = 1 else 0
X = LpVariable.dicts("X",[(i,j) for i in pincodeList for j in range(noOfBeats)], lowBound = 0, upBound = 1, cat = LpBinary)

# Dummy Descision Variable to counter Absolute difference
p = LpVariable.dicts("p",[i for i in range(noOfBeats)], lowBound = 0, cat = 'Continuous')
q = LpVariable.dicts("q",[j for j in range(noOfBeats)], lowBound = 0, cat = 'Continuous')
# --------------------------------------------------------------------------------------------------
# Objective
prob += lpSum(p[i] + q[i] for i in range(noOfBeats))
# --------------------------------------------------------------------------------------------------
# Constraints
meanLoad = float(sum(load.values()))/noOfBeats
# Constraints - 1: Absolute Value Balance
for j in range(noOfBeats):
    prob += lpSum(X[(i,j)] * load[i] for  i in pincodeList) - meanLoad == p[j] - q[j]

# Constraints - 2: All the pincode Should be assigned to some beats
for i in pincodeList:
    prob += lpSum(X[(i,j)] for j in range(noOfBeats)) == 1

# Constraints - 3: Pincode should be merged as per the Pincode merging Rule
for i in pincodeList:
    if load[i] < meanLoad:
        for j in range(noOfBeats):
            prob += lpSum(pincodeMerge[i][k] * X[(k,j)] for k in pincodeList) >= 2 * X[(i,j)]

# Constraints - 4: All the Beats Should be Used
for j in range(noOfBeats):
    prob += lpSum(X[(i,j)] for i in pincodeList) >= 1
    prob += lpSum(X[(i,j)] for i in pincodeList) <= len(pincodeList)

# --------------------------------------------------------------------------------------------------
# Solving
status = prob.solve()
print("Status:", LpStatus[status])

# The optimised objective function value is printed to the screen
print("Absolute Deviation = ", value(prob.objective))

if LpStatus[status] == 'Optimal':
    decisionMatrix = {}
    for j in range(noOfBeats):
        decisionMatrix['Beats - ' + str(j + 1)] = {}
        for i in pincodeList:
            decisionMatrix['Beats - ' + str(j + 1)][i] = X[i, j].value() * load[i]

import pandas
decisionMatrixDF = pandas.DataFrame.from_dict(decisionMatrix)
# Creating Final Output into a single Dataframe to export
beatAssignmentData = pandas.DataFrame({  'Beats': ['Beats - ' + str(st + 1) for st in range(noOfBeats) for x in pincodeList],
                                        'Pincode': pincodeList * noOfBeats,
                                        'Load': [decisionMatrix['Beats - ' + str(j + 1)][i] for j in range(noOfBeats) for i in pincodeList]})
# Pivot table
pandas.pivot_table(data = beatAssignmentData, values = 'Load', index='Beats', aggfunc=sum)