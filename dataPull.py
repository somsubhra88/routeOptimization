import pypyodbc
import pandas
from pandasql import sqldf
from pandas import merge
from datetime import datetime, timedelta
import urllib

def isNaN(x):
    return str(x).lower() == 'nan'

ekl_facilities='23'
start_date = (datetime.now() - timedelta(days = 15)).strftime('%Y-%m-%d')
end_date=(datetime.now() - timedelta(days = 14)).strftime('%Y-%m-%d')
targetURL = "https://raw.githubusercontent.com/somsubhra88/routeOptimization/master/sql%20codes/"
####################################################################################################################################################
# Tracking ID
print("Pulling the tracking IDs")
# Using pypyodbc driver creating hive connection
connection = pypyodbc.connect(driver = '{MySQL ODBC 5.2a Driver}', server = '10.85.156.146', uid = 'analytics_user', pwd = 'WER56DF3',  database = 'fklogistics')

# Opening a cursor
cur = connection.cursor()

# Reading query String from the file
query = urllib.request.urlopen(targetURL + "trackingID.txt").read()

print("Fetching data")

# Running the Query from Hive
trackingID = pandas.DataFrame(cur.execute(query,[ekl_facilities, ekl_facilities, start_date, end_date]).fetchall())
trackingID.columns = [hdrs[0] for hdrs in cur.description ]
trackingID_list = ','.join('\'' + x + '\'' for x in trackingID['tracking_id'])
print("End of Tracking ID pull")
####################################################################################################################################################
# Address
print("Address Data Pull")
# Opening a cursor
cur = connection.cursor()

# Reading query String from the file
query = urllib.request.urlopen(targetURL + "address.txt").read().decode()

# Running the Query from Hive
address = pandas.DataFrame(cur.execute(query.replace('?',trackingID_list).encode('utf-8')).fetchall())

# Headers
address.columns = [hdrs[0] for hdrs in cur.description ]
print("Address Data Pull Finished")

####################################################################################################################################################
# Shipments - B2B
print("Pulling Shipments from B2B")
connection = pypyodbc.connect(DSN="flo_warehouse_b2b", autocommit=True)

# Opening a cursor
cur = connection.cursor()

# Reading query String from the file
query = urllib.request.urlopen(targetURL + "shipment_b2b.txt").read().decode()

# Running the Query from Hive
shipment_b2b = pandas.DataFrame(cur.execute(query.replace('?',trackingID_list).encode('utf-8')).fetchall())
shipment_b2b.columns = [hdrs[0] for hdrs in cur.description ]

# Shipments - B2C
print("Pulling Undels")
connection = pypyodbc.connect(DSN="flo_warehouse_b2c", autocommit=True)

# Opening a cursor
cur = connection.cursor()

# Reading query String from the file
query = urllib.request.urlopen(targetURL + "shipment_b2c.txt").read().decode()

headers = ['merchant_ref_id', 'tracking_id', 'courier_name', 'shipment_company']
# Running the Query from Hive
shipment_b2c = pandas.DataFrame(cur.execute(query.replace('?',trackingID_list).encode('utf-8')).fetchall(), columns = headers)

# Concatenate B2B and B2C
shipment = pandas.concat([shipment_b2b, shipment_b2c], axis = 0, ignore_index = True)

mer_ref_id_list = ','.join('\'' + x + '\'' for x in shipment['merchant_ref_id'])
print("End of Shipments Data Pull")
####################################################################################################################################################
# Fulfillment
print("Fulfillment Data Pull")
connection = pypyodbc.connect(DSN="FF_flo_b2c", autocommit=True)

# Opening a cursor
cur = connection.cursor()

# Reading query String from the file

query = urllib.request.urlopen(targetURL + "fulfillment.txt").read().decode()

# Running the Query from Hive
fulfillment = pandas.DataFrame(cur.execute(query.replace('?',mer_ref_id_list).encode('utf-8')).fetchall())
# Headers
fulfillment.columns =  [hdrs[0] for hdrs in cur.description ]

# Fulfillment Data Manupulation
pysqldf = lambda q: sqldf(q, globals())

query = urllib.request.urlopen(targetURL + "fulfillment_1.txt").read().decode()
fulfillment_1 = pysqldf(query)
fulfillment_1.slot_ref_id = fulfillment_1.slot_ref_id.astype(str)

ship_add_id_list = ','.join('\'' + x + '\'' for x in fulfillment_1['shipping_address_id'])
slot_ref_id_list = ','.join('\'' + x + '\'' for x in fulfillment_1['slot_ref_id'] if x is not None)
product_id_list = ','.join('\'' + x + '\'' for x in fulfillment_1['product_id'])
print("Fulfillment Data Pull Finished")
####################################################################################################################################################
# Slot Data
print("Slot Data Pull")
connection = pypyodbc.connect(DSN="facilities", autocommit=True)

# Opening a cursor
cur = connection.cursor()

# Reading query String from the file
query = urllib.request.urlopen(targetURL + "slot.txt").read().decode()

# Running the Query from Hive
slot = pandas.DataFrame(cur.execute(query.replace('?',slot_ref_id_list).encode('utf-8')).fetchall())
# Headers
slot.columns = [hdrs[0] for hdrs in cur.description ]
slot.slot_ref_id = slot.slot_ref_id.astype(str)
# For Slots Reference id is null
#dummySlotData = pandas.DataFrame({'slot_id': [None],'slot_ref_id': [None],'facility_id': [None],'route_id': [None],'slot_start_dt': [min(slot['slot_end_dt'])],'slot_end_dt': [max(slot['slot_start_dt'])],'facility_name': [None],'route_code': [None]})
#slot_1 = pandas.concat([slot,dummySlotData],axis = 0, ignore_index = True)
print("Slot Data Pull Finished")
####################################################################################################################################################
# LBH
print("LBH Data Pull")
connection = pypyodbc.connect(DSN="flo_warehouse_b2b", autocommit=True)

# Opening a cursor
cur = connection.cursor()

# Reading query String from the file
query = urllib.request.urlopen(targetURL + "lbh.txt").read().decode()

# Running the Query from Hive
lbh = pandas.DataFrame(cur.execute(query.replace('?',product_id_list).encode('utf-8')).fetchall())
# Headers
lbh.columns = [hdrs[0] for hdrs in cur.description]
print("LBH Data Pull Finished")
####################################################################################################################################################

# Merging All the Data
# Reading query String from the file
print('Merging All the Data')
finalData = merge(merge(merge(merge(merge(trackingID,shipment, how = 'left'), fulfillment_1, how = 'left'), slot, how = 'left', on = 'slot_ref_id'), lbh, how = 'left'), address, how = 'left')
print("End of Merging Data")

finalData = finalData[finalData['merchant_ref_id'].apply(lambda x: not isNaN(x))]
finalData.to_csv('D:/SomSubhra/Route Optimization/route optimization data.csv', index = False)
