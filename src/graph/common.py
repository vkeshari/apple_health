import numpy as np
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


class GraphText:

  @classmethod
  def get_period_text(cls, period):
    if period == par.AggregationPeriod.DAILY:
      return "Days"
    elif period == par.AggregationPeriod.WEEKLY:
      return "Weeks"
    elif period == par.AggregationPeriod.MONTHLY:
      return "Months"

  @classmethod
  def get_aggregation_type_text(cls, record_aggregation_type):
    if record_aggregation_type == par.AggregateType.SUM:
      return 'Totals'
    elif record_aggregation_type == par.AggregateType.MEDIAN:
      return 'Medians'
    elif record_aggregation_type == par.AggregateType.AVERAGE:
      return 'Averages'

  @classmethod
  def get_graph_title(cls, record_type, record_unit, start_date, end_date,
                      record_aggregation_type, period, bucketing_name = ''):
    record_aggregation_text = cls.get_aggregation_type_text(record_aggregation_type)
    title_text_1 = "{} ({})".format(record_type, record_unit)
    if period == par.AggregationPeriod.DAILY:
      title_text_2 = "Daily {}".format(record_aggregation_text)
    elif period in [par.AggregationPeriod.WEEKLY, par.AggregationPeriod.MONTHLY]:
      title_text_2 = "{} Averages of Daily {}".format(period.name.capitalize(),
                                                      record_aggregation_text)
    title_text_3 = "{} to {}".format(start_date, end_date)
    if bucketing_name:
      title_text_3 += " (split {})".format(bucketing_name)
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

class GraphTickSpacer:
  
  @classmethod
  def get_ticks(cls, lower, upper):
    difference = upper - lower
    if difference <= 10:
      return list(range(lower, upper)), []
    elif difference <= 20:
      return list(range(lower, upper, 2)), list(range(lower, upper))
    elif difference <= 50:
      return list(range(lower, upper, 5)), list(range(lower, upper))
    elif difference <= 100:
      return list(range(lower, upper, 10)), list(range(lower, upper, 2))
    elif difference <= 200:
      return list(range(lower, upper, 20)), list(range(lower, upper, 5))
    elif difference <= 500:
      return list(range(lower, upper, 50)), list(range(lower, upper, 10))
    elif difference <= 1000:
      return list(range(lower, upper, 100)), list(range(lower, upper, 20))
    else:
      return list(range(lower, upper, 100)), []
