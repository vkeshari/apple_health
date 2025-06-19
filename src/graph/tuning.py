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

  def __init__(self, record_type, datasets, record_units, record_aggregation_type, data_points):
    self.record_type = record_type
    self.record_units = record_units
    self.record_aggregation_type = record_aggregation_type
    self.data_points = data_points

    self.datasets = datasets
    self.buckets = sorted(list(datasets.keys()))
    self.min_buckets = min(self.buckets)
    self.max_buckets = max(self.buckets)

    self.averages = {b: np.average(datasets[b]) for b in self.buckets}
    self.stds = {b: np.std(datasets[b]) for b in self.buckets}
    self.p5s = {b: np.percentile(datasets[b], 5, method = 'nearest') for b in self.buckets}
    self.p95s = {b: np.percentile(datasets[b], 95, method = 'nearest') for b in self.buckets}

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

    self.ylim = round(np.average(list(self.averages.values())) * 2)
    self.ax.set_ylim(0, self.ylim)
    yticks_major, yticks_minor = common.GraphTickSpacer.get_ticks(0, self.ylim)
    self.ax.set_yticks(yticks_major)
    self.ax.set_yticks(yticks_minor, minor = True)
    self.ax.grid(True, which = 'minor', axis = 'y', alpha = 0.3)
    self.ax.grid(True, which = 'major', axis = 'y', alpha = 0.5)

  def show_period_guide(self, gmtp, num_days = 1, label = ''):
    period_line = self.data_points / num_days
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
    pts = plt.plot(self.buckets, list(self.averages.values()),
                    marker = "o", markersize = 10, linewidth = 0,
                    color = 'tab:blue', alpha = 0.9, antialiased = True)
    all_error_bars = []
    for b in self.buckets:
      plt.scatter([b] * len(self.datasets[b]), self.datasets[b],
                  s = 50, c = 'tab:gray', alpha = 0.1)
      std = plt.errorbar(b, self.averages[b], yerr = self.stds[b],
                    linewidth = 8, capsize = 6, capthick = 2,
                    color = 'tab:blue', alpha = 0.5, antialiased = True)
      all_error_bars.append(std)
      mid90 = plt.errorbar(b, self.averages[b],
                    yerr = np.array([self.averages[b] - self.p5s[b],
                                      self.p95s[b] - self.averages[b]]) \
                              .reshape(2, -1),
                    linewidth = 4, capsize = 3, capthick = 1,
                    color = 'tab:blue', alpha = 0.5, antialiased = True)
      all_error_bars.append(mid90)
    
    y_positioner = common.YPositioner(y_start = 1.00 - 2 * self._text_spacing_factor,
                                      y_spacing = self._text_spacing_factor)
    gmtp = common.GraphMultiTextPrinter(ylim = self.ylim, y_positioner = y_positioner,
                                        horizontalalignment = 'left',
                                        verticalalignment = 'bottom')
    
    self.show_period_guide(gmtp, num_days = 365.25, label = 'YEARLY')
    self.show_period_guide(gmtp, num_days = 182.63, label = 'HALFYEARLY')
    self.show_period_guide(gmtp, num_days = 91.31, label = 'QUARTERLY')
    self.show_period_guide(gmtp, num_days = 30.44, label = 'MONTHLY')

    y_positioner = common.YPositioner(y_start = 1.00 - 2 * self._text_spacing_factor,
                                      y_spacing = self._text_spacing_factor)
    gmtp = common.GraphMultiTextPrinter(ylim = self.ylim, y_positioner = y_positioner,
                                        horizontalalignment = 'right',
                                        verticalalignment = 'bottom')
    gmtp.plot_annotation(s = 'Total Points: {}'.format(self.data_points),
                          x = 0.99 * self.max_buckets)
    
    self.ax.legend(handles = [pts[0]] + all_error_bars[-2 : ],
                    labels = ['Avg of Avgs', 'Std Dev', 'Middle 90%'],
                    loc = 'lower right')


    if save:
      save_filename = "TUNING_{}_{}_{}.png".format(self.min_buckets, self.max_buckets,
                                                    self.record_type)
      self.show_or_save(show = show, save_filename = save_filename)
    else:
      self.show_or_save(show = show)