import params as par
from graph import histogram
from util import csvutil, dataio, paramutil, timeutil

def build_period_graphs(data_dict, record_aggregation_types, record_units,
                        start_date, end_date, period):
  assert not record_aggregation_types.keys() ^ record_units.keys()

  for r in record_aggregation_types:
    r_by_date = {}
    for d in data_dict:
      if r not in data_dict[d]:
        continue
      if not timeutil.DatetimeUtil.check_date_range(d, start_date, end_date):
        continue
      if not data_dict[d][r] == 0:
        r_by_date[d] = data_dict[d][r]
    r_by_sorted_date = {d: v for (d, v) in sorted(r_by_date.items())}

    if par.GraphParams.HISTOGRAMS and record_aggregation_types[r] == par.AggregateType.SUM:
      hist = histogram.SingleSeriesHistogram(
                data = r_by_sorted_date,
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
  paramutil.Validator.validate_build_graphs()

  record_aggregation_types = paramutil.RecordProperties.get_record_aggregation_types()
  record_units = paramutil.RecordProperties.get_record_units()

  dio = dataio.DataIO(par.DataParams)
  for period in par.GraphParams.AGGREGATION_PERIODS:
    if period == par.AggregationPeriod.DAILY:
      data_csv = dio.get_csv_file()
    else:
      data_csv = dio.get_csv_file(period = period)

    data_dict = csvutil.CsvIO.read_data_csv(data_csv)
    build_period_graphs(data_dict, record_aggregation_types, record_units,
                        start_date = par.GraphParams.GRAPH_START_DATE,
                        end_date = par.GraphParams.GRAPH_END_DATE,
                        period = period)

if __name__ == '__main__':
  build_graphs()