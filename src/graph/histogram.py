import numpy as np
from pathlib import Path
from matplotlib import colors as mcolors
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle

import params as par
from . import common
from util import dataio, datautil, paramutil, timeutil

class Histogram:
  _resolution = tuple([7.2, 7.2])
  _major_x_ticks_spacing = 5
  _text_spacing_factor = 0.03
  _subfolder = Path('hist')
  _dio = dataio.DataIO(par.DataParams)

  _record_to_xmin, _record_to_xmax, _record_to_num_bins = \
      paramutil.RecordHistogramProperties.get_x_bounds(_major_x_ticks_spacing)
  _record_to_text_precision = paramutil.RecordProperties.get_text_precision()

  def __init__(self, record_type, record_units, record_aggregation_type,
                start_date, end_date, period):
    self.record_type = record_type
    self.record_units = record_units
    self.record_aggregation_type = record_aggregation_type
    self.start_date = start_date
    self.end_date = end_date
    self.period = period

    self.fig, self.ax = plt.subplots(figsize = self._resolution)
  
  def get_xmin(self):
    return self._record_to_xmin[self.record_type]

  def get_xmax(self):
    return self._record_to_xmax[self.record_type]
  
  def get_bin_count(self):
    return self._record_to_num_bins[self.record_type]
  
  def get_text_precision(self):
    return self._record_to_text_precision[self.record_type]
  
  def get_hist_bins(self):
    return np.linspace(self.get_xmin(), self.get_xmax(), self.get_bin_count() + 1)

  def get_ylim(self, data_series):
    data_hist_vals, _ = np.histogram(data_series, bins = self.get_hist_bins())
    return int(max(data_hist_vals) * 1.25)
  
  def init_plot(self, title_text, ylim):
    self.ax.set_title(title_text)
    self.ax.set_xlabel(self.record_type.name)
    self.ax.set_ylabel("No. of {}".format(common.GraphText.get_period_text(self.period)))

    self.ax.set_xlim(self.get_xmin(), self.get_xmax())

    hist_bins = self.get_hist_bins()
    self.ax.set_xticks(hist_bins[ : : self._major_x_ticks_spacing])
    self.ax.set_xticks(hist_bins, minor = True)
    self.ax.grid(True, which = 'both', axis = 'x', alpha = 0.3)

    self.ax.set_ylim(0, ylim)
    yticks_major, yticks_minor = common.GraphTickSpacer.get_ticks(0, ylim)
    self.ax.set_yticks(yticks_major)
    self.ax.set_yticks(yticks_minor, minor = True)
    self.ax.grid(True, which = 'minor', axis = 'y', alpha = 0.3)
    self.ax.grid(True, which = 'major', axis = 'y', alpha = 0.5)
  

  def show_average(self, value, gmtp, value_format, color, annotate = False):
    plt.axvline(x = value, ymax = gmtp.get_y_current(),
                color = color, linestyle = '--', alpha = 1.0)
    if annotate:
      gmtp.plot_annotation(
          s = ("Avg: " + value_format).format(v = value),
          x_position = common.GraphPosition.get_relative_position(value,
                                                                  self.get_xmin(),
                                                                  self.get_xmax()))
  
  def show_percentile(self, p, value, gmtp, value_format, color, annotate = False):
    plt.axvline(x = value, ymax = gmtp.get_y_current(),
                color = color, linestyle = ':', alpha = 1.0)
    if annotate:
      gmtp.plot_annotation(
          s = ("p{p}: " + value_format).format(p = p, v = value),
          x_position = common.GraphPosition.get_relative_position(value,
                                                                  self.get_xmin(),
                                                                  self.get_xmax()))
  
  def show_interval(self, ylim, color, x_low, x_high):
    self.ax.add_patch(Rectangle((x_low, 0), height = ylim, width = x_high - x_low,
                                linewidth = 0, alpha = 0.2, fill = True, facecolor = color))

  def show_stats(self, data_series, percentiles, ylim, color = None,
                  show_total_count = False, show_average = False, annotate_average = False,
                  show_percentiles = False, annotate_percentiles = False,
                  show_normal_stats = False, show_order_stats = False,
                  show_top_values = False, show_intervals = False):
    xlim = self.get_xmax()
    stat_precision = self.get_text_precision()

    data_stats = datautil.DataSeriesMetrics.get_stats(
                    data_series, include_percentiles = percentiles,
                    top_values = common.GraphText.get_top_values_count(self.period))
    (mid50_low, mid50_high) = data_stats['middle_50']
    (mid80_low, mid80_high) = data_stats['middle_80']
    (mid90_low, mid90_high) = data_stats['middle_90']

    if show_percentiles:
      percentiles_less_than_average = [p for p in percentiles \
                                          if data_stats['percentiles'][p] < data_stats['average']]
      percentiles_more_than_average = [p for p in percentiles \
                                          if data_stats['percentiles'][p] >= data_stats['average']]
    
    y_positioner = common.YPositioner(y_start = 1.00 - self._text_spacing_factor,
                                      y_spacing = self._text_spacing_factor)
    gmtp = common.GraphMultiTextPrinter(xlims = [self.get_xmin(), self.get_xmax()],
                                        ylims = [0, ylim],
                                        y_positioner = y_positioner,
                                        horizontalalignment = 'left',
                                        verticalalignment = 'bottom')
    
    value_format = common.GraphText.get_text_precision_format(stat_precision, variable = 'v')
    if show_percentiles:
      for p in percentiles_less_than_average:
        self.show_percentile(p, data_stats['percentiles'][p], gmtp, value_format, color,
                              annotate = annotate_percentiles)
    if show_average:
      self.show_average(data_stats['average'], gmtp, value_format, color,
                        annotate = annotate_average)
    if show_percentiles:
      for p in percentiles_more_than_average:
        self.show_percentile(p, data_stats['percentiles'][p], gmtp, value_format, color,
                              annotate = annotate_percentiles)
    
    if show_intervals:
      self.show_interval(ylim, color, mid50_low, mid50_high)
      self.show_interval(ylim, color, mid80_low, mid80_high)
      self.show_interval(ylim, color, mid90_low, mid90_high)
    
    y_positioner = common.YPositioner(y_start = 1.00 - self._text_spacing_factor,
                                      y_spacing = self._text_spacing_factor)
    gmtp = common.GraphMultiTextPrinter(xlims = [self.get_xmin(), self.get_xmax()],
                                        ylims = [0, ylim],
                                        y_positioner = y_positioner,
                                        x_position = 0.99,
                                        horizontalalignment = 'right',
                                        verticalalignment = 'bottom')
    
    if show_total_count:
      gmtp.plot_annotation(s = "Total points: {v:d}".format(v = len(data_series)))
    
    if show_normal_stats:
      gmtp.newline()
      gmtp.plot_annotation(s = ("Mean: " + value_format).format(v = data_stats['average']))
      gmtp.plot_annotation(s = ("Std Dev: " + value_format).format(v = data_stats['stdev']))
      gmtp.plot_annotation(s = "Skew: {v:.1f}".format(v = data_stats['skew']))
      gmtp.plot_annotation(s = "Kurtosis: {v:.1f}".format(v = data_stats['kurtosis']))
    
    if show_order_stats:
      gmtp.newline()
      gmtp.plot_annotation(s = ("Median: " + value_format).format(v = data_stats['median']))
      
      range_format = common.GraphText.get_range_precision_format(stat_precision,
                                                                  variables = ['v1', 'v2'])
      gmtp.plot_annotation(s = ("Middle 50%: " + range_format) \
                                  .format(v1 = mid50_low, v2 = mid50_high))
      gmtp.plot_annotation(s = ("Middle 80%: " + range_format) \
                                  .format(v1 = mid80_low, v2 = mid80_high))
      gmtp.plot_annotation(s = ("Middle 90%: " + range_format) \
                                  .format(v1 = mid90_low, v2 = mid90_high))
    
    if show_top_values:
      top_values_count = common.GraphText.get_top_values_count(self.period)
      gmtp.newline()
      gmtp.plot_annotation(s = "Top {} values".format(top_values_count))
      
      top_n_values = data_stats['top_values'][-top_values_count : ]
      for i in range(top_values_count):
        gmtp.plot_annotation(s = value_format.format(v = top_n_values[-(i + 1)]))

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


class SingleSeriesHistogram(Histogram):

  _subfolder = Histogram._subfolder / 'singleseries' / timeutil.Timestamp.get_timestamp()
  _percentiles = [50, 75, 90, 95]
  _color = 'tab:blue'

  def __init__(self, data, record_type, record_units, record_aggregation_type,
                start_date, end_date, period):
    Histogram.__init__(self, record_type, record_units, record_aggregation_type,
                        start_date, end_date, period)
    self.data_series = list(sorted(data.values()))
    self.ylim = self.get_ylim(self.data_series)

    actual_start_date = max(min(data.keys()), start_date)
    self.start_date = timeutil.CalendarUtil.get_period_start_date(actual_start_date, period)
    actual_end_date = min(max(data.keys()), end_date)
    self.end_date = timeutil.CalendarUtil.get_next_period_start_date(actual_end_date, period)
    
    self.init_plot()
  
  def init_plot(self):
    title_text = common.GraphText.get_graph_title(self.record_type, self.record_units,
                                                  self.start_date, self.end_date,
                                                  self.record_aggregation_type,
                                                  period = self.period)
    Histogram.init_plot(self, title_text, self.ylim)

  def plot(self, show = False, save = False):
    self.ax.hist(self.data_series, bins = self.get_bin_count(),
                  range = (self.get_xmin(), self.get_xmax()),
                  color = self._color, alpha = 0.8)
    self.show_stats(self.data_series, percentiles = self._percentiles,
                    ylim = self.ylim, color = self._color,
                    show_average = True, annotate_average = True,
                    show_percentiles = True, annotate_percentiles = True,
                    show_total_count = True, show_normal_stats = True, show_order_stats = True,
                    show_top_values = True, show_intervals = True)
    if save:
      save_filename = "{}_{}_{}_{}.png".format(self.period.name, self.record_type.name,
                                                self.start_date.strftime("%Y%m%d"),
                                                self.end_date.strftime("%Y%m%d"))
      self.show_or_save(show = show, save_filename = save_filename)
    else:
      self.show_or_save(show = show)


class MultiSeriesHistogram(Histogram):

  _subfolder = Histogram._subfolder / 'multiseries' / timeutil.Timestamp.get_timestamp()
  _percentiles = []
  _colors = list(mcolors.TABLEAU_COLORS.keys())

  def __init__(self, bucketing, datasets, record_type, record_units, record_aggregation_type,
                start_date, end_date, period):
    Histogram.__init__(self, record_type, record_units, record_aggregation_type,
                        start_date, end_date, period)
    self.bucketing = bucketing
    self.labels = list(datasets.keys())
    self.data_series = [sorted(datasets[l].values()) for l in self.labels]
    self.ylim = max([self.get_ylim(ds) for ds in self.data_series])

    actual_start_date = max(min([min(data.keys()) for data in datasets.values()]), start_date)
    self.start_date = timeutil.CalendarUtil.get_period_start_date(actual_start_date, period)
    actual_end_date = min(max([max(data.keys()) for data in datasets.values()]), end_date)
    self.end_date = timeutil.CalendarUtil.get_next_period_start_date(actual_end_date, period)
    
    self.init_plot()
  
  def init_plot(self):
    title_text = common.GraphText.get_graph_title(self.record_type, self.record_units,
                                                  self.start_date, self.end_date,
                                                  self.record_aggregation_type,
                                                  period = self.period,
                                                  bucketing = self.bucketing)
    Histogram.init_plot(self, title_text, self.ylim)

  def plot(self, show = False, save = False):
    hists = []
    for i, ds in enumerate(self.data_series):
      c = self._colors[i]
      _, _, hist = self.ax.hist(ds, bins = self.get_bin_count(),
                                range = (self.get_xmin(), self.get_xmax()),
                                color = c, alpha = 0.3)
      hists.append(hist)
      self.show_stats(ds, percentiles = self._percentiles, ylim = self.ylim,
                      color = c, show_average = True)
    self.ax.legend(handles = hists, labels = self.labels, loc = 'upper right')
    
    if save:
      save_filename = "{}_{}_{}_{}_{}_{}.png".format(self.bucketing.name, len(self.data_series),
                                                  self.period.name, self.record_type.name,
                                                  self.start_date.strftime("%Y%m%d"),
                                                  self.end_date.strftime("%Y%m%d"))
      self.show_or_save(show = show, save_filename = save_filename)
    else:
      self.show_or_save(show = show)
