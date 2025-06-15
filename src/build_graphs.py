import dataio
import params as par
from util import csvutil

def validate_params():
  if par.GraphParams.FILENAME_SUFFIX:
    assert par.GraphParams.FILENAME_SUFFIX[0] == '_'
    assert not par.GraphParams.FILENAME_SUFFIX[-1] == '_'

  assert par.GraphParams.DATA_END_DATE > par.GraphParams.DATA_START_DATE
  assert par.GraphParams.GRAPH_END_DATE > par.GraphParams.GRAPH_START_DATE

def get_records_by_aggregate_type():
  sum_type_records = set()
  order_type_records = set()

  for rt in par.RecordParams.RECORD_TYPES:
    if rt.aggregation == par.AggregateType.SUM:
      sum_type_records.add(rt.record)
    elif rt.aggregation == par.AggregateType.MEDIAN:
      order_type_records.add(rt.record)
    elif rt.aggregation == par.AggregateType.AVERAGE:
      order_type_records.add(rt.record)
  
  return sum_type_records, order_type_records

def get_records_units():
  record_units = {}

  for rt in par.RecordParams.RECORD_TYPES:
    record_units[rt.record] = rt.unit
  
  return record_units

def build_daily_graphs(daily_data_dict, sum_type_records, order_type_records, record_units):
  pass

def build_weekly_graphs(weekly_data_dict, sum_type_records, order_type_records, record_units):
  pass

def build_monthly_graphs(monthly_data_dict, sum_type_records, order_type_records, record_units):
  pass


def build_graphs():
  validate_params()

  sum_type_records, order_type_records = get_records_by_aggregate_type()
  record_units = get_records_units()

  dio = dataio.DataIO()
  if par.GraphParams.DAILY_GRAPHS:
    daily_csv_filename = "{tz}_{start}_{end}{suffix}.csv".format(
                              tz = par.GraphParams.PARSE_TIMEZONE.name,
                              start = par.GraphParams.DATA_START_DATE.strftime("%Y%m%d"),
                              end = par.GraphParams.DATA_END_DATE.strftime("%Y%m%d"),
                              suffix = par.GraphParams.FILENAME_SUFFIX)
    daily_csv = dio.get_parsed_csv_filepath(daily_csv_filename)
    daily_data_dict = csvutil.CsvIO.read_data_csv(daily_csv)
    build_daily_graphs(daily_data_dict, sum_type_records, order_type_records, record_units)
  if par.GraphParams.WEEKLY_GRAPHS:
    weekly_csv_filename = "{tz}_{start}_{end}{suffix}_WEEKLY.csv".format(
                              tz = par.GraphParams.PARSE_TIMEZONE.name,
                              start = par.GraphParams.DATA_START_DATE.strftime("%Y%m%d"),
                              end = par.GraphParams.DATA_END_DATE.strftime("%Y%m%d"),
                              suffix = par.GraphParams.FILENAME_SUFFIX)
    weekly_csv = dio.get_parsed_csv_filepath(weekly_csv_filename)
    weekly_data_dict = csvutil.CsvIO.read_data_csv(weekly_csv)
    build_weekly_graphs(weekly_data_dict, sum_type_records, order_type_records, record_units)
  if par.GraphParams.MONTHLY_GRAPHS:
    monthly_csv_filename = "{tz}_{start}_{end}{suffix}_MONTHLY.csv".format(
                              tz = par.GraphParams.PARSE_TIMEZONE.name,
                              start = par.GraphParams.DATA_START_DATE.strftime("%Y%m%d"),
                              end = par.GraphParams.DATA_END_DATE.strftime("%Y%m%d"),
                              suffix = par.GraphParams.FILENAME_SUFFIX)
    monthly_csv = dio.get_parsed_csv_filepath(monthly_csv_filename)
    monthly_data_dict = csvutil.CsvIO.read_data_csv(monthly_csv)
    build_monthly_graphs(monthly_data_dict, sum_type_records, order_type_records, record_units)

if __name__ == '__main__':
  build_graphs()