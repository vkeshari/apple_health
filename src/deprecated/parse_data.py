from datetime import date, datetime
from dateutil import tz
import os
import csv

START_DATE = date(2021, 1, 15)
END_DATE = date(2021, 2, 4)
READ_DATA_PATH = ''
WRITE_DATA_PATH = 'parsed_data'

all_data = {}
all_data_types = ['date']

for filename in sorted(os.listdir(READ_DATA_PATH)):
  dataType = filename.strip().split('.')[0]
  if dataType not in all_data_types:
    all_data_types.append(dataType)

  f = open(READ_DATA_PATH + '/' + filename, 'r')
  print ('BEGIN: ' + filename)
  csvReader = csv.DictReader(f)

  for row in csvReader:
    dataDate = datetime.strptime(row['startDate'].strip(), "%Y-%m-%d %H:%M:%S %z") \
                  .astimezone(tz.tzlocal()).date()
    if dataDate < START_DATE or dataDate > END_DATE:
      continue
    dataVal = eval(row['value'].strip())

    if dataDate not in all_data:
      all_data[dataDate] = {}
      all_data[dataDate]['date'] = dataDate.strftime("%Y%m%d")
    if dataType not in all_data[dataDate]:
      all_data[dataDate][dataType] = 0.0
    all_data[dataDate][dataType] += dataVal

  print ('END: ' + filename)
  f.close()
 
outFileName = WRITE_DATA_PATH + '/' \
                  + START_DATE.strftime("%Y%m%d") + '_' \
                  + END_DATE.strftime("%Y%m%d") + '.csv'
f = open(outFileName, 'w+')
print ('Writing to: ' + outFileName)
csvWriter = csv.DictWriter(f, fieldnames = all_data_types)

csvWriter.writeheader()
for d in all_data:
  csvWriter.writerow(all_data[d])

print ('DONE')
f.close()
