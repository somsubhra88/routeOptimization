def dynamicBeat(pincodeList, pincode, load, vanVolume):
    from pincodeMerging import pincodeMerge
    from pulp import lpSum, LpVariable, LpProblem, LpMinimize, LpBinary, LpStatus, value
    import csv
    from math import ceil
    # --------------------------------------------------------------------------------------------------
    pincodeList = list(set(pincodeList))
    noOfBeats = max(8, int(ceil(float(sum(load.values()))/vanVolume)))
    if pincode is not None:
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
                else:
                    pincodeMerge[s][d] = 1

        for s in pincodeMergeList[0][1:]:
            for d in pincodeMergeList[0][1:]:
                gate = 0
                if pincodeMerge[s][d] == 1:
                    gate = 1
                elif pincodeMerge[d][s] == 1:
                    gate = 1
                else:
                    gate = 0
                pincodeMerge[s][d], pincodeMerge[d][s] = gate, gate
    else:
        pincodeMerge = pincodeMerge(pincodeList).pincodeMerge

    print('Pincode Merging Sparse Matrix is defined')
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
    # --------------------------------------------------------------------------------------------------
    # Post Processing
    if LpStatus[status] == 'Optimal':
        decisionMatrix = {}
        for j in range(noOfBeats):
            decisionMatrix['Beats - ' + str(j + 1)] = {}
            for i in pincodeList:
                decisionMatrix['Beats - ' + str(j + 1)][i] = X[i, j].value()

    # Creating A beat file
    beatFile = [['Pin Code', 'Beat']]
    for b in list(decisionMatrix.keys()):
        for p in pincodeList:
            if decisionMatrix[b][p] == 1:
                beatFile.append([p,b])
    csv.register_dialect('customDialect',delimiter=',', quotechar='"', doublequote=True,skipinitialspace=True, lineterminator='\n',quoting=csv.QUOTE_MINIMAL)
    with open('Beat.csv','w') as beatPathCSV:
        dataWriter = csv.writer(beatPathCSV, dialect = 'customDialect')
        for row in beatFile:
            dataWriter.writerow(row)
