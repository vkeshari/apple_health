from datetime import date
import os

START_DATE = date(2020, 1, 15)
END_DATE = date(2020, 1, 28)
DATA_PATH = 'data/020521'

all_data = {}

for filename in os.listdir(DATA_PATH):
  f = open(DATA_PATH + '/' + filename, 'r')
  lines = f.readlines()
  header = lines[0]
  data = lines[1:]

  dateCol = 0
  valueCol = 0

  print (filename)
  for i, heading in enumerate(header.strip().split(',')):
    if heading == 'startDate':
      dateCol = i
    if heading == 'value':
      valueCol = i

  assert dateCol > 0, "No dateCol found in " + filename
  assert valueCol > 0, "No valueCol found in " + filename
  
  f.close()
  
