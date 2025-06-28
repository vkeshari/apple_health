import numpy as np
from pathlib import Path
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit

import params as par
from . import common
from util import dataio, paramutil, timeutil

class ComparisonGraph:
  _resolution = tuple([7.2, 7.2])
  _text_spacing_factor = 0.03
  _subfolder = Path('comparison') / timeutil.Timestamp.get_timestamp()
  _dio = dataio.DataIO(par.DataParams)

  _period_to_alphas = {par.AggregationPeriod.DAILY: 0.1,
                        par.AggregationPeriod.WEEKLY: 0.3,
                        par.AggregationPeriod.MONTHLY: 0.5}
  _axis_percent_padding = 20
  _plot_pvals = False
  _fit_line = par.RecordComparisonParams.FIT_LINE

  @classmethod
  def line_fn(cls, x, m, c):
    return m * x + c

  def __init__(self, xy_vals, record_types, record_units, record_aggregation_types,
                record_val_types, period, period_delta, correlations, correlation_pvals):
    self.record_type_x = record_types[0]
    self.record_type_y = record_types[1]

    self.record_unit_x = record_units[0]
    self.record_unit_y = record_units[1]

    self.record_aggregation_type_x = record_aggregation_types[0]
    self.record_aggregation_type_y = record_aggregation_types[1]

    self.record_val_type_x = record_val_types[0]
    self.record_val_type_y = record_val_types[1]

    assert len(xy_vals[0]) == len(xy_vals[1])
    self.total_points = len(xy_vals[0])
    self.x_vals = xy_vals[0]
    self.y_vals = xy_vals[1]

    self.x_bounds = common.GraphBounds.get_bounds_with_padding(self.x_vals,
                                                                self._axis_percent_padding)
    self.y_bounds = common.GraphBounds.get_bounds_with_padding(self.y_vals,
                                                                self._axis_percent_padding)

    self.period = period
    self.period_delta = period_delta

    self.correlations = correlations
    self.correlation_pvals = correlation_pvals

    self.fig, self.ax = plt.subplots(figsize = self._resolution)
    self.init_plot()

  def get_record_names(self):
    x_name = self.record_type_x.name
    if self.record_val_type_x == par.ValueType.DELTA:
      x_name += ' Deltas'
    y_name = self.record_type_y.name
    if self.record_val_type_y == par.ValueType.DELTA:
      y_name += ' Deltas'
    
    return x_name, y_name
  
  def get_record_filename_chunks(self):
    x_name = self.record_type_x.name
    if self.record_val_type_x == par.ValueType.DELTA:
      x_name = 'Delta' + x_name
    y_name = self.record_type_y.name
    if self.record_val_type_y == par.ValueType.DELTA:
      y_name = 'Delta' + y_name
    
    return x_name, y_name


  def get_graph_title(self):
    x_label, y_label = self.get_record_names()
    title_text_1 = "{} ({}) vs {} ({})".format(y_label, self.record_unit_y,
                                                x_label, self.record_unit_x)
    
    aggregation_period_text = common.GraphText.get_period_text(self.period)
    if self.period == par.AggregationPeriod.DAILY:
      title_text_2 = "Daily Values"
    elif self.period in [par.AggregationPeriod.WEEKLY,
                    par.AggregationPeriod.MONTHLY,
                    par.AggregationPeriod.QUARTERLY]:
      title_text_2 = "{} Averages".format(
                        common.GraphText.pretty_enum(self.period, capitalize = True))
    if self.period_delta > 0:
      title_text_2 += " separated by {} {}".format(self.period_delta, aggregation_period_text)
    
    title_text_3 = "{} to {}".format(self._dio.data_params.START_DATE,
                                      self._dio.data_params.END_DATE)
    
    return "{}\n{}\n{}".format(title_text_1, title_text_2, title_text_3)
  
  def init_plot(self):
    title_text = self.get_graph_title()
    self.ax.set_title(title_text)

    x_label, y_label = self.get_record_names()
    if self.period_delta > 0:
      y_label += " ({} {} later)".format(self.period_delta,
                                          common.GraphText.get_period_text(self.period))
    
    self.ax.set_xlabel(x_label)
    self.ax.set_ylabel(y_label)

    self.ax.set_xlim(*self.x_bounds)
    self.ax.set_ylim(*self.y_bounds)

    self.ax.grid(True, which = 'major', axis = 'both', alpha = 0.5)
    self.ax.grid(True, which = 'minor', axis = 'both', alpha = 0.3)

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
    
    y_positioner = common.YPositioner(y_start = 1.00 - self._text_spacing_factor,
                                      y_spacing = self._text_spacing_factor)
    gmtp = common.GraphMultiTextPrinter(self.x_bounds, self.y_bounds, y_positioner,
                                        x_position = 0.99,
                                        horizontalalignment = 'right',
                                        verticalalignment = 'bottom')
    gmtp.plot_annotation(s = "Total Points: {}".format(self.total_points))
    gmtp.newline()
    gmtp.plot_annotation(s = "Correlations")
    for m in self.correlations:
      gmtp.plot_annotation(s = "{}: {:.2f}".format(m.name, self.correlations[m]))
    if self._plot_pvals:
      gmtp.newline()
      gmtp.plot_annotation(s = "Correlation P-Vals")
      for m in self.correlations:
        gmtp.plot_annotation(s = "{}: {:.2f}".format(m.name, self.correlation_pvals[m]))
    
    if self._fit_line:
      (m, c), _ = curve_fit(self.line_fn, self.x_vals, self.y_vals)
      self.ax.plot(self.x_bounds, [self.line_fn(x, m, c) for x in self.x_bounds],
                    color = 'tab:blue', linewidth = 5, alpha = 0.5)
      gmtp.newline()
      gmtp.plot_annotation(s = "Fit Line Slope: {:.2f}".format(m))

    if save:
      x_filename_chunk, y_filename_chunk = self.get_record_filename_chunks()
      save_filename = "{}_{}_{}_{}.png".format(self.period.name,
                                            self.period_delta,
                                            y_filename_chunk,
                                            x_filename_chunk)
      self.show_or_save(show = show, save_filename = save_filename)
    else:
      self.show_or_save(show = show)
