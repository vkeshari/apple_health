from matplotlib import pyplot as plt
from pathlib import Path

import params as par
from . import common
from util import dataio, timeutil

class RMSErrorGraph:
  _resolution = tuple([10.8, 7.2])
  _text_spacing_factor = 0.03
  _subfolder = Path('rmserror') / timeutil.Timestamp.get_timestamp()
  _dio = dataio.DataIO(par.DataParams)

  _ypadding_fraction = 0.05

  _period_guide_weeks = {'MONTHLY': 4.33,
                          'SIXWEEKLY': 6,
                          'TWOMONTHLY': 8.67,
                          'QUARTERLY': 13,
                          'FOURMONTHLY': 17.33,
                          'HALFYEARLY': 26,
                          'NINEMONTHLY': 39,
                          'YEARLY': 52}

  def __init__(self, overall_avg, rms_errors, use_rolling_avg_for_rms,
                record_type, record_units, record_aggregation_type):
    self.record_type = record_type
    self.record_units = record_units
    self.record_aggregation_type = record_aggregation_type

    self.overall_avg = overall_avg
    self.use_rolling_avg_for_rms = use_rolling_avg_for_rms
    self.rms_errors = rms_errors
    self.windows = sorted(self.rms_errors.keys())

    self.xlims = [0, self.windows[-1]]
    self.ylims = [0, max(self.rms_errors.values()) * (1.0 + self._ypadding_fraction)]
    
    self.fig, self.ax = plt.subplots(figsize = self._resolution)
    self.init_plot()
  
  def init_plot(self):
    title_text = common.GraphText.get_graph_title(self.record_type, self.record_units,
                                                  self._dio.data_params.START_DATE,
                                                  self._dio.data_params.END_DATE,
                                                  self.record_aggregation_type,
                                                  period = par.AggregationPeriod.DAILY)
    title_text = title_text + '\n' + "RMS Error of Moving Averages by Window Size in weeks"
    self.ax.set_title(title_text)
    self.ax.set_xlabel("Window Size (weeks)")
    self.ax.set_ylabel("{}: RMS Error of Moving Averages ({})".format(self.record_type.name,
                                                                      self.record_units))

    self.ax.set_xlim(*self.xlims)
    self.ax.grid(True, which = 'minor', axis = 'x', alpha = 0.3)
    self.ax.grid(True, which = 'major', axis = 'x', alpha = 0.5)

    self.ax.set_ylim(*self.ylims)
    yticks_major, yticks_minor = common.GraphTickSpacer.get_ticks(*self.ylims)
    self.ax.set_yticks(yticks_major)
    self.ax.set_yticks(yticks_minor, minor = True)
    self.ax.grid(True, which = 'minor', axis = 'y', alpha = 0.3)
    self.ax.grid(True, which = 'major', axis = 'y', alpha = 0.5)

  def show_value_guide(self, val, alpha = 0.5):
    plt.axhline(y = val, linestyle = ':', linewidth = 2, color = 'gray', alpha = alpha)

  def show_period_guide(self, gmtp, num_weeks = 1, label = ''):
    if num_weeks <= self.xlims[0] or num_weeks >= self.xlims[1]:
      return
    
    plt.axvline(x = num_weeks, ymax = gmtp.get_y_current(),
                linestyle = ':', linewidth = 2, color = 'gray', alpha = 0.5)
    gmtp.plot_annotation(
        s = label,
        x_position = common.GraphPosition.get_relative_position(num_weeks, *self.xlims))

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
    graphs = []

    xs, ys = zip(*self.rms_errors.items())
    rmserror_plot = plt.plot(xs, ys, linewidth = 3, alpha = 0.7, antialiased = True,
                              label = "RMS Error of Moving Averages")
    graphs.append(rmserror_plot[0])
    
    self.show_value_guide(self.overall_avg * 0.01, alpha = 0.5)
    self.show_value_guide(self.overall_avg * 0.02, alpha = 0.5)
    self.show_value_guide(self.overall_avg * 0.03, alpha = 0.5)
    self.show_value_guide(self.overall_avg * 0.05, alpha = 0.5)
    self.show_value_guide(self.overall_avg * 0.1, alpha = 0.5)

    ap = common.AnnotationPrinter(alpha = 0.6,
                                  horizontalalignment = 'left', verticalalignment = 'bottom')
    ap.plot_annotation(x = self.windows[0], y = self.overall_avg * 0.01, s = "1% of AVG")
    ap.plot_annotation(x = self.windows[0], y = self.overall_avg * 0.02, s = "2% of AVG")
    ap.plot_annotation(x = self.windows[0], y = self.overall_avg * 0.03, s = "3% of AVG")
    ap.plot_annotation(x = self.windows[0], y = self.overall_avg * 0.05, s = "5% of AVG")
    ap.plot_annotation(x = self.windows[0], y = self.overall_avg * 0.1, s = "10% of AVG")
    
    y_positioner = common.YPositioner(y_start = 1.00 - 2 * self._text_spacing_factor,
                                      y_spacing = self._text_spacing_factor)
    gmtp = common.GraphMultiTextPrinter(xlims = self.xlims, ylims = self.ylims,
                                        y_positioner = y_positioner,
                                        horizontalalignment = 'left',
                                        verticalalignment = 'bottom')
    
    for p, w in self._period_guide_weeks.items():
      self.show_period_guide(gmtp, num_weeks = w, label = p)
    
    self.ax.legend(handles = graphs, loc = 'upper right')

    if save:
      windows_text = str(self.windows[0]) + '_' + str(self.windows[-1])
      save_filename = "RMSERROR_{}_{}_{}.png".format(self.use_rolling_avg_for_rms,
                                                      self.record_type.name, windows_text)
      self.show_or_save(show = show, save_filename = save_filename)
    else:
      self.show_or_save(show = show)
