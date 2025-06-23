import numpy as np
from matplotlib import pyplot as plt
from pathlib import Path

import params as par
from . import common
from util import dataio, timeutil

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

  def __init__(self, datasets, record_type, record_units, record_aggregation_type, data_points):
    self.record_type = record_type
    self.record_units = record_units
    self.record_aggregation_type = record_aggregation_type
    self.data_points = data_points

    self.datasets = datasets
    self.buckets = sorted(list(datasets.keys()))
    self.min_buckets = min(self.buckets)
    self.max_buckets = max(self.buckets)

    self.stats = {b: common.DataMetrics.get_stats(
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
    self.ax.set_ylabel("Average {} per split".format(self.record_type))

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
    all_error_bars = []
    for b in self.buckets:
      outliers_below = self.stats[b]['percentiles'][self._outermost_interval[0]]
      outliers_above = self.stats[b]['percentiles'][self._outermost_interval[1]]
      outliers = [v for v in self.datasets[b] \
                    if not outliers_below <= v <= outliers_above]
      out = plt.scatter([b] * len(outliers), outliers,
                        s = 50, c = 'tab:gray', alpha = 0.1)
      for i, [low, high] in enumerate(self._order_intervals):
        below_median = self.stats[b]['median'] - self.stats[b]['percentiles'][low]
        above_median = self.stats[b]['percentiles'][high] - self.stats[b]['median']
        eb = plt.errorbar(b, self.stats[b]['median'],
                          yerr = np.array([below_median, above_median]).reshape(2, -1),
                          linewidth = 4 + 2 * i,
                          color = 'tab:blue', alpha = 0.4, antialiased = True)
        all_error_bars.append(eb)
    
    y_positioner = common.YPositioner(y_start = 1.00 - 2 * self._text_spacing_factor,
                                      y_spacing = self._text_spacing_factor)
    gmtp = common.GraphMultiTextPrinter(ylim = self.ylim, y_positioner = y_positioner,
                                        horizontalalignment = 'left',
                                        verticalalignment = 'bottom')
    
    self.show_period_guide(gmtp, num_days = 365.25, label = 'YEARLY')
    self.show_period_guide(gmtp, num_days = 182.63, label = 'HALFYEARLY')
    self.show_period_guide(gmtp, num_days = 91.31, label = 'QUARTERLY')
    self.show_period_guide(gmtp, num_days = 30.44, label = 'MONTHLY')
    self.show_period_guide(gmtp, num_days = 7, label = 'WEEKLY')

    y_positioner = common.YPositioner(y_start = 1.00 - 2 * self._text_spacing_factor,
                                      y_spacing = self._text_spacing_factor)
    gmtp = common.GraphMultiTextPrinter(ylim = self.ylim, y_positioner = y_positioner,
                                        horizontalalignment = 'right',
                                        verticalalignment = 'bottom')
    gmtp.plot_annotation(s = 'Total Points: {}'.format(self.data_points),
                          x = 0.99 * self.max_buckets)
    
    self.ax.legend(handles = [out] + all_error_bars[-len(self._order_intervals) : ],
                    labels = ["Outliers"] \
                                + ["Middle {}%".format(oi[1] - oi[0]) \
                                      for oi in self._order_intervals],
                    loc = 'lower right')

    if save:
      save_filename = "TUNING_{}_{}_{}.png".format(self.min_buckets, self.max_buckets,
                                                    self.record_type)
      self.show_or_save(show = show, save_filename = save_filename)
    else:
      self.show_or_save(show = show)