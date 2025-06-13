from csv import DictReader, DictWriter
from datetime import datetime

class CsvIO:

  _date_field_csv = 'date'

  @classmethod
  def read_data_csv(cls, in_csv):
    start_time = datetime.now()

    csv_data = []
    with open(in_csv, newline = '') as csv_file:
      reader = DictReader(csv_file, restval = 'NA', dialect = 'excel')

      for row in reader:
        csv_data.append(row)
    
    data_dict = {}
    for row in csv_data:
      d = row['date']
      data_dict[d] = {k: v for (k, v) in row.items() if not k == 'date'}
    
    print()
    print(in_csv)
    print("CSV read in {}".format(datetime.now() - start_time))
    
    return data_dict
  
  @classmethod
  def write_data_csv(cls, out_csv, data_dict):
    fields = set()
    for d in data_dict:
      fields = fields | data_dict[d].keys()

    start_time = datetime.now()

    fieldnames = [cls._date_field_csv] + sorted(fields)

    with open(out_csv, 'w', newline = '') as csv_file:
      writer = DictWriter(csv_file, fieldnames = fieldnames, restval = 'NA', dialect = 'excel')
      writer.writeheader()

      for d in sorted(data_dict.keys()):
        writer.writerow({cls._date_field_csv: str(d)} | data_dict[d])

    print()
    print(out_csv)
    print("CSV written in {}".format(datetime.now() - start_time))
