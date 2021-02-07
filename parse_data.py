from datetime import date, datetime
from dateutil import tz
import os
import csv

START_DATE = date(2021, 1, 15)
END_DATE = date(2021, 2, 4)
DATA_PATH = 'data/020521'

all_data = {}

for filename in os.listdir(DATA_PATH):
  dataType = filename.strip().split('.')[0]

  f = open(DATA_PATH + '/' + filename, 'r')
  print ('BEGIN: ' + filename)
  csvReader = csv.DictReader(f)

  for row in csvReader:
    dataDate = datetime.strptime(row['startDate'].strip(), "%Y-%m-%d %H:%M:%S %z").astimezone(tz.tzlocal()).date()
    if dataDate < START_DATE or dataDate > END_DATE:
      continue
    dataVal = eval(row['value'].strip())

    if dataDate not in all_data:
      all_data[dataDate] = {}
    if dataType not in all_data[dataDate]:
      all_data[dataDate][dataType] = 0.0
    all_data[dataDate][dataType] += dataVal

  print ('END: ' + filename)
  f.close()
  
