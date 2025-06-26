import numpy as np
from pathlib import Path
from matplotlib import pyplot as plt

import params as par
from . import common
from util import dataio, paramutil, timeutil

class ComparisonGraph:
  _resolution = tuple([7.2, 7.2])
  _text_spacing_factor = 0.03
  _subfolder = Path('comparison') / timeutil.Timestamp.get_timestamp()
  _dio = dataio.DataIO(par.DataParams)
  _record_to_min, _record_to_max = paramutil.RecordLineGraphProperties.get_y_bounds()

  _period_to_alphas = {par.AggregationPeriod.DAILY: 0.1,
                        par.AggregationPeriod.WEEKLY: 0.3,
                        par.AggregationPeriod.MONTHLY: 0.5}

  @classmethod
  def get_bounds(cls, r):
    return cls._record_to_min[r], cls._record_to_max[r]

  def __init__(self, xy_vals, record_types, record_units, record_aggregation_types,
                period, period_delta, correlations):
    self.record_type_y = record_types[0]
    self.record_type_x = record_types[1]

    self.record_unit_y = record_units[0]
    self.record_unit_x = record_units[1]

    self.record_aggregation_type_y = record_aggregation_types[0]
    self.record_aggregation_type_x = record_aggregation_types[1]

    assert len(xy_vals[0]) == len(xy_vals[1])
    self.total_points = len(xy_vals[0])
    self.y_vals = xy_vals[0]
    self.x_vals = xy_vals[1]

    self.period = period
    self.period_delta = period_delta

    self.correlations = correlations

    self.fig, self.ax = plt.subplots(figsize = self._resolution)
    self.init_plot()

  def get_graph_title(self):
    title_text_1 = "{} ({}) vs {} ({})".format(self.record_type_y.name, self.record_unit_y,
                                                self.record_type_x.name, self.record_unit_x)
    
    aggregation_period_text = common.GraphText.get_period_text(self.period)
    if self.period == par.AggregationPeriod.DAILY:
      title_text_2 = "Daily values separated by {} {}".format(self.period_delta,
                                                              aggregation_period_text)
    elif self.period in [par.AggregationPeriod.WEEKLY,
                    par.AggregationPeriod.MONTHLY,
                    par.AggregationPeriod.QUARTERLY]:
      title_text_2 = "{} Averages separated by {} {}".format(
                        common.GraphText.pretty_enum(self.period, capitalize = True),
                                                      self.period_delta, aggregation_period_text)
    
    title_text_3 = "{} to {}".format(self._dio.data_params.START_DATE,
                                      self._dio.data_params.END_DATE)
    
    return "{}\n{}\n{}".format(title_text_1, title_text_2, title_text_3)
  
  def init_plot(self):
    title_text = self.get_graph_title()
    self.ax.set_title(title_text)
    if self.period_delta == 0:
      x_label = self.record_type_x.name
    else:
      x_label = "{} ({} {} later)".format(self.record_type_x.name, self.period_delta,
                                          common.GraphText.get_period_text(self.period))
    self.ax.set_xlabel(x_label)
    self.ax.set_ylabel(self.record_type_y.name)

    xmin, xmax = self.get_bounds(self.record_type_x)
    self.ax.set_xlim(xmin, xmax)
    xticks_major, xticks_minor = common.GraphTickSpacer.get_ticks(xmin, xmax)
    self.ax.set_xticks(xticks_major)
    self.ax.set_xticks(xticks_minor, minor = True)

    ymin, ymax = self.get_bounds(self.record_type_y)
    self.ax.set_ylim(ymin, ymax)
    yticks_major, yticks_minor = common.GraphTickSpacer.get_ticks(ymin, ymax)
    self.ax.set_yticks(yticks_major)
    self.ax.set_yticks(yticks_minor, minor = True)

    self.ax.grid(True, which = 'minor', axis = 'both', alpha = 0.3)
    self.ax.grid(True, which = 'major', axis = 'both', alpha = 0.5)

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
    plt.scatter(self.x_vals, self.y_vals,
                color = 'tab:gray', alpha = self._period_to_alphas[self.period])
    
    xlims = self.get_bounds(self.record_type_x)
    ylims = self.get_bounds(self.record_type_y)
    y_positioner = common.YPositioner(y_start = 1.00 - self._text_spacing_factor,
                                      y_spacing = self._text_spacing_factor)
    gmtp = common.GraphMultiTextPrinter(xlims, ylims, y_positioner, x_position = 0.99,
                                        horizontalalignment = 'right',
                                        verticalalignment = 'bottom')
    gmtp.plot_annotation(s = "Total Points: {}".format(self.total_points))
    gmtp.newline()
    gmtp.plot_annotation(s = "Correlations:")
    for m in self.correlations:
      gmtp.plot_annotation(s = "{}: {:.2f}".format(m.name, self.correlations[m]))

    if save:
      save_filename = "{}_{}_{}_{}.png".format(self.period.name,
                                            self.period_delta,
                                            self.record_type_y.name,
                                            self.record_type_x.name)
      self.show_or_save(show = show, save_filename = save_filename)
    else:
      self.show_or_save(show = show)
