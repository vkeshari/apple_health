import numpy as np

import params as par
from graph import tuning
from util import csvutil, dataio, paramutil

def bucket_randomly(r_values, num_buckets):
  all_values = list(r_values)
  np.random.shuffle(all_values)
  value_subsets = np.array_split(all_values, num_buckets)
  assert len(value_subsets) == num_buckets

  subset_averages = []
  for i, vs in enumerate(value_subsets):
    subset_averages.append(np.average(vs))

  return subset_averages

def build_bucket_tuning_data(data_dict, record_aggregation_types, record_units, bucket_range):
  assert not record_aggregation_types.keys() ^ record_units.keys()

  for r in record_aggregation_types:
    if not record_aggregation_types[r] == par.AggregateType.SUM:
      continue

    r_by_date = {}
    for d in data_dict:
      if r not in data_dict[d]:
        continue
      if not data_dict[d][r] == 0:
        r_by_date[d] = data_dict[d][r]

    datasets = {}
    for num_buckets in bucket_range:
      datasets[num_buckets] = bucket_randomly(r_by_date.values(), num_buckets = num_buckets)
    
    tuning_graph = tuning.TuningGraph(datasets, r,
                                      record_units[r], record_aggregation_types[r],
                                      data_points = len(r_by_date))
    tuning_graph.plot(show = False, save = True)

    print()
    print("Built Bucket Tuning Datasets for {}.".format(r))


def bucket_tuning():
  paramutil.Validator.validate_bucket_tuning()

  record_aggregation_types = paramutil.RecordProperties.get_record_aggregation_types()
  record_units = paramutil.RecordProperties.get_record_units()

  dio = dataio.DataIO(par.DataParams)
  data_csv = dio.get_csv_file()
  data_dict = csvutil.CsvIO.read_data_csv(data_csv)

  bucket_range = list(range(par.BucketTuningParams.MIN_BUCKETS,
                            par.BucketTuningParams.MAX_BUCKETS + 1,
                            par.BucketTuningParams.BUCKET_STEP))
  build_bucket_tuning_data(data_dict, record_aggregation_types, record_units, bucket_range)

if __name__ == '__main__':
  bucket_tuning()
