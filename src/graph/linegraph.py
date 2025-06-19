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

    if save:
      save_filename = "{}_{}_{}.png".format(self.record_type,
                                                self.start_date.strftime("%Y%m%d"),
                                                self.end_date.strftime("%Y%m%d"))
      self.show_or_save(show = show, save_filename = save_filename)
    else:
      self.show_or_save(show = show)
