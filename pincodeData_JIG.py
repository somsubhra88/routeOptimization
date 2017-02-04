from geoCodeAPI import pincodePoint, distance
import pandas
pincode = pandas.read_csv('Beat_BLR.csv')
#pincode = pandas.concat([pandas.DataFrame({'Pin Code': [560105], 'Beat': ['Jigni Warehouse']}),pincode], axis =0, ignore_index = True)
#lat, lng = [12.783284], [77.6427423]
lat, lng = [], []

for p in pincode['Pin Code']:
    lat_lng = pincodePoint(str(p))
    lat.append(lat_lng['lat'])
    lng.append(lat_lng['lng'])

pincode['lat'] = lat
pincode['lng'] = lng

hubData = pandas.DataFrame({'Hub': ['Jigni', 'BulkHub_WFL', 'BulkHub_BLR', 'BulkHub_YWP'],
                  'Hub Type' : ['Warehouse', 'Bulk Hub', 'Bulk Hub', 'Bulk Hub'],
                  'lat' : [12.783284, 12.988738, 12.8852659, 13.034638],
                  'lng' : [77.6427423, 77.8174173, 77.6533668, 77.5801103]
                  })

distanceMatrix = {}
for s in hubData['Hub']:
    distanceMatrix[s] = {}
    for d in pincode['Pin Code']:
        source = {'lat': float(hubData[hubData['Hub'] == s]['lat']), 'lng': float(hubData[hubData['Hub'] == s]['lng'])}
        destination = {'lat': float(pincode[pincode['Pin Code'] == d]['lat']), 'lng': float(pincode[pincode['Pin Code'] == d]['lng'])}
        distanceMatrix[s][d] = distance(source, destination)
        
distanceMatrix = pandas.DataFrame.from_dict(distanceMatrix, orient='index').stack().reset_index()
distanceMatrix.columns = ['Hub','Pincode','Time']
distanceMatrix.reset_index(drop=True, inplace=True)
pincodeDistance = pandas.DataFrame.pivot_table(distanceMatrix, values = 'Time', index = 'Pincode', columns = 'Hub', aggfunc = sum)

pincodeDistance.to_csv('BLR_Pincode.csv', index = True)