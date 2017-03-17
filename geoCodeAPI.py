def googleGeoCode(addr1, addr2, pincode, city, state):
    import requests, json, re
    from requests.utils import quote
    googleAPI = 'https://maps.googleapis.com/maps/api/geocode/json?address='
    key = 'AIzaSyDB5Lsnc9JpnyQSclQDvWObKQtyHrBhS5I'

    addr1 = quote(str(addr1), safe='')
    pincode = quote(str(pincode), safe='')
    city = quote(str(city), safe='')
    state = quote(str(state), safe='')

    if addr2 != '':
        addr2 = quote(str(addr2), safe='')
        url = googleAPI + addr1 + addr2 + city + state + pincode + "&key=" + key
        url = re.sub(r'#', r'', url)
    else:
        url = googleAPI + addr1 + addr2 + city + state + pincode + "&key=" + key
        url = re.sub(r'#', r'', url)

    resp = requests.get(url)
    if len(json.loads(resp.text)['results'])==0:
        return  "error finding locations"
    else:
        return json.loads(resp.text)['results'][0]['geometry']['location']

def pincodeCentre(pincode):
    import requests, json, re
    from requests.utils import quote
    # Default Parameters
    key = "0e41de65-d2c5-4ebd-9cfb-a552dae27f3e"
    header = {'referer': 'http://large-analytics.flipkart.com/'}

    url = "http://10.85.50.71/pincode-info?key=" + key + "&pincode=" + str(pincode) + "&doctypes=Pincode_region"
    resp = requests.get(url, headers=header, timeout=None)
    northEast = resp.json()['pincode_info']['Pincode_region']['bounding_box']['northeast']
    southWest = resp.json()['pincode_info']['Pincode_region']['bounding_box']['southwest']
    point = {'lat': (northEast['lat'] + southWest['lat']) / 2, 'lng': (northEast['lng'] + southWest['lng']) / 2}

    return point

def latLngValidation(point,pincode):
    import requests, json, re
    from requests.utils import quote
    # Reverse geocode to get the pincode
    resp = requests.get('http://10.85.53.150/reverse_geocode?point=' + str(point['lat']) + "," + str(point['lng']))
    for item in json.loads(resp.text)['results'][0]['address_components']:
        if item['DOCTYPE'] == 'Pincode_region':
            pincodeName = item['NAME']

    # Getting the neighbourhood of the user given pincode
    resp = requests.get('http://10.85.53.150/get_pincode_neighbourhood?pincode=' + str(pincode))
    pincodeNeighbour = [str(pincodes['NAME']) for pincodes in json.loads(resp.text)['pincode_info']['Pincode_region']['docs']]

    if pincodeName in pincodeNeighbour:
        return True
    else:
        False

def point(addr1, addr2, pincode, city, state):
    import requests, json, re
    from requests.utils import quote
    from geoCodeAPI import googleGeoCode, pincodeCentre, latLngValidation
    # Default Parameters
    key = "0e41de65-d2c5-4ebd-9cfb-a552dae27f3e"
    header = {'referer': 'http://large-analytics.flipkart.com/'}

    # geoCodeAPI = "https://maps.flipkart.com/geocode?"
    # geoCodeAPI = "https://maps.flipkart.com/geocode?"
    geoCodeAPI = "http://10.85.50.71/geocode?"

    addr1 = quote(str(addr1), safe='')
    pincode = quote(str(pincode), safe='')
    city = quote(str(city), safe='')
    state = quote(str(state), safe='')

    if addr2 != '':
        addr2 = quote(str(addr2), safe='')
        url1 = geoCodeAPI + \
               "addr1=" + addr1 + "&addr2=" + addr2 + \
               "&city=" + city + "&state=" + state + "&pincode=" + \
               pincode + "&key=" + key
        url1 = re.sub(r'#', r'', url1)
    else:
        url1 = geoCodeAPI + \
               "addr1=" + addr1 + "&city=" + city + \
               "&state=" + state + "&pincode=" + pincode + \
               "&key=" + key
        url1 = re.sub(r'#', r'', url1)
    # print(url1)
    resp = requests.get(url1, headers=header, timeout=None)
    if resp.json().get('status') is not None:
        point = json.loads(resp.text)['results'][0]['geometry']['location']
        if latLngValidation(point, pincode):
            return point
        else:
            point = googleGeoCode(addr1, addr2, pincode, city, state)
            if latLngValidation(point, pincode):
                return point
            else:
                return pincodeCentre(pincode)
    else:
        return pincodeCentre(pincode)

def distance(point1, point2):
    global time
    from copy import deepcopy
    import requests, json
    point1 = deepcopy(point1)
    point2 = deepcopy(point2)
    requests.adapters.DEFAULT_RETRIES = 30
    key = "0e41de65-d2c5-4ebd-9cfb-a552dae27f3e"
    header = {'referer': 'http://large-analytics.flipkart.com/'}
    url2 = 'http://10.85.50.71/directions?point=' + \
           str(point1['lat']) + ',' + str(point1['lng']) + \
           '&point=' + str(point2['lat']) + ',' + str(point2['lng']) + \
           "&key=" + key
    # print(url2)
    try:
        resp = requests.get(url2, headers=header, timeout=None)
        if resp.json()['info'].get('errors') is None:
            time = float(json.loads(resp.text)['paths'][0]['time']) / 3600000
    except:
        notFound = True
        counter = 0
        while notFound:
            point1['lat'] *= (0.999 ** (1 - (counter % 2))) * (1.001 ** (counter % 2))
            point1['lng'] *= (0.999 ** (1 - (counter % 2))) * (1.001 ** (counter % 2))

            point2['lat'] *= (0.999 ** (1 - (counter % 2))) * (1.001 ** (counter % 2))
            point1['lng'] *= (0.999 ** (1 - (counter % 2))) * (1.001 ** (counter % 2))
            url2 = 'http://10.85.50.71/directions?point=' + \
                   str(point1['lat']) + ',' + str(point1['lng']) + \
                   '&point=' + str(point2['lat']) + ',' + str(point2['lng']) + \
                   "&key=" + key
            resp = requests.get(url2, headers=header, timeout=None)
            if resp.json()['info'].get('errors') is None:
                notFound = False
                time = float(json.loads(resp.text)['paths'][0]['time']) / 3600000
            else:
                counter += 1
            if counter > 1000:
                break
    return time
