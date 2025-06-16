from pathlib import Path
from matplotlib import pyplot as plt

import params as par
from util import dataio

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

  def __init__(self, data, record_type, record_units, record_aggregation_type,
                start_date, end_date, period):
    Histogram.__init__(self, record_type, record_units, record_aggregation_type,
                        start_date, end_date, period)
    self.data = data
    self.start_date = max(min(data.keys()), start_date)
    self.end_date = min(max(data.keys()), end_date)
  
  def plot(self, show = False, save = False):
    fig, ax = plt.subplots(figsize = self._resolution)

    if self.record_aggregation_type == par.AggregateType.SUM:
      record_aggregation_text = 'Totals'
    elif self.record_aggregation_type == par.AggregateType.MEDIAN:
      record_aggregation_text = 'Medians'
    elif self.record_aggregation_type == par.AggregateType.AVERAGE:
      record_aggregation_text = 'Averages'

    title_text_1 = "{}".format(self.record_type)
    if self.period == par.AggregationPeriod.DAILY:
      title_text_2 = "Daily {}".format(record_aggregation_text)
    elif self.period in [par.AggregationPeriod.WEEKLY, par.AggregationPeriod.MONTHLY]:
      title_text_2 = "{} Averages of Daily {}".format(self.period.name.capitalize(),
                                                      record_aggregation_text)
    title_text_3 = "{} to {}".format(self.start_date, self.end_date)
    
    title_text = "{}\n{}\n{}".format(title_text_1, title_text_2, title_text_3)
    ax.set_title(title_text)

    self.show_or_save(fig, show = show, save = save)
