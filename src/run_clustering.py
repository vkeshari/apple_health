import numpy as np
from scipy import stats
from sklearn import decomposition

import params as par
from graph import clustering
from util import csvutil, dataio, datautil, paramutil

def remove_outliers(dataset, dates):
  assert len(dataset) == len(dates)

  reduced_data = []
  reduced_dates = []
  for i, date_vals in enumerate(dataset):
    if all([-1 <= dv <= 1 for dv in date_vals]):
      reduced_data.append(date_vals)
      reduced_dates.append(dates[i])
  return reduced_data, reduced_dates

def get_groups_by_record(dataset, record_types, rescalers, r):
  assert r in record_types
  percentile_intervals = [20, 40, 60, 80, 100]

  groups = []
  r_index = record_types.index(r)
  vals = dataset[ : , r_index]
  for v in vals:
    percentile = stats.percentileofscore(vals, v)
    for interval in percentile_intervals:
      if percentile <= interval:
        groups.append(rescalers[r].backscale(stats.scoreatpercentile(vals, interval)))
        break
    else:
      groups.append(10)
  return groups

def do_clustering(data_dict, record_aggregation_types, record_units, record_types, period):
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
  dataset, dates = remove_outliers(dataset, all_dates)

  dataset = np.array(dataset)
  print("Built datasets.")

  pca = decomposition.PCA(n_components = 2)
  pca.fit(dataset)
  dataset_new = pca.transform(dataset)
  print("Run Dimensionality Reduction.")

  for r in record_types:
    groups = get_groups_by_record(dataset, record_types, rescalers, r)

    cluster = clustering.ClusteringGraph(xy_vals = dataset_new,
                                          dates  = dates,
                                          groups = groups,
                                          record_types = record_types,
                                          group_by_record = r,
                                          record_unit = record_units[r],
                                          period = period)
    cluster.plot(show = False, save = True)

  print()
  print("Clustering finished for {} data.".format(period.name))


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
                  period = period)



if __name__ == '__main__':
  run_clustering()