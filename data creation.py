import os
import pandas
from datetime import datetime
# Data Import
roData = pandas.read_csv('CHV_11_22.csv')
# OFD Dates
OFD = roData['ofd_date'].unique()
for dt in OFD:
    tempData = roData[roData['ofd_date'] == dt]
    newpath = r'.\Results\CHV\CHV_' + dt
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    tempData['slot_start_dt'][pandas.isnull(tempData['slot_start_dt'])] = min([datetime.strptime(x, '%d-%m-%Y %H.%M') for x in tempData['slot_start_dt'][pandas.notnull(tempData['slot_start_dt'])]]).strftime('%d-%m-%Y %H.%M')
    tempData['slot_end_dt'][pandas.isnull(tempData['slot_end_dt'])] = min([datetime.strptime(x, '%d-%m-%Y %H.%M') for x in tempData['slot_end_dt'][pandas.notnull(tempData['slot_end_dt'])]]).strftime('%d-%m-%Y %H.%M')
    tempData.to_csv(newpath + '\CHV_' + dt + '.csv', index = False)
