import params as par
from graph import histogram, linegraph, movingavg
from util import csvutil, dataio, paramutil, timeutil

from matplotlib import pyplot as plt
import numpy as np
import math

DAYS_IN_WEEK = 7

def build_moving_averages(data_dict, activities, min_weeks, max_weeks, consistent_periods):
  
  all_dates = list(data_dict.keys())
  activity_to_vals = {a: [] for a in activities if all(a in data_dict[d] for d in data_dict)}
  for d in data_dict:
    for a in activity_to_vals:
      activity_to_vals[a].append(data_dict[d][a])
  
  for a in activity_to_vals:
    assert len(activity_to_vals[a]) == len(all_dates)

  moving_averages = {a: {} for a in activity_to_vals}
  rolling_averages = {a: {} for a in activity_to_vals}
  overall_averages = {a: 0 for a in activity_to_vals}

  for a in activity_to_vals:
    overall_avg = np.average(activity_to_vals[a])
    print(str(a) + '\tAVG:\t' + "{:.2f}".format(overall_avg))
    overall_averages[a] = overall_avg

    moving_averages[a] = {n: {} for n in range(min_weeks, max_weeks + 1)}
    for i in range(len(activity_to_vals[a]) + 1):
      
      if i < min_weeks * DAYS_IN_WEEK or consistent_periods and i < max_weeks * DAYS_IN_WEEK:
        continue

      if i > 0:
        rolling_averages[a][all_dates[i - 1]] = \
                  np.sum(activity_to_vals[a][ : i]) / i
      
      for n in moving_averages[a]:
        window_days = n * DAYS_IN_WEEK
        if i < window_days:
          continue

        moving_averages[a][n][all_dates[i - 1]] = \
                np.sum(activity_to_vals[a][i - window_days : i]) / window_days
  
  return moving_averages, rolling_averages, overall_averages


def show_moving_averages(record_aggregation_types, record_units,
                          moving_averages, rolling_averages, overall_averages,
                          use_rolling_avg, graph_sets):
  
  for a in moving_averages:
    activity_ma = moving_averages[a]
    activity_ra = rolling_averages[a]
    activity_oa = overall_averages[a]

    rms_errors = {}
    for n in activity_ma:
      sq_sum = 0.0
      for d in activity_ma[n]:
        if use_rolling_avg:
          sq_sum += math.pow(activity_ma[n][d] - activity_ra[d], 2)
        else:
          sq_sum += math.pow(activity_ma[n][d] - activity_oa, 2)
      rms_errors[n] = math.sqrt(sq_sum / len(activity_ma[n]))

    # xs, ys = zip(*rms_errors.items())
    # plt.plot(xs,  ys)
    # plt.show()
  
    for gs in graph_sets:
      relevant_moving_avgs = {n: avgs for n, avgs in activity_ma.items() if n in gs}
      relevant_rms_errors = {n: rms for n, rms in rms_errors.items() if n in gs}
      graph = movingavg.MovingAvgGraph(relevant_moving_avgs, activity_ra, activity_oa,
                                        relevant_rms_errors, use_rolling_avg,
                                        a, record_units[a], record_aggregation_types[a])
      graph.plot(show = False, save = True)


def process_moving_averages(data_dict, record_aggregation_types, record_units,
                            activities, min_weeks, max_weeks, consistent_periods,
                            use_rolling_avg, graph_sets):
  
  moving_averages, rolling_averages, overall_averages = \
        build_moving_averages(data_dict, activities, min_weeks, max_weeks, consistent_periods)
  show_moving_averages(record_aggregation_types, record_units,
                        moving_averages, rolling_averages, overall_averages,
                        use_rolling_avg, graph_sets)


def moving_average():
  paramutil.Validator.validate_moving_average()

  record_aggregation_types = paramutil.RecordProperties.get_record_aggregation_types()
  record_units = paramutil.RecordProperties.get_record_units()

  dio = dataio.DataIO(par.DataParams)

  data_csv = dio.get_csv_file(period = par.AggregationPeriod.DAILY)
  data_dict = csvutil.CsvIO.read_data_csv(data_csv)

  process_moving_averages(data_dict, record_aggregation_types, record_units,
                          activities = par.MovingAverageParams.ACTIVITIES,
                          min_weeks = par.MovingAverageParams.MIN_WEEKS,
                          max_weeks = par.MovingAverageParams.MAX_WEEKS,
                          consistent_periods = par.MovingAverageParams.CONSISTENT_PERIODS,
                          use_rolling_avg = par.MovingAverageParams.USE_ROLLING_AVG_FOR_ERRORS,
                          graph_sets = par.MovingAverageParams.GRAPH_SETS)


if __name__ == '__main__':
  moving_average()