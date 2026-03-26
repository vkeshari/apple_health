import params as par
from graph import histogram, linegraph
from util import csvutil, dataio, paramutil, timeutil

from matplotlib import pyplot as plt
import numpy as np
import math

DAYS_IN_WEEK = 7

def build_moving_averages(data_dict, record_aggregation_types, record_units,
                          activities, min_weeks, max_weeks, consistent_periods, graph_sets):
  
  all_dates = list(data_dict.keys())
  activity_to_vals = {a: [] for a in activities if all(a in data_dict[d] for d in data_dict)}
  for d in data_dict:
    for a in activity_to_vals:
      activity_to_vals[a].append(data_dict[d][a])
  
  for a in activity_to_vals:
    assert len(activity_to_vals[a]) == len(all_dates)

  for a in activity_to_vals:
    overall_avg = np.average(activity_to_vals[a])
    print(str(a) + '\t' + "{:.2f}".format(overall_avg))

    moving_averages = {n: {} for n in range(min_weeks, max_weeks + 1)}
    for i in range(len(activity_to_vals[a]) + 1):
      if i < min_weeks * DAYS_IN_WEEK or consistent_periods and i < max_weeks * DAYS_IN_WEEK:
        continue
      
      for n in moving_averages:
        window_days = n * DAYS_IN_WEEK
        if i < window_days:
          continue

        moving_averages[n][all_dates[i - 1]] = \
                np.sum(activity_to_vals[a][i - window_days : i]) / window_days
    
    for n in moving_averages:
      print (str(n) + '\t' + str(len(moving_averages[n])) + '\t' + str(min(moving_averages[n])) + '\t' + str(max(moving_averages[n])))

    rms_errors = {}
    for n in moving_averages:
      sq_sum = 0.0
      for d in moving_averages[n]:
        sq_sum += math.pow(moving_averages[n][d] - overall_avg, 2)
      rms_errors[n] = math.sqrt(sq_sum / len(moving_averages[n]))

    xs, ys = zip(*rms_errors.items())
    plt.plot(xs,  ys)
    plt.show()
    
    pair_rms_errors = {s: {l: 0.0 for l in range(s, max_weeks + 1)} \
                      for s in range(min_weeks, max_weeks + 1)}
    for s in pair_rms_errors:
      for l in pair_rms_errors[s]:
        sq_sum = 0.0
        for d in moving_averages[s]:
          if d not in moving_averages[l]:
            continue
          sq_sum += math.pow(moving_averages[s][d] - moving_averages[l][d], 2)
        pair_rms_errors[s][l] = math.sqrt(sq_sum / len(moving_averages[l]))
    
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
        xs, ys = zip(*moving_averages[p].items())
        plt.plot(xs, ys, linewidth = 2, alpha = 0.5)
      
      plt.show()


def moving_average():
  paramutil.Validator.validate_moving_average()

  record_aggregation_types = paramutil.RecordProperties.get_record_aggregation_types()
  record_units = paramutil.RecordProperties.get_record_units()

  dio = dataio.DataIO(par.DataParams)

  data_csv = dio.get_csv_file(period = par.AggregationPeriod.DAILY)
  data_dict = csvutil.CsvIO.read_data_csv(data_csv)

  build_moving_averages(data_dict, record_aggregation_types, record_units,
                        activities = par.MovingAverageParams.ACTIVITIES,
                        min_weeks = par.MovingAverageParams.MIN_WEEKS,
                        max_weeks = par.MovingAverageParams.MAX_WEEKS,
                        consistent_periods = par.MovingAverageParams.CONSISTENT_PERIODS,
                        graph_sets = par.MovingAverageParams.GRAPH_SETS)


if __name__ == '__main__':
  moving_average()