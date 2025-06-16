import dataio
import params as par
from util import csvutil
from util import timeutil

def validate_params():
  if par.AggregateGraphParams.FILENAME_SUFFIX:
    assert par.AggregateGraphParams.FILENAME_SUFFIX[0] == '_'
    assert not par.AggregateGraphParams.FILENAME_SUFFIX[-1] == '_'

  assert par.AggregateGraphParams.DATA_END_DATE > par.AggregateGraphParams.DATA_START_DATE
  assert par.AggregateGraphParams.GRAPH_END_DATE > par.AggregateGraphParams.GRAPH_START_DATE

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

def build_period_graphs(daily_data_dict, sum_type_records, order_type_records, record_units,
                        start_date, end_date, period):
  for r in sum_type_records:
    r_by_date = {}
    for d in daily_data_dict:
      if not timeutil.DatetimeUtil.check_date_range(d, start_date, end_date):
        continue
      r_by_date[d] = daily_data_dict[d][r]
  
  r_by_sorted_date = {d: v for (d, v) in sorted(r_by_date.items())}

  print()
  print("Built data for {} graphs.".format(period.name.capitalize()))


def build_graphs():
  validate_params()

  sum_type_records, order_type_records = get_records_by_aggregate_type()
  record_units = get_records_units()

  dio = dataio.DataIO()
  for period in par.AggregateGraphParams.AGGREGATION_PERIODS:
    if period == par.AggregationPeriod.DAILY:
      period_text = ''
    else:
      period_text = '_' + period.name
  
    data_csv_filename = "{tz}_{start}_{end}{suffix}{period}.csv".format(
                            tz = par.AggregateGraphParams.PARSE_TIMEZONE.name,
                            start = par.AggregateGraphParams.DATA_START_DATE.strftime("%Y%m%d"),
                            end = par.AggregateGraphParams.DATA_END_DATE.strftime("%Y%m%d"),
                            suffix = par.AggregateGraphParams.FILENAME_SUFFIX,
                            period = period_text)
    data_csv = dio.get_parsed_csv_filepath(data_csv_filename)
    data_dict = csvutil.CsvIO.read_data_csv(data_csv)
    build_period_graphs(data_dict, sum_type_records, order_type_records, record_units,
                        start_date = par.AggregateGraphParams.GRAPH_START_DATE,
                        end_date = par.AggregateGraphParams.GRAPH_END_DATE,
                        period = period)

if __name__ == '__main__':
  build_graphs()