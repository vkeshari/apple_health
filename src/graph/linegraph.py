import math
import numpy as np
from pathlib import Path
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle

import params as par
from . import common
from util import dataio, paramutil, timeutil

class LineGraph:
  _resolution = tuple([10.8, 7.2])
  _text_spacing_factor = 0.03
  _subfolder = Path('line') / timeutil.Timestamp.get_timestamp()
  _dio = dataio.DataIO(par.DataParams)
  _record_to_text_precision = paramutil.RecordHistogramProperties.get_text_precision()

  _largest_periods = [par.AggregationPeriod.QUARTERLY,
                      par.AggregationPeriod.MONTHLY,
                      par.AggregationPeriod.WEEKLY,
                      par.AggregationPeriod.DAILY]
  
  _show_points = par.AggregationPeriod.QUARTERLY
  _show_lines = par.AggregationPeriod.MONTHLY
  _show_intervals = par.AggregationPeriod.QUARTERLY
  _interval_percentiles = [[25, 75], [10, 90], [5, 95]]
  
  @classmethod
  def get_largest_period(cls, periods):
    for p in cls._largest_periods:
      if p in periods:
        return p

  @classmethod
  def get_smallest_period(cls, periods):
    for p in cls._largest_periods[ : : -1]:
      if p in periods:
        return p

  def __init__(self, datasets, record_type, record_units, record_aggregation_type,
                start_date, end_date):
    self.record_type = record_type
    self.record_units = record_units
    self.record_aggregation_type = record_aggregation_type

    self.dates = {}
    self.data_series = {}
    for period in datasets:
      self.dates[period] = list(sorted(datasets[period].keys()))
      self.data_series[period] = [datasets[period][d] for d in self.dates[period]]
    self.largest_period = self.get_largest_period(datasets.keys())
    self.smallest_period = self.get_smallest_period(datasets.keys())

    actual_start_date = max(min(self.dates[self.largest_period]), start_date)
    self.start_date = timeutil.CalendarUtil.get_period_start_date(actual_start_date,
                                                                  self.largest_period)
    actual_end_date = min(max(self.dates[self.largest_period]), end_date)
    self.end_date = timeutil.CalendarUtil.get_next_period_start_date(actual_end_date,
                                                                      self.largest_period)

    self.ylim = math.ceil(np.average(self.data_series[self.smallest_period]) * 2)
    self.fig, self.ax = plt.subplots(figsize = self._resolution)

    self.init_plot()
  
  def init_plot(self):
    title_text = common.GraphText.get_graph_title(self.record_type, self.record_units,
                                                  self._dio.data_params.START_DATE,
                                                  self._dio.data_params.END_DATE,
                                                  self.record_aggregation_type)
    self.ax.set_title(title_text)
    self.ax.set_xlabel("Date")
    self.ax.set_ylabel(self.record_type)

    self.ax.set_xlim(self.start_date, self.end_date)
    self.ax.grid(True, which = 'major', axis = 'x', alpha = 0.5)

    self.ax.set_ylim(0, self.ylim)
    yticks_major, yticks_minor = common.GraphTickSpacer.get_ticks(0, self.ylim)
    self.ax.set_yticks(yticks_major)
    self.ax.set_yticks(yticks_minor, minor = True)
    self.ax.grid(True, which = 'minor', axis = 'y', alpha = 0.3)
    self.ax.grid(True, which = 'major', axis = 'y', alpha = 0.5)
  
  def get_text_precision(self):
    return self._record_to_text_precision[self.record_type]

  def plot_interval(self, d, patch_width, low, high, interval_handles):
    p = self.ax.add_patch(Rectangle((d, low), height = high - low, width = patch_width,
                                    facecolor = 'tab:blue', alpha = 0.3, fill = True))
    interval_handles.append(p)

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
    
    all_handles = []
    interval_handles = []
    labels = []
    for period in self.dates:
      if period == par.AggregationPeriod.DAILY:
        s = plt.scatter(self.dates[period], self.data_series[period],
                        s = 50, c = 'tab:gray', alpha = 0.1)
        all_handles.append(s)
        labels.append('Daily Values')
        
        if self._show_intervals:
          interval_data = {}
          for i, d in enumerate(self.dates[period]):
            start_of_interval = timeutil.CalendarUtil.get_period_start_date(
                                d, period = self._show_intervals)
            if start_of_interval not in interval_data:
              interval_data[start_of_interval] = []
            interval_data[start_of_interval].append(self.data_series[period][i])
          for d in interval_data:
            patch_width = \
                timeutil.CalendarUtil.get_next_period(d, period = self._show_intervals) - d
            all_percentiles = np.array(self._interval_percentiles).flatten()
            percentiles = \
                common.DataMetrics.get_percentiles(interval_data[d],
                                                    percentiles = all_percentiles)
            for p_low, p_high in self._interval_percentiles:
              self.plot_interval(d, patch_width,
                                  percentiles[p_low], percentiles[p_high],
                                  interval_handles)
      
      if self._show_lines and period == self._show_lines:
        xs = [timeutil.CalendarUtil.get_middle_of_period(d, period) for d in self.dates[period]]
        l = plt.plot(xs, self.data_series[period],
                      linewidth = 3, color = 'tab:blue', alpha = 0.8, antialiased = True)
        all_handles.append(l[0])
        labels.append("{} Averages".format(common.GraphText.pretty_enum(period, capitalize = True)))
      if self._show_points and period == self._show_points:
        xs = [timeutil.CalendarUtil.get_middle_of_period(d, period) for d in self.dates[period]]
        p = plt.plot(xs, self.data_series[period],
                      marker = "o", markersize = 10, linewidth = 0,
                      color = 'tab:blue', alpha = 0.9, antialiased = True)
        all_handles.append(p[0])
        labels.append("{} Averages".format(common.GraphText.pretty_enum(period, capitalize = True)))
      
    if interval_handles:
      all_handles.append(interval_handles[0])
      labels.append("{} Intervals".format(common.GraphText.pretty_enum(self._show_intervals,
                                                                      capitalize = True)))
      
    self.ax.legend(handles = all_handles, labels = labels, loc = 'upper right')

    if save:
      save_filename = "{}_{}_{}.png".format(self.record_type,
                                                self.start_date.strftime("%Y%m%d"),
                                                self.end_date.strftime("%Y%m%d"))
      self.show_or_save(show = show, save_filename = save_filename)
    else:
      self.show_or_save(show = show)
