from datetime import datetime
import numpy as np

import dataio
import params as par
from util import csvutil
from util import timeutil

def validate_params():
  if par.AggregatorParams.FILENAME_SUFFIX:
    assert par.AggregatorParams.FILENAME_SUFFIX[0] == '_'
    assert not par.AggregatorParams.FILENAME_SUFFIX[-1] == '_'

  assert par.AggregatorParams.END_DATE > par.AggregatorParams.START_DATE

def aggregate_data_by_period(daily_data_dict, period_start_date_fn = None):
  periodly_data_dict = {}
  for d in daily_data_dict:
    period_start_date = period_start_date_fn(d)
    if period_start_date not in periodly_data_dict:
      periodly_data_dict[period_start_date] = {}
    for r in daily_data_dict[d]:
      if r not in periodly_data_dict[period_start_date]:
        periodly_data_dict[period_start_date][r] = []
      periodly_data_dict[period_start_date][r].append(daily_data_dict[d][r])

  for p in periodly_data_dict:
    for r in periodly_data_dict[p]:
      periodly_avg = np.average(periodly_data_dict[p][r])
      periodly_data_dict[p][r] = round(periodly_avg, 2)
  
  return periodly_data_dict


def aggregate_data_by_week(daily_data_dict):
  start_time = datetime.now()

  weekly_data_dict = aggregate_data_by_period(
                          daily_data_dict,
                          period_start_date_fn = timeutil.CalendarUtil.get_week_start_date)
  
  print()
  print("Weekly aggregate built in {}".format(datetime.now() - start_time))

  return weekly_data_dict

def aggregate_data_by_month(daily_data_dict, period_start_date_fn = None):
  start_time = datetime.now()

  monthly_data_dict = aggregate_data_by_period(
                          daily_data_dict,
                          period_start_date_fn = timeutil.CalendarUtil.get_month_start_date)
  
  print()
  print("Monthly aggregate built in {}".format(datetime.now() - start_time))
  
  return monthly_data_dict


def aggregate_data():
  validate_params()

  start_time = datetime.now()
  
  dio = dataio.DataIO()
  in_csv_filename = "{tz}_{start}_{end}{suffix}.csv".format(
                        tz = par.AggregatorParams.PARSE_TIMEZONE.name,
                        start = par.AggregatorParams.START_DATE.strftime("%Y%m%d"),
                        end = par.AggregatorParams.END_DATE.strftime("%Y%m%d"),
                        suffix = par.AggregatorParams.FILENAME_SUFFIX)
  in_csv = dio.get_parsed_csv_filepath(in_csv_filename)

  daily_data_dict = csvutil.CsvIO.read_data_csv(in_csv)

  if par.AggregatorParams.MONTHLY_AGGREGATION:
    monthly_data_dict = aggregate_data_by_month(daily_data_dict)
    if par.AggregatorParams.WRITE_DATA:
      monthly_csv_filename = "{tz}_{start}_{end}{suffix}_MONTHLY.csv".format(
                                  tz = par.AggregatorParams.PARSE_TIMEZONE.name,
                                  start = par.AggregatorParams.START_DATE.strftime("%Y%m%d"),
                                  end = par.AggregatorParams.END_DATE.strftime("%Y%m%d"),
                                  suffix = par.AggregatorParams.FILENAME_SUFFIX)
      monthly_csv = dio.get_parsed_csv_filepath(monthly_csv_filename)
      csvutil.CsvIO.write_data_csv(monthly_csv, monthly_data_dict)
  
  if par.AggregatorParams.WEEKLY_AGGREGATION:
    weekly_data_dict = aggregate_data_by_week(daily_data_dict)
    if par.AggregatorParams.WRITE_DATA:
      weekly_csv_filename = "{tz}_{start}_{end}{suffix}_WEEKLY.csv".format(
                                  tz = par.AggregatorParams.PARSE_TIMEZONE.name,
                                  start = par.AggregatorParams.START_DATE.strftime("%Y%m%d"),
                                  end = par.AggregatorParams.END_DATE.strftime("%Y%m%d"),
                                  suffix = par.AggregatorParams.FILENAME_SUFFIX)
      weekly_csv = dio.get_parsed_csv_filepath(weekly_csv_filename)
      csvutil.CsvIO.write_data_csv(weekly_csv, weekly_data_dict)
    
  print()
  print("Aggregation done in {}".format(datetime.now() - start_time))

if __name__ == '__main__':
  aggregate_data()