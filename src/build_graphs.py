import params as par
from graph import histogram
from util import csvutil
from util import dataio
from util import timeutil

def validate_params():
  if par.AggregateGraphParams.FILENAME_SUFFIX:
    assert par.AggregateGraphParams.FILENAME_SUFFIX[0] == '_'
    assert not par.AggregateGraphParams.FILENAME_SUFFIX[-1] == '_'

  assert par.AggregateGraphParams.DATA_END_DATE > par.AggregateGraphParams.DATA_START_DATE
  assert par.AggregateGraphParams.GRAPH_END_DATE > par.AggregateGraphParams.GRAPH_START_DATE

def get_record_aggregation_types():
  record_aggregation_types = {}
  for rt in par.RecordParams.RECORD_TYPES:
    record_aggregation_types[rt.record] = rt.aggregation
  return record_aggregation_types

def get_record_units():
  record_units = {}
  for rt in par.RecordParams.RECORD_TYPES:
    record_units[rt.record] = rt.unit
  return record_units

def build_period_graphs(daily_data_dict, record_aggregation_types, record_units,
                        start_date, end_date, period):
  assert not record_aggregation_types.keys() ^ record_units.keys()

  for r in record_aggregation_types:
    r_by_date = {}
    for d in daily_data_dict:
      if r not in daily_data_dict[d]:
        continue
      if not timeutil.DatetimeUtil.check_date_range(d, start_date, end_date):
        continue
      if not daily_data_dict[d][r] == 0:
        r_by_date[d] = daily_data_dict[d][r]
    r_by_sorted_date = {d: v for (d, v) in sorted(r_by_date.items())}

    if record_aggregation_types[r] == par.AggregateType.SUM:
      hist = histogram.SingleSeriesHistogram(data = r_by_sorted_date,
                                              record_type = r,
                                              record_units = record_units[r],
                                              record_aggregation_type = record_aggregation_types[r],
                                              start_date = start_date,
                                              end_date = end_date,
                                              period = period)
      hist.plot(show = False, save = True)

  print()
  print("Created {} graphs.".format(period.name.capitalize()))


def build_graphs():
  validate_params()

  record_aggregation_types = get_record_aggregation_types()
  record_units = get_record_units()

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
    build_period_graphs(data_dict, record_aggregation_types, record_units,
                        start_date = par.AggregateGraphParams.GRAPH_START_DATE,
                        end_date = par.AggregateGraphParams.GRAPH_END_DATE,
                        period = period)

if __name__ == '__main__':
  build_graphs()