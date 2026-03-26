import params as par
from graph import histogram, linegraph
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

  for a in activity_to_vals:
    overall_avg = np.average(activity_to_vals[a])
    print(str(a) + '\tAVG:\t' + "{:.2f}".format(overall_avg))

    moving_averages[a] = {n: {} for n in range(min_weeks, max_weeks + 1)}
    for i in range(len(activity_to_vals[a]) + 1):
      if i < min_weeks * DAYS_IN_WEEK or consistent_periods and i < max_weeks * DAYS_IN_WEEK:
        continue
      
      for n in moving_averages[a]:
        window_days = n * DAYS_IN_WEEK
        if i < window_days:
          continue

        moving_averages[a][n][all_dates[i - 1]] = \
                np.sum(activity_to_vals[a][i - window_days : i]) / window_days
    
    return moving_averages, overall_avg
  

def show_moving_averages(moving_averages, overall_avg, min_weeks, max_weeks, graph_sets):
  
  for a in moving_averages:
    activity_ma = moving_averages[a]

    rms_errors = {}
    for n in activity_ma:
      sq_sum = 0.0
      for d in activity_ma[n]:
        sq_sum += math.pow(activity_ma[n][d] - overall_avg, 2)
      rms_errors[n] = math.sqrt(sq_sum / len(activity_ma[n]))

    xs, ys = zip(*rms_errors.items())
    plt.plot(xs,  ys)
    plt.show()
    
    pair_rms_errors = {s: {l: 0.0 for l in range(s, max_weeks + 1)} \
                      for s in range(min_weeks, max_weeks + 1)}
    for s in pair_rms_errors:
      for l in pair_rms_errors[s]:
        sq_sum = 0.0
        for d in activity_ma[s]:
          if d not in activity_ma[l]:
            continue
          sq_sum += math.pow(activity_ma[s][d] - activity_ma[l][d], 2)
        pair_rms_errors[s][l] = math.sqrt(sq_sum / len(activity_ma[l]))
    
    max_val = max([max(pair_rms_errors[s].values()) for s in pair_rms_errors])
    
    imvals = np.full((max_weeks - min_weeks + 1, max_weeks - min_weeks + 1), np.nan)
    for i, s in enumerate(pair_rms_errors.keys()):
      for j, l in enumerate(pair_rms_errors[s].keys()):
        imvals[i, i + j] = pair_rms_errors[s][l]
    
    plt.imshow(imvals, origin = 'lower', aspect = 'auto',
                extent = (min_weeks, max_weeks + 1, min_weeks, max_weeks + 1),
                cmap = 'viridis', vmin = 0, vmax = max_val)
    
    plt.show()
  
    for gs in graph_sets:
      for p in gs:
        xs, ys = zip(*activity_ma[p].items())
        plt.plot(xs, ys, linewidth = 2, alpha = 0.5)
      
      plt.show()


def process_moving_averages(data_dict, record_aggregation_types, record_units,
                            activities = par.MovingAverageParams.ACTIVITIES,
                            min_weeks = par.MovingAverageParams.MIN_WEEKS,
                            max_weeks = par.MovingAverageParams.MAX_WEEKS,
                            consistent_periods = par.MovingAverageParams.CONSISTENT_PERIODS,
                            graph_sets = par.MovingAverageParams.GRAPH_SETS):
  
  moving_averages, overall_avg = build_moving_averages(data_dict, activities, min_weeks, max_weeks,
                                                        consistent_periods)
  show_moving_averages(moving_averages, overall_avg, min_weeks, max_weeks, graph_sets)


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
                          graph_sets = par.MovingAverageParams.GRAPH_SETS)


if __name__ == '__main__':
  moving_average()