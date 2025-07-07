from pathlib import Path
from matplotlib import colors as mcolors
from matplotlib import pyplot as plt

import params as par
from . import common
from util import dataio, paramutil, timeutil

class ClusteringGraph:
  _resolution = tuple([7.2, 7.2])
  _text_spacing_factor = 0.03
  _subfolder = Path('clustering') / timeutil.Timestamp.get_timestamp()
  _dio = dataio.DataIO(par.DataParams)

  _period_to_alphas = {par.AggregationPeriod.DAILY: 0.1,
                        par.AggregationPeriod.WEEKLY: 0.3,
                        par.AggregationPeriod.MONTHLY: 0.5}
  _record_to_text_precision = paramutil.RecordProperties.get_text_precision()
  _axis_percent_padding = 20
  _plot_pvals = False
  _fit_line = par.RecordComparisonParams.FIT_LINE
  _colors = list(mcolors.TABLEAU_COLORS.keys())

  def __init__(self, xy_vals, dates, groups, record_types, group_by_record, record_unit, period):
    self.total_points = len(xy_vals)
    self.x_vals = xy_vals[ : , 0]
    self.y_vals = xy_vals[ : , 1]

    self.x_bounds = common.GraphBounds.get_bounds_with_padding(self.x_vals,
                                                                self._axis_percent_padding)
    self.y_bounds = common.GraphBounds.get_bounds_with_padding(self.y_vals,
                                                                self._axis_percent_padding)

    assert len(xy_vals) == len(dates)
    self.dates = dates

    assert len(xy_vals) == len(groups)
    self.groups = groups
    self.group_ids = sorted(list(set(self.groups)))
    assert len(self.group_ids) <= 10

    self.record_types = record_types
    assert group_by_record in self.record_types
    self.group_by_record = group_by_record

    self.record_unit = record_unit
    self.period = period

    self.fig, self.ax = plt.subplots(figsize = self._resolution)
    self.init_plot()

  def get_graph_title(self):
    period_text = common.GraphText.pretty_enum(self.period, capitalize = True)
    title_1 = "Dimensionailty Reduction on {} data".format(period_text)
    title_2 = "Grouped by {} ({})".format(self.group_by_record.name, self.record_unit)

    return title_1 + '\n' + title_2
  
  def init_plot(self):
    title_text = self.get_graph_title()
    self.ax.set_title(title_text)

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
    scatters = []
    for gid_index, gid in enumerate(self.group_ids):
      indices = [i for i, g in enumerate(self.groups) if g == gid]
      x_vals = self.x_vals[indices]
      y_vals = self.y_vals[indices]
      s = plt.scatter(x_vals, y_vals,
                      color = self._colors[gid_index],
                      alpha = self._period_to_alphas[self.period])
      scatters.append(s)
    
    group_id_label_format = \
        "Up to " + \
            common.GraphText.get_text_precision_format(
                self._record_to_text_precision[self.group_by_record])
    group_id_labels = [group_id_label_format.format(v = gid) for gid in self.group_ids]
    plt.legend(handles = scatters, labels = group_id_labels, loc = 'lower left',
                title = "{} ({})".format(self.group_by_record.name, self.record_unit),
                alignment = 'left')

    if save:
      save_filename = "{}_{}.png".format(self.period.name, self.group_by_record.name)
      self.show_or_save(show = show, save_filename = save_filename)
    else:
      self.show_or_save(show = show)
