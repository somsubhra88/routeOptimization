class pincodeMerge:
    def __init__(self,pincodeList):
        from geoCodeAPI import pincodeCentre, distance
        import progressbar
        pincodeList = list(set(pincodeList))
        # Resolving Pincode Lat lng
        self.pincodeGeocode = {}
        print("Pincode Centre Lat-Lng")
        for p in pincodeList:
            while True:
                try:
                    self.pincodeGeocode[p] = pincodeCentre(p)
                except:
                    continue
                else:
                    break
        bar = progressbar.ProgressBar(maxval = len(pincodeList) ** 2, widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()
        barCounter = 0
        # Resolving Distance Matrix
        print("Distance Matrix")
        self.distanceMatrix = {}
        for s in pincodeList:
            self.distanceMatrix[s] = {}
            for d in pincodeList:
                barCounter += 1
                bar.update(barCounter)
                infLoopCounter = 0
                while True:
                    infLoopCounter += 1
                    if(infLoopCounter > 10):
                        break
                    else:
                        try:
                            self.distanceMatrix[s][d] = distance(self.pincodeGeocode[s], self.pincodeGeocode[d])
                        except:
                            continue
                        else:
                            break
        bar.finish()
        print('Pincode Distance Matrix Finished')
        # Picode Merging Sparse Matrix -
        # if the time taken from source pincode to destination pincode less than that of 1 hour then assign it to 1 else o
        self.pincodeMerge = {}
        for s in pincodeList:
            self.pincodeMerge[s] = {}
            for d in pincodeList:
                if self.distanceMatrix[s][d] <= 1:
                    self.pincodeMerge[s][d] = 1
                else:
                    self.pincodeMerge[s][d] = 0

        # Checking if a pincode is assigned to single beat
        for s in pincodeList:
            if sum(self.pincodeMerge[s].values()) <= 2:
                sortedDist = sorted(list(self.distanceMatrix[s].values()))
                # 75-th percentile of the distance as new cutoff
                cutOff = sortedDist[int(round(0.20 * len(sortedDist) + 0.5)) -1]
                for d in pincodeList:
                    if self.distanceMatrix[s][d] <= cutOff:
                        self.pincodeMerge[s][d] = 1
                    else:
                        self.pincodeMerge[s][d] = 0

        # Converting it to symetric Matrix
        for s in pincodeList:
            for d in pincodeList:
                gate = 0
                if self.pincodeMerge[s][d] == 1:
                    gate = 1
                elif self.pincodeMerge[d][s] == 1:
                    gate = 1
                else:
                    gate = 0
                self.pincodeMerge[s][d], self.pincodeMerge[d][s] = gate, gate
