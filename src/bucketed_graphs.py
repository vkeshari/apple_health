import numpy as np

import params as par
from graph import histogram
from util import csvutil, dataio, paramutil, timeutil

def bucket_by_year(r_by_date):
  r_by_sorted_date = {d: v for (d, v) in sorted(r_by_date.items())}
  datasets = {}
  for d in r_by_sorted_date:
    y = d.year
    if y not in datasets:
      datasets[y] = {}
    datasets[y][d] = r_by_sorted_date[d]
  
  return datasets

def bucket_randomly(r_by_date, num_buckets):
  dates = np.array(list(r_by_date.keys()))
  np.random.shuffle(dates)
  date_subsets = np.array_split(dates, num_buckets)
  assert len(date_subsets) == num_buckets

  datasets = {}
  for i, ds in enumerate(date_subsets):
    label = 'Random Dates {}'.format(i + 1)
    r_by_date_subset = {d: v for (d, v) in r_by_date.items() if d in ds}
    datasets[label] = {d: v for (d, v) in sorted(r_by_date_subset.items())}

  return datasets

def build_period_bucket_graphs(data_dict, record_aggregation_types, record_units,
                                start_date, end_date, period, bucketing):
  assert not record_aggregation_types.keys() ^ record_units.keys()

  print()
  for r in record_aggregation_types:
    r_by_date = csvutil.CsvData.build_time_series_for_record(r, data_dict, record_units[r],
                                                                start_date, end_date)

    if bucketing == par.BucketingType.BY_YEAR:
      datasets = bucket_by_year(r_by_date)
    elif bucketing == par.BucketingType.RANDOMLY:
      datasets = bucket_randomly(r_by_date,
                                  num_buckets = par.BucketedGraphParams.NUM_RANDOM_BUCKETS)
    
    if record_aggregation_types[r] == par.AggregateType.SUM:
      hist = histogram.MultiSeriesHistogram(
                bucketing = bucketing,
                datasets = datasets,
                record_type = r,
                record_units = record_units[r],
                record_aggregation_type = record_aggregation_types[r],
                start_date = start_date,
                end_date = end_date,
                period = period)
      hist.plot(show = False, save = True)

  print()
  print("Created {} graphs.".format(period.name.capitalize()))


def bucketed_graphs():
  paramutil.Validator.validate_bucketed_graphs()

  record_aggregation_types = paramutil.RecordProperties.get_record_aggregation_types()
  record_units = paramutil.RecordProperties.get_record_units()

  dio = dataio.DataIO(par.DataParams)
  for period in par.BucketedGraphParams.AGGREGATION_PERIODS:
    data_csv = dio.get_csv_file(period = period)
    data_dict = csvutil.CsvIO.read_data_csv(data_csv)
    
    build_period_bucket_graphs(data_dict, record_aggregation_types, record_units,
                                start_date = par.BucketedGraphParams.GRAPH_START_DATE,
                                end_date = par.BucketedGraphParams.GRAPH_END_DATE,
                                period = period, bucketing = par.BucketedGraphParams.BUCKETING)

if __name__ == '__main__':
  bucketed_graphs()
