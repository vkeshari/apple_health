from datetime import datetime
import numpy as np

import params as par
from util import csvutil, dataio, paramutil, timeutil

def aggregate_data_by_period(daily_data_dict, period):
  start_time = datetime.now()

  periodly_data_dict = {}
  for d in daily_data_dict:
    period_start_date = timeutil.CalendarUtil.get_period_start_date(d, period)
    if period_start_date not in periodly_data_dict:
      periodly_data_dict[period_start_date] = {}
    for r in daily_data_dict[d]:
      if r.name not in periodly_data_dict[period_start_date]:
        periodly_data_dict[period_start_date][r.name] = []
      periodly_data_dict[period_start_date][r.name].append(daily_data_dict[d][r])

  for p in periodly_data_dict:
    for r in periodly_data_dict[p]:
      periodly_avg = np.average(periodly_data_dict[p][r])
      periodly_data_dict[p][r] = round(periodly_avg, 2)
  
  print()
  print("{} aggregate built in {}".format(period.name.capitalize(), datetime.now() - start_time))
  
  return periodly_data_dict


def aggregate_data():
  paramutil.Validator.validate_aggregate_data()

  start_time = datetime.now()
  
  dio = dataio.DataIO(par.DataParams)
  in_csv = dio.get_csv_file()
  daily_data_dict = csvutil.CsvIO.read_data_csv(in_csv)

  for period in par.AggregatorParams.AGGREGATION_PERIODS:
    aggregated_data_dict = aggregate_data_by_period(daily_data_dict, period)
    if par.AggregatorParams.WRITE_DATA:
      aggregated_csv = dio.get_csv_file(period = period)
      csvutil.CsvIO.write_data_csv(aggregated_csv, aggregated_data_dict)
    
  print()
  print("Aggregation done in {}".format(datetime.now() - start_time))

if __name__ == '__main__':
  aggregate_data()