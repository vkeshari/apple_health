import numpy as np
from pathlib import Path
from matplotlib import pyplot as plt

import params as par
from . import common
from util import dataio
from util import timeutil

class Histogram:
  _resolution = tuple([7.2, 7.2])
  _subfolder = Path('hist')
  _dio = dataio.DataIO()

  _record_to_xmin = {}
  _record_to_xmax = {}
  _record_to_num_bins = {}
  _record_to_text_precision = {}
  for rhl in par.RecordHistogramLimits.RECORD_HISTOGRAM_LIMITS:
    record_type = rhl.record
    _record_to_xmin[record_type] = rhl.xmin
    _record_to_xmax[record_type] = rhl.xmax
    _record_to_num_bins[record_type] = rhl.num_bins
    _record_to_text_precision[record_type] = rhl.text_precision

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
  
  def annotate_average(self, plt, value, ymax, stat_height, stat_precision):
    plt.axvline(x = value, ymax = stat_height,
                linestyle = '--', color = 'grey', alpha = 1.0)
    plt.text(x = value, y = stat_height * ymax, alpha = 0.8,
              s = ("Avg: {v:." + str(stat_precision) + "f}").format(v = value),
              horizontalalignment = 'left', verticalalignment = 'bottom')
  
  def annotate_percentile(self, plt, p, value, ymax, stat_height, stat_precision):
    plt.axvline(x = value, ymax = stat_height,
                linestyle = ':', color = 'grey', alpha = 0.8)
    plt.text(x = value, y = stat_height * ymax, alpha = 0.8,
              s = ("p{p}: {v:." + str(stat_precision) + "f}") \
                      .format(p = p, v = value),
              horizontalalignment = 'left', verticalalignment = 'bottom')
  
  def annotate_graph(self, data_series, percentiles, ymax, stat_precision,
                      show_average = False, show_percentiles = False):
    data_stats = common.DataMetrics.get_stats(data_series, include_percentiles = percentiles)
    data_series_average = data_stats['average']

    stat_height = 0.97
    percentiles_less_than_average = [p for p in percentiles \
                                        if data_stats['percentiles'][p] < data_series_average]
    percentiles_more_than_average = [p for p in percentiles \
                                        if data_stats['percentiles'][p] >= data_series_average]
    if show_percentiles:
      for p in percentiles_less_than_average:
        stat_height -= 0.03
        self.annotate_percentile(plt, p, data_stats['percentiles'][p],
                                  ymax, stat_height, stat_precision)
    if show_average:
      stat_height -= 0.03
      self.annotate_average(plt, data_series_average, ymax, stat_height, stat_precision)
    if show_percentiles:
      for p in percentiles_more_than_average:
        stat_height -= 0.03
        self.annotate_percentile(plt, p, data_stats['percentiles'][p],
                                  ymax, stat_height, stat_precision)

  
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
    data_hist_vals, _ = np.histogram(data_series,
                                      bins = np.linspace(self.get_xmin(), self.get_xmax(),
                                                          self.get_bin_count() + 1))
    ymax = int(max(data_hist_vals) * 1.25)
    ax.set_ylim(0, ymax)

    ax.hist(data_series, bins = self.get_bin_count(), \
          range = (self.get_xmin(), self.get_xmax()),
          alpha = 0.8)
    
    self.annotate_graph(data_series, percentiles = self._percentiles, ymax = ymax,
                        stat_precision = self.get_text_precision(),
                        show_average = True, show_percentiles = True)

    self.show_or_save(fig, show = show, save = save)
