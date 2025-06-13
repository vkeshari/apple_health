from csv import DictReader, DictWriter
from datetime import datetime, date

import params as par

class CsvIO:

  _date_field_csv = 'date'
  _restval = 'NA'
  _csv_dialect = 'excel'

  @classmethod
  def read_data_csv(cls, in_csv):
    start_time = datetime.now()

    csv_data = []
    with open(in_csv, newline = '') as csv_file:
      reader = DictReader(csv_file, restval = cls._restval, dialect = cls._csv_dialect)

      for row in reader:
        csv_data.append(row)
    
    data_dict = {}
    for row in csv_data:
      d = date.fromisoformat(row['date'])
      data_dict[d] = {r: eval(v) for (r, v) in row.items() \
                                    if not r == 'date' and not v == cls._restval}
    
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
      writer = DictWriter(csv_file, fieldnames = fieldnames,
                          restval = cls._restval, dialect = cls._csv_dialect)
      writer.writeheader()

      for d in sorted(data_dict.keys()):
        writer.writerow({cls._date_field_csv: str(d)} | data_dict[d])

    print()
    print(out_csv)
    print("CSV written in {}".format(datetime.now() - start_time))


class XmlToCsv:

  _sum_type_records = set()
  for rt in par.RecordParams.RECORD_TYPES:
    if rt.aggregation == par.AggregateType.SUM:
      _sum_type_records.add(rt.record)

  @classmethod
  def xml_dict_to_csv_dict(cls, records_by_date):
    data_dict = {}
    for r in records_by_date:
      for d in records_by_date[r]:
        if d not in data_dict:
          data_dict[d] = {}
        data_dict[d][r] = records_by_date[r][d]
    
    # Record types that use a sum for aggregation must have 0s instead of missing values.
    for d in data_dict:
      for r in cls._sum_type_records:
        if r not in data_dict[d]:
          data_dict[d][r] = 0
    
    return data_dict
