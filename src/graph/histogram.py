from pathlib import Path
from matplotlib import pyplot as plt

from . import common
from util import dataio
from util import timeutil

class Histogram:
  _resolution = tuple([7.2, 7.2])
  _subfolder = Path('hist')
  _dio = dataio.DataIO()

  def __init__(self, record_type, record_units, record_aggregation_type,
                start_date, end_date, period):
    self.record_type = record_type
    self.record_units = record_units
    self.record_aggregation_type = record_aggregation_type
    self.start_date = start_date
    self.end_date = end_date
    self.period = period
  
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
  _percentiles = [10, 20, 50, 80, 90, 95, 99]

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
    title_text = common.GraphTitle.get_graph_title(self.record_type,
                                                    self.start_date, self.end_date,
                                                    self.record_aggregation_type, self.period)
    ax.set_title(title_text)
    ax.set_xlabel(self.record_type)
    ax.set_ylabel("No. of {}".format(common.GraphTitle.get_period_text(self.period)))

    data_series = list(sorted(self.data.values()))
    data_series_average = common.DataMetrics.get_average(data_series)
    data_series_percentiles = common.DataMetrics.get_percentiles(data_series, self._percentiles)

    ax.hist(data_series, bins = max(10, int(len(data_series) / 100)), \
          # range = (750, 2050),
          alpha = 0.8)
    for p in data_series_percentiles:
      plt.axvline(x = data_series_average, linestyle = '--', color = 'grey', alpha = 1.0)
      plt.axvline(x = data_series_percentiles[p], linestyle = ':', color = 'grey', alpha = 0.8)

    self.show_or_save(fig, show = show, save = save)
