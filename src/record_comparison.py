import params as par

from graph import comparison
from util import csvutil, dataio, datautil, paramutil, timeutil
  
def make_comparisons_with_period_delta(all_r_to_dates, record_aggregation_types, record_units,
                                        period, period_delta, min_correlations):

  print()
  print("{}\t+{}".format(period.name, period_delta))

  record_types = all_r_to_dates.keys()
  slow_changing_records = paramutil.RecordGroups.get_slow_changing_record_types()

  for r1 in record_types:
    for r2 in record_types:
      if r1 == r2 and (period_delta == 0 or r1 in slow_changing_records):
        continue

      r1_by_date = all_r_to_dates[r1]
      r2_by_date = all_r_to_dates[r2]

      vals1 = []
      vals2 = []
      for d in r1_by_date:
        r2d = timeutil.CalendarUtil.get_next_period_start_date(d, period = period, n = period_delta)
        if r2d not in r2_by_date:
          continue
        vals1.append(r1_by_date[d])
        vals2.append(r2_by_date[r2d])
      assert len(vals1) == len(vals2)

      corrs, _ = datautil.DataComparisonMetrics.get_correlations(vals1, vals2)
      if not any(abs(corrs[m]) >= cut for m, cut in min_correlations.items()):
        continue

      com = comparison.ComparisonGraph(tuple([vals1, vals2]),
                                        tuple([r1, r2]),
                                        tuple([record_units[r1], record_units[r2]]),
                                        tuple([record_aggregation_types[r1],
                                                record_aggregation_types[r2]]),
                                        period, period_delta,
                                        correlations = corrs)
      com.plot(show = False, save = True)

def make_all_comparisons(data_dict, record_aggregation_types, record_units,
                          period, max_period_delta, min_correlations):
  assert not record_aggregation_types.keys() ^ record_units.keys()
  
  record_types = record_aggregation_types.keys()

  all_r_to_dates = {}
  for r in record_types:
    all_r_to_dates[r] = csvutil.CsvData.build_time_series_for_record(r, data_dict,
                                                                      unit = record_units[r])
  
  for pd in range(max_period_delta):
    make_comparisons_with_period_delta(all_r_to_dates, record_aggregation_types, record_units,
                                        period, pd, min_correlations)


def record_comparison():
  paramutil.Validator.validate_record_comparison()

  record_aggregation_types = paramutil.RecordProperties.get_record_aggregation_types()
  record_units = paramutil.RecordProperties.get_record_units()

  dio = dataio.DataIO(par.DataParams)

  for period in par.RecordComparisonParams.AGGREGATION_PERIODS:
    data_csv = dio.get_csv_file(period = period)
    data_dict = csvutil.CsvIO.read_data_csv(data_csv)

    make_all_comparisons(data_dict, record_aggregation_types, record_units,
                          period = period,
                          max_period_delta = par.RecordComparisonParams.MAX_PERIOD_DELTAS[period],
                          min_correlations = par.RecordComparisonParams.MIN_CORRELATIONS)

if __name__ == '__main__':
  record_comparison()
