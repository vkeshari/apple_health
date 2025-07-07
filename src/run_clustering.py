import numpy as np
from sklearn import decomposition

import params as par
from graph import clustering
from util import csvutil, dataio, datautil, paramutil

def get_groups_by_record(dataset, record_types, rescalers, r):
  assert r in record_types

  groups = []
  r_index = record_types.index(r)
  vals = dataset[ : , r_index]
  for v in vals:
    for interval in [-2, -1, -0.5, -0.2, 0.2, 0.5, 1, 2]:
      if v < interval:
        groups.append(rescalers[r].backscale(interval))
        break
    else:
      groups.append(10)
  return groups

def do_clustering(data_dict, record_aggregation_types, record_units,
                  record_types, group_by, period):
  assert not record_aggregation_types.keys() ^ record_units.keys()
  assert not record_types - record_aggregation_types.keys()

  print()
  record_types = list(record_types)
  all_r_by_date = {}
  for r in record_types:
    r_by_date = csvutil.CsvData.build_time_series_for_record(r, data_dict, record_units[r])
    all_r_by_date[r] = r_by_date

  all_dates = set()
  for r in record_types:
    all_dates = all_dates | all_r_by_date[r].keys()
  all_dates = sorted(all_dates)

  rescalers = {}
  for r in record_types:
    rescalers[r] = datautil.Rescaler(all_r_by_date[r].values())

  dataset = []
  for d in all_dates:
    data_row = []
    for r in record_types:
      if d not in all_r_by_date[r]:
        data_row.append(0)
      else:
        data_row.append(rescalers[r].rescale(all_r_by_date[r][d]))
    dataset.append(data_row)
  dataset = np.array(dataset)

  groups = get_groups_by_record(dataset, record_types, rescalers, group_by)

  print()
  print("Built datasets.")

  pca = decomposition.PCA(n_components = 2)
  pca.fit(dataset)
  dataset_new = pca.transform(dataset)

  print("Run Dimensionality Reduction.")

  cluster = clustering.ClusteringGraph(xy_vals = dataset_new,
                                        dates  = all_dates,
                                        groups = groups,
                                        record_types = record_types,
                                        group_by_record = group_by,
                                        period = period)
  cluster.plot(show = False, save = True)

  print()
  print("Done clustering for {}".format(period.name))


def run_clustering():
  paramutil.Validator.validate_run_clustering()

  record_aggregation_types = paramutil.RecordProperties.get_record_aggregation_types()
  record_units = paramutil.RecordProperties.get_record_units()

  dio = dataio.DataIO(par.DataParams)

  for period in par.ClusteringParams.AGGREGATION_PERIODS:
    data_csv = dio.get_csv_file(period = period)
    data_dict = csvutil.CsvIO.read_data_csv(data_csv)

    do_clustering(data_dict, record_aggregation_types, record_units,
                  record_types = par.ClusteringParams.ACTIVITIES,
                  group_by = par.ClusteringParams.GROUP_BY_ACTIVITY,
                  period = period)



if __name__ == '__main__':
  run_clustering()