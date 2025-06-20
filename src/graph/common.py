import numpy as np
from dataclasses import dataclass
from matplotlib import pyplot as plt
from scipy import stats

import params as par

class DataMetrics:

  @classmethod
  def get_average(cls, data_series):
    return np.average(data_series)
  
  @classmethod
  def get_percentile(cls, data_series, p):
    assert 0 < p < 100

    return np.percentile(data_series, p, method = 'nearest')

  @classmethod
  def get_median(cls, data_series):
    return cls.get_percentile(data_series, 50)

  @classmethod
  def get_percentiles(cls, data_series, percentiles):
    assert all([0 < p < 100 for p in percentiles])

    data_percentiles = {}
    for p in percentiles:
      data_percentiles[p] = cls.get_percentile(data_series, p)
    
    return data_percentiles
  
  @classmethod
  def get_stats(cls, data_series, include_percentiles, top_values):
    assert len(data_series) >= top_values
    data_series = sorted(data_series)

    data_stats = {}
    data_stats['average'] = cls.get_average(data_series)
    data_stats['median'] = cls.get_median(data_series)
    data_stats['stdev'] = np.std(data_series)
    data_stats['skew'] = stats.skew(data_series)
    data_stats['kurtosis'] = stats.kurtosis(data_series)
    data_stats['top_values'] = data_series[-top_values : ]

    percentiles_to_measure = set([5, 10, 25, 50, 75, 90, 95]) | set(include_percentiles)
    percentiles = cls.get_percentiles(data_series, percentiles_to_measure)

    data_stats['percentiles'] = {}
    for p in percentiles:
      data_stats['percentiles'][p] = percentiles[p]
    data_stats['middle_50'] = tuple([percentiles[25], percentiles[75]])
    data_stats['middle_80'] = tuple([percentiles[10], percentiles[90]])
    data_stats['middle_90'] = tuple([percentiles[5], percentiles[95]])

    return data_stats

  @classmethod
  def get_top_values_count(cls, period):
    if period == par.AggregationPeriod.DAILY:
      return 10
    elif period == par.AggregationPeriod.WEEKLY:
      return 5
    elif period == par.AggregationPeriod.MONTHLY:
      return 3
    elif period == par.AggregationPeriod.QUARTERLY:
      return 2


class GraphText:

  @classmethod
  def pretty_enum(cls, enum_val, capitalize = False):
    enum_name = enum_val.name.replace('_', ' ').lower()
    if capitalize:
      return enum_name.capitalize()
    else:
      return enum_name

  @classmethod
  def get_period_text(cls, period):
    if period == par.AggregationPeriod.DAILY:
      return "Days"
    elif period == par.AggregationPeriod.WEEKLY:
      return "Weeks"
    elif period == par.AggregationPeriod.MONTHLY:
      return "Months"
    elif period == par.AggregationPeriod.QUARTERLY:
      return "Quarters"

  @classmethod
  def get_aggregation_type_text(cls, record_aggregation_type):
    if record_aggregation_type == par.AggregateType.SUM:
      return 'Totals'
    elif record_aggregation_type == par.AggregateType.MEDIAN:
      return 'Medians'
    elif record_aggregation_type == par.AggregateType.AVERAGE:
      return 'Averages'

  @classmethod
  def get_graph_title(cls, record_type, record_unit, start_date, end_date, record_aggregation_type,
                      period = par.AggregationPeriod.DAILY, bucketing = None):
    record_aggregation_text = cls.get_aggregation_type_text(record_aggregation_type)
    title_text_1 = "{} ({})".format(record_type, record_unit)
    if period == par.AggregationPeriod.DAILY:
      title_text_2 = "Daily {}".format(record_aggregation_text)
    elif period in [par.AggregationPeriod.WEEKLY,
                    par.AggregationPeriod.MONTHLY,
                    par.AggregationPeriod.QUARTERLY]:
      title_text_2 = "{} Averages of Daily {}".format(cls.pretty_enum(period, capitalize = True),
                                                      record_aggregation_text)
    title_text_3 = "{} to {}".format(start_date, end_date)
    if bucketing:
      title_text_3 += " (split {})".format(cls.pretty_enum(bucketing))
    return "{}: {}\n{}".format(title_text_1, title_text_2, title_text_3)
  
  @classmethod
  def get_text_precision_format(cls, precision, variable = 'v'):
    return "{" + variable + ":." + str(precision) + "f}"
  
  @classmethod
  def get_range_precision_format(cls, precision, variables = ['v1', 'v2']):
    return "{" + variables[0] + ":." + str(precision) + "f}" + " to " \
              + "{" + variables[1] + ":." + str(precision) + "f}"

class AnnotationPrinter:

  def __init__(self, fontsize = 'medium', alpha = 0.8,
                horizontalalignment = 'center', verticalalignment = 'center'):
    self.fontsize = fontsize
    self.alpha = alpha
    self.horizontalalignment = horizontalalignment
    self.verticalalignment = verticalalignment
  
  def plot_annotation(self, x, y, s):
    plt.text(x = x, y = y, s = s,
              alpha = self.alpha, fontsize = self.fontsize,
              horizontalalignment = self.horizontalalignment,
              verticalalignment = self.verticalalignment)

class YPositioner:

  def __init__(self, y_start, y_spacing):
    self.y_start = y_start
    self.y_spacing = y_spacing
    self.y_current = y_start
  
  def next(self):
    self.y_current -= self.y_spacing

class GraphMultiTextPrinter:

  def __init__(self, ylim, y_positioner, x = None,
                horizontalalignment = 'center', verticalalignment = 'center'):
    self.ylim = ylim
    self.y_positioner = y_positioner
    self.x = x
    self.annotation_printer = AnnotationPrinter(horizontalalignment = horizontalalignment,
                                                verticalalignment = verticalalignment)
  
  def get_y_current(self):
    return self.y_positioner.y_current

  def get_y_position(self):
    return self.ylim * self.get_y_current()
  
  def newline(self):
    self.y_positioner.next()
  
  def newlines(self, n):
    for _ in range(n):
      self.newline()
  
  def plot_annotation(self, s, x = None):
    assert x or self.x

    if x:
      self.annotation_printer.plot_annotation(x = x, y = self.get_y_position(), s = s)
    elif self.x:
      self.annotation_printer.plot_annotation(x = self.x, y = self.get_y_position(), s = s)
    self.newline()

@dataclass
class GraphTickSpacing:
  upper_bound: float
  major_spacing: float
  minor_spacing: float

class GraphTickSpacer:

  # This list must be sorted in ascending order of upper_bound
  _ticks_by_upper_bounds = [
      GraphTickSpacing(1, 0.2, 0.1),
      GraphTickSpacing(5, 1, 0.2),
      GraphTickSpacing(10, 1, 0.5),
      GraphTickSpacing(20, 2, 1),
      GraphTickSpacing(50, 5, 1),
      GraphTickSpacing(100, 10, 2),
      GraphTickSpacing(200, 20, 5),
      GraphTickSpacing(500, 50, 10),
      GraphTickSpacing(1000, 100, 20),
      GraphTickSpacing(2000, 200, 50),
      GraphTickSpacing(5000, 500, 100),
      GraphTickSpacing(10000, 1000, 200),
      GraphTickSpacing(20000, 2000, 500),
      GraphTickSpacing(50000, 5000, 1000),
      GraphTickSpacing(100000, 10000, 2000),
      GraphTickSpacing(1000000, 100000, 20000),
  ]

  last_upper_bound = 0
  for gts in _ticks_by_upper_bounds:
    assert gts.upper_bound > gts.major_spacing > gts.minor_spacing
    assert gts.upper_bound > last_upper_bound
    last_upper_bound = gts.upper_bound
  
  @classmethod
  def get_ticks(cls, lower, upper):
    difference = upper - lower
    for gts in cls._ticks_by_upper_bounds:
      if difference <= gts.upper_bound:
        return np.arange(lower, upper, gts.major_spacing), \
                np.arange(lower, upper, gts.minor_spacing)
