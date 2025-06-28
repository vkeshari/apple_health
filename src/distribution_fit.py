import params as par
from util import csvutil, dataio, datautil, paramutil, timeutil

def fit_distribution(data_dict, record_aggregation_types, record_units, period,
                      record_types, num_best_fits):
  assert not record_aggregation_types.keys() ^ record_units.keys()
  assert not record_types - record_aggregation_types.keys()

  print()
  fit_results = {}
  for r in record_types:
    if not record_aggregation_types[r] == par.AggregateType.SUM:
      continue

    r_by_date = csvutil.CsvData.build_time_series_for_record(r, data_dict, record_units[r],
                                                              sort = True)
    fit_results[r] = datautil.DataSeriesMetrics.get_best_fit(list(r_by_date.values()),
                                                              num_best_fits = num_best_fits)

  print()
  print("Fit Results for {} data.".format(period.name.capitalize()))
  for r in fit_results:
    print()
    print(r.name)
    print(fit_results[r])


def distribution_fit():
  paramutil.Validator.validate_distribution_fit()

  record_aggregation_types = paramutil.RecordProperties.get_record_aggregation_types()
  record_units = paramutil.RecordProperties.get_record_units()

  dio = dataio.DataIO(par.DataParams)

  for period in par.DistributionFitParams.AGGREGATION_PERIODS:
    data_csv = dio.get_csv_file(period = period)
    data_dict = csvutil.CsvIO.read_data_csv(data_csv)

    fit_distribution(data_dict, record_aggregation_types, record_units, period = period,
                      record_types = par.DistributionFitParams.ACTIVITIES,
                      num_best_fits = par.DistributionFitParams.NUM_BEST_FITS)


if __name__ == '__main__':
  distribution_fit()
