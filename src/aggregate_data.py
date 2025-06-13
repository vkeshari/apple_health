from datetime import datetime, date

import dataio
import params as par
from util import csvutil

def validate_params():
  pass

def aggregate_data_by_week(daily_data_dict):
  return None

def aggregate_data_by_month(daily_data_dict):
  return None


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
    monthly_data_dict = aggregate_data_by_week(daily_data_dict)
    monthly_csv_filename = "{tz}_{start}_{end}{suffix}_MONTHLY.csv".format(
                                tz = par.AggregatorParams.PARSE_TIMEZONE.name,
                                start = par.AggregatorParams.START_DATE.strftime("%Y%m%d"),
                                end = par.AggregatorParams.END_DATE.strftime("%Y%m%d"),
                                suffix = par.AggregatorParams.FILENAME_SUFFIX)
    monthly_csv = dio.get_parsed_csv_filepath(monthly_csv_filename)
    if par.AggregatorParams.WRITE_DATA:
      csvutil.CsvIO.write_data_csv(monthly_csv, monthly_data_dict)
  
  if par.AggregatorParams.WEEKLY_AGGREGATION:
    weekly_data_dict = aggregate_data_by_week(daily_data_dict)
    weekly_csv_filename = "{tz}_{start}_{end}{suffix}_WEEKLY.csv".format(
                                tz = par.AggregatorParams.PARSE_TIMEZONE.name,
                                start = par.AggregatorParams.START_DATE.strftime("%Y%m%d"),
                                end = par.AggregatorParams.END_DATE.strftime("%Y%m%d"),
                                suffix = par.AggregatorParams.FILENAME_SUFFIX)
    weekly_csv = dio.get_parsed_csv_filepath(weekly_csv_filename)
    if par.AggregatorParams.WRITE_DATA:
      csvutil.CsvIO.write_data_csv(weekly_csv, weekly_data_dict)
    
    print()
    print("Aggregation done in {}".format(datetime.now() - start_time))

if __name__ == '__main__':
  aggregate_data()