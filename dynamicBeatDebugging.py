import pickle
import csv
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
    
#from pincodeMerging import pincodeMerge
import pandas
from pulp import lpSum, LpVariable, LpProblem, LpMinimize, LpBinary, LpStatus, value, CPLEX_CMD
from math import ceil
    # --------------------------------------------------------------------------------------------------

vanVolume = 125
pincodeList = list(set(pincodeList))
#pincodeMerge = pincodeMerge(pincodeList).pincodeMerge
pincode = 'Pincode Merging.csv'
pincodeMerge = {}
# Importing Pincode Merging data
with open(pincode,'r') as f:
    reader = csv.reader(f)
    pincodeMergeList = list(reader)

for i in range(len(pincodeMergeList[0][1:])):
    pincodeMerge[pincodeMergeList[0][i + 1]] = {}
    for j in range(len(pincodeMergeList[0][1:])):
        pincodeMerge[pincodeMergeList[0][i + 1]][pincodeMergeList[0][j + 1]] = pincodeMergeList[i + 1][j + 1]

for s in pincodeMergeList[0][1:]:
    for d in pincodeMergeList[0][1:]:
        if (pincodeMerge[s][d] is None or pincodeMerge[s][d] == ''):
            pincodeMerge[s][d] = 0
        

for s in pincodeMergeList[0][1:]:
    for d in pincodeMergeList[0][1:]:
        gate = 0
        if str(pincodeMerge[s][d]) == '1':
            gate = 1
        elif str(pincodeMerge[d][s]) == '1':
            gate = 1
        else:
            gate = 0
        pincodeMerge[s][d], pincodeMerge[d][s] = gate, gate                   

for m in pincodeList:
    pincodeMerge[m] = dict((k,pincodeMerge[m][k]) for k in pincodeList)

pincodeMerge = dict((k,pincodeMerge[k]) for k in pincodeList)

pincodeMergeDF = pandas.DataFrame.from_dict(pincodeMerge)
#noOfBeats = int(ceil(float(sum(load.values()))/vanVolume))
# noOfBeats = max(8,int(ceil(float(sum(load.values()))/vanVolume)))
#pincodeList = ['560085','560029','560062','560041','562125']
noOfBeats = 8
#for m in pincodeList:
#    pincodeMerge[m] = dict((k,pincodeMerge[m][k]) for k in pincodeList)
# --------------------------------------------------------------------------------------------------
# Assigning the problem
prob = LpProblem("LoadBalancing", LpMinimize)
# --------------------------------------------------------------------------------------------------
# Input Parameters for Constraints Optimization
# Parameter Determins how close the values of two beats are expected
b = 10.00
# Penalty values for Closeness Slack Variables
penaltyCloseness = 100
# Penalty value for excedding the volumetric capacity
penaltyVolume = 200
# Upper Limit of the volumetric capacity
U = 130
# --------------------------------------------------------------------------------------------------
# Descision Variables
# If i-th pincode belongs to j-th beat then x_ij = 1 else 0
X = LpVariable.dicts("X",[(i,j) for i in pincodeList for j in range(noOfBeats)], lowBound = 0, upBound = 1, cat = LpBinary)
#
Z = LpVariable.dicts("Z",[(i) for i in range(noOfBeats)], lowBound = 0, upBound = 1, cat = LpBinary)

# Slack variables for Cluster Closeness
S1 = LpVariable.dicts("S1",[(i,j) for i in range(noOfBeats) for j in [z for z in range(noOfBeats) if z != i]], lowBound = 0, cat = 'Continuous')
S2 = LpVariable.dicts("S2",[i for i in range(noOfBeats)], lowBound = 0, cat = 'Continuous')
# --------------------------------------------------------------------------------------------------
# Objective
prob += lpSum(penaltyCloseness * S1[(i,j)] for i in range(noOfBeats) for j in [z for z in range(noOfBeats) if z != i]) +\
             lpSum(penaltyVolume * S2[i] for i in range(noOfBeats)) \
                 + 1000 * lpSum(Z[c] for c in range(noOfBeats))
# --------------------------------------------------------------------------------------------------
# Constraints
# Constraints - 1: All the pincode Should be assigned to some beats
for i in pincodeList:
    prob += lpSum(X[(i,j)] for j in range(noOfBeats)) == 1

# Constraints - 2: Pincode should be merged as per the Pincode merging Rule
for i in pincodeList:
    for j in range(noOfBeats):
        coeff = len(pincodeList) - sum(pincodeMerge[i].values())
        prob += lpSum(pincodeMerge[i][k] * X[(k,j)]  for k in [z for z in pincodeList if z != i]) >= X[(i,j)]
        prob += lpSum((1 - pincodeMerge[i][k]) * (1 - X[(k,j)]) / coeff for k in [z for z in pincodeList if z != i]) >= X[(i,j)]

# Constraints - 3: Volume Constraints
for j in range(noOfBeats):
    prob += lpSum(load[i] * X[(i,j)] for i in pincodeList) - S2[j] <= U
#    prob += lpSum(load[i] * X[(i,j)] for i in pincodeList) <= 1.2 * U

# Constraints - 4: All the Beats Should be Used
for c1 in range(noOfBeats):
    for c2 in [z for z in range(noOfBeats) if z != c1]:
        prob += lpSum(load[i] * X[(i,c1)] for i in pincodeList) - lpSum(load[i] * X[(i,c2)] for i in pincodeList) - S1[(c1,c2)] <= b
    
# 
for c in range(noOfBeats):
    prob += Z[c] <= lpSum(X[(i,c)] for i in pincodeList)
    for i in pincodeList:
        prob += Z[c] >= X[(i,c)]

# --------------------------------------------------------------------------------------------------
# Solving
status = prob.solve(CPLEX_CMD(path = r'C:\x86_win32\cplex.exe'))
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
    beatAssignmentData = beatAssignmentData[beatAssignmentData['Load'] > 0]
    # Pivot table
    pandas.pivot_table(data = beatAssignmentData, values = 'Load', index='Beats', aggfunc=sum)