import numpy as np
from pathlib import Path
from matplotlib import pyplot as plt

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
  
  def get_top_values_count(self):
    if self.period == par.AggregationPeriod.DAILY:
      return 10
    elif self.period == par.AggregationPeriod.WEEKLY:
      return 5
    elif self.period == par.AggregationPeriod.MONTHLY:
      return 3
  
  def get_yticks(self, ylim):
    if ylim <= 10:
      return list(range(ylim)), []
    elif ylim <= 20:
      return list(range(0, ylim, 2)), list(range(ylim))
    elif ylim <= 50:
      return list(range(0, ylim, 5)), list(range(ylim))
    elif ylim <= 100:
      return list(range(0, ylim, 10)), list(range(0, ylim, 2))
    elif ylim <= 200:
      return list(range(0, ylim, 20)), list(range(0, ylim, 5))
    elif ylim <= 500:
      return list(range(0, ylim, 50)), list(range(0, ylim, 10))
    elif ylim <= 1000:
      return list(range(0, ylim, 100)), list(range(0, ylim, 20))
    else:
      return list(range(0, ylim, 100)), []
  
  def get_text_precision_format(self, precision, variable = 'v'):
    return "{" + variable + ":." + str(precision) + "f}"
  
  def show_average(self, value, ylim, stat_height, stat_precision, annotate = False):
    plt.axvline(x = value, ymax = stat_height,
                linestyle = '--', color = 'grey', alpha = 1.0)
    if annotate:
      value_format = self.get_text_precision_format(stat_precision, variable = 'v')
      plt.text(x = value, y = stat_height * ylim, alpha = 0.8,
                s = ("Avg: " + value_format).format(v = value),
                horizontalalignment = 'left', verticalalignment = 'bottom')
  
  def show_percentile(self, p, value, ylim, stat_height, stat_precision, annotate = False):
    plt.axvline(x = value, ymax = stat_height,
                linestyle = ':', color = 'grey', alpha = 1.0)
    if annotate:
      value_format = self.get_text_precision_format(stat_precision, variable = 'v')
      plt.text(x = value, y = stat_height * ylim, alpha = 0.8,
                s = ("p{p}: " + value_format).format(p = p, v = value),
                horizontalalignment = 'left', verticalalignment = 'bottom')
  
  def show_stats(self, data_series, percentiles, ylim, stat_precision,
                  show_average = False, annotate_average = False,
                  show_percentiles = False, annotate_percentiles = False,
                  show_normal_stats = False, show_order_stats = False, show_top_values = False):
    data_stats = common.DataMetrics.get_stats(data_series, include_percentiles = percentiles,
                                              top_values = self.get_top_values_count())
    data_series_average = data_stats['average']

    if show_percentiles:
      percentiles_less_than_average = [p for p in percentiles \
                                          if data_stats['percentiles'][p] < data_series_average]
      percentiles_more_than_average = [p for p in percentiles \
                                          if data_stats['percentiles'][p] >= data_series_average]
    
    stat_height = 1.00 - self._text_spacing_factor
    if show_percentiles:
      for p in percentiles_less_than_average:
        stat_height -= self._text_spacing_factor
        self.show_percentile(p, data_stats['percentiles'][p],
                              ylim, stat_height, stat_precision,
                              annotate = annotate_percentiles)
    if show_average:
      stat_height -= self._text_spacing_factor
      self.show_average(data_series_average,
                        ylim, stat_height, stat_precision,
                        annotate = annotate_average)
    if show_percentiles:
      for p in percentiles_more_than_average:
        stat_height -= self._text_spacing_factor
        self.show_percentile(p, data_stats['percentiles'][p],
                              ylim, stat_height, stat_precision,
                              annotate = annotate_percentiles)
    
    stat_height = 1.00 - self._text_spacing_factor
    if show_normal_stats:
      pass
    if show_order_stats:
      pass
    if show_top_values:
      pass
  
  def show_or_save(self, fig, show = False, save = False):
    if show:
      fig.tight_layout()
      plt.show()
    if save:
      save_filename = "{}_{}_{}_{}.png".format(self.record_type,
                                                self.period.name,
                                                self.start_date.strftime("%Y%m%d"),
                                                self.end_date.strftime("%Y%m%d"))
      save_file = self._dio.get_graph_filepath(self._subfolder / save_filename)
      fig.tight_layout()
      save_file.parent.mkdir(exist_ok = True, parents = True)
      fig.savefig(save_file)
      print ("Graph written to: {}".format(save_file))
      plt.close()


class SingleSeriesHistogram(Histogram):

  _subfolder = Histogram._subfolder / 'singleseries'
  _percentiles = [50, 90, 95]

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

    hist_bins = np.linspace(self.get_xmin(), self.get_xmax(), self.get_bin_count() + 1)
    ax.set_xticks(hist_bins[ : : self._major_x_ticks_spacing])
    ax.set_xticks(hist_bins, minor = True)
    ax.grid(True, which = 'both', axis = 'x', alpha = 0.3)

    data_hist_vals, _ = np.histogram(data_series, bins = hist_bins)
    ylim = int(max(data_hist_vals) * 1.25)
    ax.set_ylim(0, ylim)
    yticks_major, yticks_minor = self.get_yticks(ylim)
    ax.set_yticks(yticks_major)
    ax.set_yticks(yticks_minor, minor = True)
    ax.grid(True, which = 'minor', axis = 'y', alpha = 0.3)
    ax.grid(True, which = 'major', axis = 'y', alpha = 0.5)

    ax.hist(data_series, bins = self.get_bin_count(), \
            range = (self.get_xmin(), self.get_xmax()),
            alpha = 0.8)
    
    self.show_stats(data_series, percentiles = self._percentiles, ylim = ylim,
                    stat_precision = self.get_text_precision(),
                    show_average = True, annotate_average = True,
                    show_percentiles = True, annotate_percentiles = True,
                    show_normal_stats = True, show_order_stats = True, show_top_values = True)

    self.show_or_save(fig, show = show, save = save)
