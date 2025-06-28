import params as par

from concurrent.futures import ProcessPoolExecutor, wait
from graph import comparison
from util import csvutil, dataio, datautil, paramutil, timeutil

class RecordComparator:

  def __init__(self, record_type_pair, record_aggregation_type_pair, record_unit_pair,
                period, period_delta, correlation_params):
    self.record_type_pair = record_type_pair
    self.record_aggregation_type_pair = record_aggregation_type_pair
    self.record_unit_pair = record_unit_pair

    self.period = period
    self.period_delta = period_delta

    self.correlation_cutoffs = correlation_params['correlation_cutoffs']
    self.min_acceptable_correlation = correlation_params['min_acceptable_correlation']
    self.min_datapoints = correlation_params['min_datapoints']
  
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

    if len(vals1) < self.min_datapoints:
      return

    corrs, corr_pvals = datautil.DataComparisonMetrics.get_correlations(vals1, vals2)
    any_correlation_above_cutoff = \
        any(abs(corrs[m]) >= cut for m, cut in self.correlation_cutoffs.items())
    all_correlations_above_minimum_acceptable_value = \
        all(abs(c) >= self.min_acceptable_correlation for c in corrs.values())
    if not any_correlation_above_cutoff or not all_correlations_above_minimum_acceptable_value:
      return
    
    com = comparison.ComparisonGraph(tuple([vals1, vals2]),
                                      self.record_type_pair,
                                      self.record_unit_pair,
                                      self.record_aggregation_type_pair,
                                      val_type_pair,
                                      self.period, self.period_delta,
                                      correlations = corrs,
                                      correlation_pvals = corr_pvals)
    com.plot(show = False, save = True)


def make_comparisons_with_period_delta(all_values_by_date, all_deltas_by_date,
                                        record_aggregation_types, record_units,
                                        period, period_delta, correlation_params):

  print("{}\t+{}".format(period.name, period_delta))

  record_types = all_values_by_date.keys()

  seen_same_period_pairs = []
  for r1 in record_types:
    for r2 in record_types:
      if r1 == r2 \
          or any(paramutil.RecordCorrelations.is_ignored_activity(r) for r in [r1, r2]) \
          or paramutil.RecordCorrelations.is_highly_correlated_pair(r1, r2):
        continue
      if period_delta == 0:
        if {r1, r2} in seen_same_period_pairs:
          continue
        seen_same_period_pairs.append({r1, r2})

      record_type_pair = tuple([r1, r2])
      record_aggregation_type_pair = tuple([record_aggregation_types[r1],
                                            record_aggregation_types[r2]])
      record_unit_pair = tuple([record_units[r1], record_units[r2]])
      comparator = RecordComparator(record_type_pair, record_aggregation_type_pair,
                                    record_unit_pair, period, period_delta, correlation_params)

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

def make_all_comparisons(executor, data_dict, record_aggregation_types, record_units, period,
                          max_period_delta, correlation_params):
  assert not record_aggregation_types.keys() ^ record_units.keys()
  
  record_types = record_aggregation_types.keys()

  all_values_by_date = {}
  all_deltas_by_date = {}
  for r in record_types:
    all_values_by_date[r] = csvutil.CsvData.build_time_series_for_record(
                                r, data_dict, unit = record_units[r])
    all_deltas_by_date[r] = csvutil.CsvData.build_time_deltas_for_record(
                                r, data_dict, unit = record_units[r])
  
  pd_futs = []
  for pd in range(max_period_delta + 1):
    pd_futs.append(executor.submit(make_comparisons_with_period_delta,
                                    all_values_by_date, all_deltas_by_date,
                                    record_aggregation_types, record_units,
                                    period, pd, correlation_params))
  return pd_futs


def record_comparison():
  paramutil.Validator.validate_record_comparison()

  record_aggregation_types = paramutil.RecordProperties.get_record_aggregation_types()
  record_units = paramutil.RecordProperties.get_record_units()

  dio = dataio.DataIO(par.DataParams)

  with ProcessPoolExecutor() as executor:
    all_pd_futs = []
    for period in par.RecordComparisonParams.AGGREGATION_PERIODS:
      data_csv = dio.get_csv_file(period = period)
      data_dict = csvutil.CsvIO.read_data_csv(data_csv)

      correlation_params = paramutil.RecordCorrelations.get_correlation_params()

      pd_futs = make_all_comparisons(executor,
                    data_dict, record_aggregation_types, record_units, period = period,
                    max_period_delta = par.RecordComparisonParams.MAX_PERIOD_DELTAS[period],
                    correlation_params = correlation_params)
      all_pd_futs += pd_futs
    wait(all_pd_futs)

if __name__ == '__main__':
  record_comparison()
