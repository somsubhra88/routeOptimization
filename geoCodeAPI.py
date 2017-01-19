def point(addr1, addr2, pincode, city, state):
    import requests, json, re
    from requests.utils import quote
    # Default Parameters
    key = "0e41de65-d2c5-4ebd-9cfb-a552dae27f3e"
    header = {'referer': 'http://large-analytics.flipkart.com/'}

    # geoCodeAPI = "https://maps.flipkart.com/geocode?"
    geoCodeAPI = "https://maps.flipkart.com/geocode?"

    addr1 = quote(str(addr1), safe='')
    pincode = quote(str(pincode), safe='')
    city = quote(str(city), safe='')
    state = quote(str(state), safe='')
    # "?key=" + key +
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
    else:
        print(url1)
        url1 = "https://maps.flipkart.com/pincode-info?key=" + \
               key + "&pincode=" + pincode + "&doctypes=Pincode_region"
        resp = requests.get(url1, headers=header, timeout=None)
        northEast = resp.json()['pincode_info']['Pincode_region']['bounding_box']['northeast']
        southWest = resp.json()['pincode_info']['Pincode_region']['bounding_box']['southwest']
        point = {'lat': (northEast['lat'] + southWest['lat']) / 2, 'lng': (northEast['lng'] + southWest['lng']) / 2}

    return point


def distance(point1, point2):
    global time
    from copy import deepcopy
    import requests, json
    point1 = deepcopy(point1)
    point2 = deepcopy(point2)
    requests.adapters.DEFAULT_RETRIES = 30
    key = "0e41de65-d2c5-4ebd-9cfb-a552dae27f3e"
    header = {'referer': 'http://large-analytics.flipkart.com/'}
    url2 = 'https://maps.flipkart.com/api/v1/directions?point=' + \
           str(point1['lat']) + ',' + str(point1['lng']) + \
           '&point=' + str(point2['lat']) + ',' + str(point2['lng']) + \
           "&key=" + key
    # print(url2)
    try:
        resp = requests.get(url2, headers=header, timeout=None)
        if resp.json()['info'].get('errors') is None:
            time = json.loads(resp.text)['paths'][0]['time'] / 3600000
    except:
        notFound = True
        counter = 0
        while notFound:
            point1['lat'] *= (0.999 ** (1 - (counter % 2))) * (1.001 ** (counter % 2))
            point1['lng'] *= (0.999 ** (1 - (counter % 2))) * (1.001 ** (counter % 2))

            point2['lat'] *= (0.999 ** (1 - (counter % 2))) * (1.001 ** (counter % 2))
            point1['lng'] *= (0.999 ** (1 - (counter % 2))) * (1.001 ** (counter % 2))
            url2 = 'https://maps.flipkart.com/api/v1/directions?point=' + \
                   str(point1['lat']) + ',' + str(point1['lng']) + \
                   '&point=' + str(point2['lat']) + ',' + str(point2['lng']) + \
                   "&key=" + key
            resp = requests.get(url2, headers=header, timeout=None)
            if resp.json()['info'].get('errors') is None:
                notFound = False
                time = json.loads(resp.text)['paths'][0]['time'] / 3600000
            else:
                counter += 1
            if counter > 1000:
                break
    return time
