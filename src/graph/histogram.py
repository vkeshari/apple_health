import numpy as np
from pathlib import Path
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle

import params as par
from . import common
from util import dataio
from util import timeutil

class Histogram:
  _resolution = tuple([7.2, 7.2])
  _major_x_ticks_spacing = 5
  _text_spacing_factor = 0.03
  _subfolder = Path('hist')
  _dio = dataio.DataIO()

  _record_to_xmin = {}
  _record_to_xmax = {}
  _record_to_num_bins = {}
  _record_to_text_precision = {}
  for rhp in par.RecordHistogramParams.RECORD_HISTOGRAM_PARAMS:
    record_type = rhp.record
    _record_to_xmin[record_type] = rhp.xmin
    _record_to_xmax[record_type] = rhp.xmax
    assert rhp.num_bins % _major_x_ticks_spacing == 0
    _record_to_num_bins[record_type] = rhp.num_bins
    _record_to_text_precision[record_type] = rhp.text_precision

  def __init__(self, record_type, record_units, record_aggregation_type,
                start_date, end_date, period):
    self.record_type = record_type
    self.record_units = record_units
    self.record_aggregation_type = record_aggregation_type
    self.start_date = start_date
    self.end_date = end_date
    self.period = period
  
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

  def get_top_values_count(self):
    if self.period == par.AggregationPeriod.DAILY:
      return 10
    elif self.period == par.AggregationPeriod.WEEKLY:
      return 5
    elif self.period == par.AggregationPeriod.MONTHLY:
      return 3
  

  def show_average(self, value, gmtp, value_format, annotate = False):
    plt.axvline(x = value, ymax = gmtp.get_y_current(),
                linestyle = '--', color = 'grey', alpha = 1.0)
    if annotate:
      gmtp.plot_annotation(s = ("Avg: " + value_format).format(v = value), x = value)
  
  def show_percentile(self, p, value, gmtp, value_format, annotate = False):
    plt.axvline(x = value, ymax = gmtp.get_y_current(),
                linestyle = ':', color = 'grey', alpha = 1.0)
    if annotate:
      gmtp.plot_annotation(s = ("p{p}: " + value_format).format(p = p, v = value), x = value)
  
  def show_interval(self, ax, ylim, x_low, x_high):
    ax.add_patch(Rectangle((x_low, 0), height = ylim, width = x_high - x_low,
                            linewidth = 0, alpha = 0.2, fill = True))

  def show_stats(self, ax, data_series, percentiles, ylim,
                  show_total_count = False, show_average = False, annotate_average = False,
                  show_percentiles = False, annotate_percentiles = False,
                  show_normal_stats = False, show_order_stats = False,
                  show_top_values = False, show_intervals = False):
    xlim = self.get_xmax()
    stat_precision = self.get_text_precision()

    data_stats = common.DataMetrics.get_stats(data_series, include_percentiles = percentiles,
                                              top_values = self.get_top_values_count())
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
    gmtp = common.GraphMultiTextPrinter(ylim = ylim, y_positioner = y_positioner,
                                        horizontalalignment = 'left',
                                        verticalalignment = 'bottom')
    
    value_format = common.GraphText.get_text_precision_format(stat_precision, variable = 'v')
    if show_percentiles:
      for p in percentiles_less_than_average:
        self.show_percentile(p, data_stats['percentiles'][p], gmtp, value_format,
                              annotate = annotate_percentiles)
    if show_average:
      self.show_average(data_stats['average'], gmtp, value_format,
                        annotate = annotate_average)
    if show_percentiles:
      for p in percentiles_more_than_average:
        self.show_percentile(p, data_stats['percentiles'][p], gmtp, value_format,
                              annotate = annotate_percentiles)
    
    if show_intervals:
      self.show_interval(ax, ylim, mid50_low, mid50_high)
      self.show_interval(ax, ylim, mid80_low, mid80_high)
      self.show_interval(ax, ylim, mid90_low, mid90_high)
    
    y_positioner = common.YPositioner(y_start = 1.00 - self._text_spacing_factor,
                                      y_spacing = self._text_spacing_factor)
    gmtp = common.GraphMultiTextPrinter(ylim = ylim, y_positioner = y_positioner,
                                        x = 0.99 * xlim,
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
      top_values_count = self.get_top_values_count()
      gmtp.newline()
      gmtp.plot_annotation(s = "Top {} values".format(top_values_count))
      
      top_n_values = data_stats['top_values'][-top_values_count : ]
      for i in range(top_values_count):
        gmtp.plot_annotation(s = value_format.format(v = top_n_values[-(i + 1)]))

  def show_or_save(self, fig, show = False, save_filename = None):
    if show:
      fig.tight_layout()
      plt.show()
    if save_filename:
      save_file = self._dio.get_graph_filepath(self._subfolder / save_filename)
      fig.tight_layout()
      save_file.parent.mkdir(exist_ok = True, parents = True)
      fig.savefig(save_file)
      print ("Graph written to: {}".format(save_file))
      plt.close()


class SingleSeriesHistogram(Histogram):

  _subfolder = Histogram._subfolder / 'singleseries'
  _percentiles = [50, 75, 90, 95]

  def __init__(self, data, record_type, record_units, record_aggregation_type,
                start_date, end_date, period):
    Histogram.__init__(self, record_type, record_units, record_aggregation_type,
                        start_date, end_date, period)
    self.data = data

    actual_start_date = max(min(data.keys()), start_date)
    self.start_date = timeutil.CalendarUtil.get_period_start_date(actual_start_date, period)
    actual_end_date = min(max(data.keys()), end_date)
    self.end_date = timeutil.CalendarUtil.get_next_period_start_date(actual_end_date, period)
  
  def plot(self, show = False, save = False):
    fig, ax = plt.subplots(figsize = self._resolution)
    title_text = common.GraphText.get_graph_title(self.record_type, self.record_units,
                                                  self.start_date, self.end_date,
                                                  self.record_aggregation_type, self.period)
    ax.set_title(title_text)
    ax.set_xlabel(self.record_type)
    ax.set_ylabel("No. of {}".format(common.GraphText.get_period_text(self.period)))

    data_series = list(sorted(self.data.values()))

    ax.set_xlim(self.get_xmin(), self.get_xmax())

    hist_bins = self.get_hist_bins()
    ax.set_xticks(hist_bins[ : : self._major_x_ticks_spacing])
    ax.set_xticks(hist_bins, minor = True)
    ax.grid(True, which = 'both', axis = 'x', alpha = 0.3)

    ylim = self.get_ylim(data_series)
    ax.set_ylim(0, ylim)
    yticks_major, yticks_minor = common.GraphTickSpacer.get_ticks(0, ylim)
    ax.set_yticks(yticks_major)
    ax.set_yticks(yticks_minor, minor = True)
    ax.grid(True, which = 'minor', axis = 'y', alpha = 0.3)
    ax.grid(True, which = 'major', axis = 'y', alpha = 0.5)

    ax.hist(data_series, bins = self.get_bin_count(),
            range = (self.get_xmin(), self.get_xmax()),
            alpha = 0.8)
    
    self.show_stats(ax, data_series, percentiles = self._percentiles, ylim = ylim,
                    show_average = True, annotate_average = True,
                    show_percentiles = True, annotate_percentiles = True,
                    show_total_count = True, show_normal_stats = True, show_order_stats = True,
                    show_top_values = True, show_intervals = True)
    if save:
      save_filename = "{}_{}_{}_{}.png".format(self.record_type, self.period.name,
                                                self.start_date.strftime("%Y%m%d"),
                                                self.end_date.strftime("%Y%m%d"))
      self.show_or_save(fig, show = show, save_filename = save_filename)
    else:
      self.show_or_save(fig, show = show)
