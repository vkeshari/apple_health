import numpy as np
from dataclasses import dataclass
from matplotlib import pyplot as plt

import params as par

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
    title_text_1 = "{} ({})".format(record_type.name, record_unit)
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

class GraphPosition:

  @classmethod
  def get_relative_position(cls, val, min, max):
    return (val - min) / (max - min)
  
  @classmethod
  def get_absolute_value(cls, pos, min, max):
    return min + pos * (max - min)

class GraphMultiTextPrinter:

  def __init__(self, xlims, ylims, y_positioner, x_position = None,
                horizontalalignment = 'center', verticalalignment = 'center'):
    self.xlims = xlims
    self.ylims = ylims

    self.y_positioner = y_positioner
    self.x_position = x_position

    self.annotation_printer = AnnotationPrinter(horizontalalignment = horizontalalignment,
                                                verticalalignment = verticalalignment)
  
  def get_y_current(self):
    return self.y_positioner.y_current

  def get_y_position(self):
    return GraphPosition.get_absolute_value(self.get_y_current(), self.ylims[0], self.ylims[1])
  
  def get_x_position(self, x_position):
    return GraphPosition.get_absolute_value(x_position, self.xlims[0], self.xlims[1])
  
  def newline(self):
    self.y_positioner.next()
  
  def newlines(self, n):
    for _ in range(n):
      self.newline()
  
  def plot_annotation(self, s, x_position = None):
    assert x_position or self.x_position

    if x_position:
      self.annotation_printer.plot_annotation(x = self.get_x_position(x_position),
                                              y = self.get_y_position(),
                                              s = s)
    elif self.x_position:
      self.annotation_printer.plot_annotation(x = self.get_x_position(self.x_position),
                                              y = self.get_y_position(),
                                              s = s)
    self.newline()

class GraphBounds:

  @classmethod
  def get_bounds_with_padding(cls, data_series, percent_padding):
    minval = min(data_series)
    maxval = max(data_series)
    diff = maxval - minval
    padding = percent_padding * diff / 100.0
    return minval - padding, maxval + padding

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
