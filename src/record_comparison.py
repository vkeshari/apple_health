import params as par

from graph import comparison
from util import csvutil, dataio, datautil, paramutil, timeutil

class RecordComparator:

  def __init__(self, record_type_pair, record_aggregation_type_pair, record_unit_pair,
                period, period_delta, min_correlations, min_acceptable_correlation):
    self.record_type_pair = record_type_pair
    self.record_aggregation_type_pair = record_aggregation_type_pair
    self.record_unit_pair = record_unit_pair
    self.period = period
    self.period_delta = period_delta
    self.min_correlations = min_correlations
    self.min_acceptable_correlation = min_acceptable_correlation
  
  def compare_and_graph_values(self, vals_by_date_1, vals_by_date_2, val_type_pair):
    vals1 = []
    vals2 = []
    for d in vals_by_date_1:
      r2d = timeutil.CalendarUtil.get_next_period_start_date(
                d, period = self.period, n = self.period_delta)
      if r2d not in vals_by_date_2:
        continue
      vals1.append(vals_by_date_1[d])
      vals2.append(vals_by_date_2[r2d])
    assert len(vals1) == len(vals2)

    corrs, _ = datautil.DataComparisonMetrics.get_correlations(vals1, vals2)
    if any(abs(corrs[m]) >= cut for m, cut in self.min_correlations.items()) \
        and all(abs(c) >= self.min_acceptable_correlation for c in corrs.values()):
      com = comparison.ComparisonGraph(tuple([vals1, vals2]),
                                        self.record_type_pair,
                                        self.record_unit_pair,
                                        self.record_aggregation_type_pair,
                                        val_type_pair,
                                        self.period, self.period_delta,
                                        correlations = corrs)
      com.plot(show = False, save = True)


def make_comparisons_with_period_delta(all_values_by_date, all_deltas_by_date,
                                        record_aggregation_types, record_units,
                                        period, period_delta,
                                        min_correlations, min_acceptable_correlation):

  print()
  print("{}\t+{}".format(period.name, period_delta))

  record_types = all_values_by_date.keys()
  slow_changing_records = paramutil.RecordGroups.get_slow_changing_record_types()

  for r1 in record_types:
    for r2 in record_types:
      if r1 == r2 or set([r1, r2]) in paramutil.RecordGroups.get_highly_correlated_record_pairs():
        continue

      record_type_pair = tuple([r1, r2])
      record_aggregation_type_pair = tuple([record_aggregation_types[r1],
                                            record_aggregation_types[r2]])
      record_unit_pair = tuple([record_units[r1], record_units[r2]])
      comparator = RecordComparator(record_type_pair, record_aggregation_type_pair,
                                    record_unit_pair, period, period_delta,
                                    min_correlations, min_acceptable_correlation)

      r1_vals_by_date = all_values_by_date[r1]
      r2_vals_by_date = all_values_by_date[r2]
      r1_deltas_by_date = all_deltas_by_date[r1]
      r2_deltas_by_date = all_deltas_by_date[r2]
      
      comparator.compare_and_graph_values(r1_vals_by_date, r2_vals_by_date,
                                          tuple([par.ValueType.RAW, par.ValueType.RAW]))
      if period_delta > 0:
        comparator.compare_and_graph_values(r1_vals_by_date, r2_deltas_by_date,
                                            tuple([par.ValueType.RAW, par.ValueType.DELTA]))
        comparator.compare_and_graph_values(r1_deltas_by_date, r2_vals_by_date,
                                            tuple([par.ValueType.DELTA, par.ValueType.RAW]))
        comparator.compare_and_graph_values(r1_deltas_by_date, r2_deltas_by_date,
                                            tuple([par.ValueType.DELTA, par.ValueType.DELTA]))


def make_all_comparisons(data_dict, record_aggregation_types, record_units,
                          period, max_period_delta, min_correlations, min_acceptable_correlation):
  assert not record_aggregation_types.keys() ^ record_units.keys()
  
  record_types = record_aggregation_types.keys()

  all_values_by_date = {}
  all_deltas_by_date = {}
  for r in record_types:
    all_values_by_date[r] = csvutil.CsvData.build_time_series_for_record(
                                r, data_dict, unit = record_units[r])
    all_deltas_by_date[r] = csvutil.CsvData.build_time_deltas_for_record(
                                r, data_dict, unit = record_units[r])
  
  for pd in range(max_period_delta):
    make_comparisons_with_period_delta(all_values_by_date, all_deltas_by_date,
                                        record_aggregation_types, record_units,
                                        period, pd, min_correlations, min_acceptable_correlation)


def record_comparison():
  paramutil.Validator.validate_record_comparison()

  record_aggregation_types = paramutil.RecordProperties.get_record_aggregation_types()
  record_units = paramutil.RecordProperties.get_record_units()

  dio = dataio.DataIO(par.DataParams)

  for period in par.RecordComparisonParams.AGGREGATION_PERIODS:
    data_csv = dio.get_csv_file(period = period)
    data_dict = csvutil.CsvIO.read_data_csv(data_csv)

    make_all_comparisons(
        data_dict, record_aggregation_types, record_units, period = period,
        max_period_delta = par.RecordComparisonParams.MAX_PERIOD_DELTAS[period],
        min_correlations = par.RecordComparisonParams.MIN_CORRELATIONS,
        min_acceptable_correlation = par.RecordComparisonParams.MIN_ACCEPTABLE_CORRELATION)

if __name__ == '__main__':
  record_comparison()
