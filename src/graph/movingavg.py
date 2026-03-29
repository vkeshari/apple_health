import numpy as np
from matplotlib import pyplot as plt
from pathlib import Path

import params as par
from . import common
from util import dataio, datautil, timeutil

class MovingAvgGraph:
  _resolution = tuple([10.8, 7.2])
  _text_spacing_factor = 0.03
  _subfolder = Path('movingavg') / timeutil.Timestamp.get_timestamp()
  _dio = dataio.DataIO(par.DataParams)

  _ypadding_fraction = 0.05
  _light_colors = True

  def __init__(self, moving_avgs, rolling_avgs, overall_avg, rms_errors, use_rolling_avg_for_rms,
                record_type, record_units, record_aggregation_type):
    self.record_type = record_type
    self.record_units = record_units
    self.record_aggregation_type = record_aggregation_type
    
    self.overall_avg = overall_avg
    self.rolling_avgs = rolling_avgs

    self.use_rolling_avg_for_rms = use_rolling_avg_for_rms
    self.rms_errors = rms_errors

    self.moving_avgs = moving_avgs
    self.windows = sorted(self.moving_avgs.keys())

    self.start_date = self._dio.data_params.END_DATE
    self.end_date = self._dio.data_params.START_DATE
    self.min_val = self.overall_avg * 2
    self.max_val = 0
    for n in moving_avgs:
      min_date = min(moving_avgs[n].keys())
      if min_date < self.start_date:
        self.start_date = min_date
      max_date = max(moving_avgs[n].keys())
      if max_date > self.end_date:
        self.end_date = max_date

      min_val = min(moving_avgs[n].values())
      if min_val < self.min_val:
        self.min_val = min_val
      max_val = max(moving_avgs[n].values())
      if max_val > self.max_val:
        self.max_val = max_val

    self.xlims = [self.start_date, self.end_date]
    self.ylims = [self.min_val * (1.0 - self._ypadding_fraction),
                  self.max_val * (1.0 + self._ypadding_fraction)]
    
    self.fig, self.ax = plt.subplots(figsize = self._resolution)
    self.init_plot()
  
  def init_plot(self):
    title_text = common.GraphText.get_graph_title(self.record_type, self.record_units,
                                                  self.start_date,
                                                  self.end_date,
                                                  self.record_aggregation_type,
                                                  period = par.AggregationPeriod.DAILY)
    title_text = title_text + '\n' + "Moving Averages by Window Size in weeks"
    self.ax.set_title(title_text)
    self.ax.set_xlabel("Window Size (weeks)")
    self.ax.set_ylabel("{}: Moving Averages ({})".format(self.record_type.name,
                                                          self.record_units))

    self.ax.set_xlim(*self.xlims)
    self.ax.grid(True, which = 'minor', axis = 'x', alpha = 0.3)
    self.ax.grid(True, which = 'major', axis = 'x', alpha = 0.5)

    self.ax.set_ylim(*self.ylims)
    yticks_major, yticks_minor = common.GraphTickSpacer.get_ticks(*self.ylims)
    self.ax.set_yticks(yticks_major)
    self.ax.set_yticks(yticks_minor, minor = True)
    self.ax.grid(True, which = 'minor', axis = 'y', alpha = 0.3)
    self.ax.grid(True, which = 'major', axis = 'y', alpha = 0.5)

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
    graphs = []

    xs, ys = zip(*self.rolling_avgs.items())
    rolling_avg_plot = plt.plot(xs, ys, linewidth = 4, alpha = 0.6, antialiased = True,
                                    label = "Rolling Average")
    graphs.append(rolling_avg_plot[0])

    for p in self.windows:
      xs, ys = zip(*self.moving_avgs[p].items())
      if self._light_colors:
        linealpha = 0.4
      else:
        linealpha = 0.5
      weekly_avg_plot = plt.plot(xs, ys, linewidth = 4, alpha = linealpha, antialiased = True,
                                      label = "Moving Average: {} Week".format(p))
      graphs.append(weekly_avg_plot[0])
    
    self.show_value_guide(self.overall_avg, alpha = 0.5)
    self.show_value_guide(self.overall_avg * 0.95, alpha = 0.3)
    self.show_value_guide(self.overall_avg * 1.05, alpha = 0.3)
    self.show_value_guide(self.overall_avg * 0.9, alpha = 0.3)
    self.show_value_guide(self.overall_avg * 1.1, alpha = 0.3)

    ap = common.AnnotationPrinter(alpha = 0.6,
                                  horizontalalignment = 'left', verticalalignment = 'bottom')
    ap.plot_annotation(x = self.start_date, y = self.overall_avg, s = "Avg")
    ap.plot_annotation(x = self.start_date, y = self.overall_avg * 0.95, s = "Avg +/- 5%")
    ap.plot_annotation(x = self.start_date, y = self.overall_avg * 1.05, s = "Avg +/- 5%")
    ap.plot_annotation(x = self.start_date, y = self.overall_avg * 0.9, s = "Avg +/- 10%")
    ap.plot_annotation(x = self.start_date, y = self.overall_avg * 1.1, s = "Avg +/- 10%")
    
    self.ax.legend(handles = graphs, loc = 'upper left')

    y_positioner = common.YPositioner(y_start = 1.00 - self._text_spacing_factor,
                                      y_spacing = self._text_spacing_factor)
    gmtp = common.GraphMultiTextPrinter(xlims = self.xlims, ylims = self.ylims,
                                        y_positioner = y_positioner,
                                        x_position = 0.99,
                                        horizontalalignment = 'right',
                                        verticalalignment = 'bottom')
    
    if self.use_rolling_avg_for_rms:
      vs_avg_text = "Rolling Avg"
    else:
      vs_avg_text = "Overall Avg"
    gmtp.plot_annotation(s = 'RMS Error vs {}'.format(vs_avg_text))
    for n in self.rms_errors:
      gmtp.plot_annotation(s = '{} Week: {:.2f} {}'.format(n, self.rms_errors[n],
                                                            self.record_units))

    if save:
      windows_text = '_'.join([str(n) for n in self.windows])
      save_filename = "MOVINGAVG_{}_{}_{}.png".format(self.use_rolling_avg_for_rms,
                                                      self.record_type.name, windows_text)
      self.show_or_save(show = show, save_filename = save_filename)
    else:
      self.show_or_save(show = show)