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

  return sorted(subset_averages)

def build_bucket_tuning_graphs(data_dict, record_aggregation_types, record_units,
                                bucket_range, num_runs):
  assert not record_aggregation_types.keys() ^ record_units.keys()

  for r in record_aggregation_types:
    if not record_aggregation_types[r] == par.AggregateType.SUM:
      continue

    r_by_date = csvutil.CsvData.build_time_series_for_record(r, data_dict, record_units[r])

    datasets = {}
    for num_buckets in bucket_range:
      run_subset_averages = [bucket_randomly(r_by_date.values(), num_buckets = num_buckets) \
                                for _ in range(num_runs)]
      datasets[num_buckets] = []
      zipped_run_subset_averages = zip(*run_subset_averages)
      for vals in zipped_run_subset_averages:
        assert len(vals) == num_runs
        datasets[num_buckets].append(np.average(vals))
      assert len(datasets) == num_buckets

    print()
    print("Built Bucket Tuning Datasets for {}.".format(r))
    
    tuning_graph = tuning.TuningGraph(datasets, r,
                                      record_units[r], record_aggregation_types[r],
                                      raw_values = list(r_by_date.values()), num_runs = num_runs)
    tuning_graph.plot(show = False, save = True)


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
  build_bucket_tuning_graphs(data_dict, record_aggregation_types, record_units,
                              bucket_range, par.BucketTuningParams.NUM_RUNS)

if __name__ == '__main__':
  bucket_tuning()
