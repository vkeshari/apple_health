import numpy as np
from dataclasses import dataclass

import params as par

class GraphTitle:

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
  def get_graph_title(cls, record_type, start_date, end_date, record_aggregation_type, period):
    record_aggregation_text = cls.get_aggregation_type_text(record_aggregation_type)
    title_text_1 = "{}".format(record_type)
    if period == par.AggregationPeriod.DAILY:
      title_text_2 = "Daily {}".format(record_aggregation_text)
    elif period in [par.AggregationPeriod.WEEKLY, par.AggregationPeriod.MONTHLY]:
      title_text_2 = "{} Averages of Daily {}".format(period.name.capitalize(),
                                                      record_aggregation_text)
    title_text_3 = "{} to {}".format(start_date, end_date)
    
    return "{} ({})\n{}".format(title_text_1, title_text_2, title_text_3)

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
    return np.get_percentile(data_series, 50)

  @classmethod
  def get_percentiles(cls, data_series, percentiles):
    assert all([0 < p < 100 for p in percentiles])

    data_percentiles = {}
    for p in percentiles:
      data_percentiles[p] = cls.get_percentile(data_series, p)
    
    return data_percentiles
