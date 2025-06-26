import numpy as np
from matplotlib import pyplot as plt
from pathlib import Path

import params as par
from . import common
from util import dataio, datautil, timeutil

class TuningGraph:
  _resolution = tuple([10.8, 7.2])
  _text_spacing_factor = 0.03
  _subfolder = Path('tuning') / timeutil.Timestamp.get_timestamp()
  _dio = dataio.DataIO(par.DataParams)

  _order_intervals = [[5, 95], [10, 90], [25, 75]]
  last_interval_start = 0
  last_interal_end = 100
  for oi in _order_intervals:
    assert oi[0] > last_interval_start
    assert oi[1] < last_interal_end
    assert oi[1] > oi[0]
    assert oi[0] == 100 - oi[1]
    last_interval_start = oi[0]
    last_interal_end = oi[1]
  _outermost_interval = _order_intervals[0]

  _period_guide_days = {'YEARLY': 365.25,
                        'HALFYEARLY': 182.63,
                        'FOURMONTHLY': 121.75,
                        'QUARTERLY': 91.31,
                        'TWOMONTHLY': 60.88,
                        'SIXWEEKLY': 42,
                        'MONTHLY': 30.44,
                        'WEEKLY': 7}

  def __init__(self, datasets, record_type, record_units, record_aggregation_type,
                raw_values, num_runs):
    self.record_type = record_type
    self.record_units = record_units
    self.record_aggregation_type = record_aggregation_type
    self.num_runs = num_runs

    self.data_points = len(raw_values)
    self.raw_average = np.average(raw_values)

    self.datasets = datasets
    self.buckets = sorted(list(datasets.keys()))
    self.min_buckets = min(self.buckets)
    self.max_buckets = max(self.buckets)

    self.stats = {b: datautil.DataSeriesMetrics.get_stats(
                        datasets[b],
                        include_percentiles = np.array(self._order_intervals).flatten()) \
                      for b in self.buckets}
    self.averages = {b: self.stats[b]['average'] for b in self.buckets}

    self.ylim = round(np.average(list(self.averages.values())) * 2)
    self.fig, self.ax = plt.subplots(figsize = self._resolution)
    self.init_plot()
  
  def init_plot(self):
    title_text = common.GraphText.get_graph_title(self.record_type, self.record_units,
                                                  self._dio.data_params.START_DATE,
                                                  self._dio.data_params.END_DATE,
                                                  self.record_aggregation_type,
                                                  period = par.AggregationPeriod.DAILY,
                                                  bucketing = par.BucketingType.RANDOMLY)
    title_text = title_text + '\n' + "Average values per split by no. of splits"
    self.ax.set_title(title_text)
    self.ax.set_xlabel("No. of splits")
    self.ax.set_ylabel("Average {} per split".format(self.record_type.name))

    self.ax.set_xlim(0, self.max_buckets)
    xticks_major, xticks_minor = common.GraphTickSpacer.get_ticks(0, self.max_buckets)
    self.ax.set_xticks(xticks_major)
    self.ax.set_xticks(xticks_minor, minor = True)
    self.ax.grid(True, which = 'minor', axis = 'x', alpha = 0.3)
    self.ax.grid(True, which = 'major', axis = 'x', alpha = 0.5)

    self.ax.set_ylim(0, self.ylim)
    yticks_major, yticks_minor = common.GraphTickSpacer.get_ticks(0, self.ylim)
    self.ax.set_yticks(yticks_major)
    self.ax.set_yticks(yticks_minor, minor = True)
    self.ax.grid(True, which = 'minor', axis = 'y', alpha = 0.3)
    self.ax.grid(True, which = 'major', axis = 'y', alpha = 0.5)

  def show_period_guide(self, gmtp, num_days = 1, label = ''):
    period_line = self.data_points / num_days
    if period_line > self.max_buckets:
      return
    
    plt.axvline(x = period_line, ymax = gmtp.get_y_current(),
                linestyle = ':', linewidth = 2, color = 'gray', alpha = 0.8)
    gmtp.plot_annotation(s = label, x = period_line)

  def show_value_guide(self, val, alpha = 0.5):
    plt.axhline(y = val, linestyle = '-', linewidth = 2, color = 'gray', alpha = alpha)

  def show_or_save(self, show = False, save_filename = None):
    self.fig.tight_layout()
    if show:
      plt.show()
    if save_filename:
      save_file = self._dio.get_graph_filepath(self._subfolder / save_filename)
      save_file.parent.mkdir(exist_ok = True, parents = True)
      self.fig.savefig(save_file)
      print ("Graph written to: {}".format(save_file))
      plt.close()
  
  def plot(self, show = False, save = False):
    for b in self.buckets:
      lowest_percentile = self.stats[b]['percentiles'][self._outermost_interval[0]]
      highest_percentile = self.stats[b]['percentiles'][self._outermost_interval[1]]
      outliers = [v for v in self.datasets[b] \
                    if not lowest_percentile <= v <= highest_percentile]
      out = plt.scatter([b] * len(outliers), outliers,
                        s = 50, c = 'tab:gray', alpha = 0.1)
    
    fill_betweens = []
    for i, [low, high] in enumerate(self._order_intervals):
      y_mins = [self.stats[b]['percentiles'][low] for b in self.buckets]
      y_maxs = [self.stats[b]['percentiles'][high] for b in self.buckets]
      fb = self.ax.fill_between(x = self.buckets, y1 = y_mins, y2 = y_maxs, step = 'mid',
                                color = 'tab:blue', alpha = 0.3 + 0.1 * i, antialiased = True)
      fill_betweens.append(fb)
    
    y_positioner = common.YPositioner(y_start = 1.00 - 2 * self._text_spacing_factor,
                                      y_spacing = self._text_spacing_factor)
    gmtp = common.GraphMultiTextPrinter(ylim = self.ylim, y_positioner = y_positioner,
                                        horizontalalignment = 'left',
                                        verticalalignment = 'bottom')
    
    for p, d in self._period_guide_days.items():
      self.show_period_guide(gmtp, num_days = d, label = p)
    
    self.show_value_guide(self.raw_average, alpha = 0.6)
    self.show_value_guide(self.raw_average * 0.95, alpha = 0.5)
    self.show_value_guide(self.raw_average * 1.05, alpha = 0.5)
    ap = common.AnnotationPrinter(alpha = 0.6,
                                  horizontalalignment = 'left', verticalalignment = 'bottom')
    ap.plot_annotation(x = 0.1, y = self.raw_average * 1.05, s = "Avg +/- 5%")

    y_positioner = common.YPositioner(y_start = 1.00 - 2 * self._text_spacing_factor,
                                      y_spacing = self._text_spacing_factor)
    gmtp = common.GraphMultiTextPrinter(ylim = self.ylim, y_positioner = y_positioner,
                                        horizontalalignment = 'right',
                                        verticalalignment = 'bottom')
    gmtp.plot_annotation(s = 'Data for {} days'.format(self.data_points),
                          x = 0.99 * self.max_buckets)
    gmtp.plot_annotation(s = 'Randomized runs: {}'.format(self.num_runs),
                          x = 0.99 * self.max_buckets)
    
    self.ax.legend(handles = [out] + fill_betweens,
                    labels = ["Outliers"] \
                                + ["Middle {}%".format(oi[1] - oi[0]) \
                                      for oi in self._order_intervals],
                    loc = 'lower right')

    if save:
      save_filename = "TUNING_{}_{}_{}_{}.png".format(self.num_runs, self.min_buckets,
                                                      self.max_buckets, self.record_type.name)
      self.show_or_save(show = show, save_filename = save_filename)
    else:
      self.show_or_save(show = show)