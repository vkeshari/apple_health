import numpy as np
from fitter import Fitter
from scipy import stats

import params as par

class DataSeriesMetrics:

  @classmethod
  def get_average(cls, data_series):
    return np.average(data_series)

  @classmethod
  def get_std(cls, data_series):
    return np.std(data_series)
  
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
  def get_stats(cls, data_series, include_percentiles, top_values = 1):
    assert len(data_series) >= top_values
    data_series = sorted(data_series)

    data_stats = {}
    data_stats['average'] = cls.get_average(data_series)
    data_stats['median'] = cls.get_median(data_series)
    data_stats['stdev'] = cls.get_std(data_series)
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
  def get_nsigma_interval(cls, data_series, nsigma = 3):
    assert nsigma >= 1

    av = cls.get_average(data_series)
    std = cls.get_std(data_series)

    return av - nsigma * std, av + nsigma * std
  
  @classmethod
  def get_best_fit(cls, data_series, num_best_fits = 10):
    f = Fitter(data_series)
    f.fit()
    return f.summary(Nbest = num_best_fits)


class DataComparisonMetrics:

  @classmethod
  def get_correlations(cls, vals1, vals2):
    assert len(vals1) > 1
    assert len(vals2) > 1
    assert len(vals1) == len(vals2)

    correlations = {}
    corr_pvals = {}
    pearson_corr = stats.pearsonr(vals1, vals2)
    correlations[par.CorrelationType.PEARSON] = pearson_corr.statistic
    corr_pvals[par.CorrelationType.PEARSON] = pearson_corr.pvalue
    correlations[par.CorrelationType.SPEARMAN], corr_pvals[par.CorrelationType.SPEARMAN] = \
        stats.spearmanr(vals1, vals2)
    correlations[par.CorrelationType.KENDALL], corr_pvals[par.CorrelationType.KENDALL] = \
        stats.kendalltau(vals1, vals2)

    return correlations, corr_pvals


class Rescaler:

  def __init__(self, data):
    self.average = np.average(list(data))

    p5 = np.percentile(list(data), 5, method = 'nearest')
    p95 = np.percentile(list(data), 95, method = 'nearest')
    self.spread = max(abs(self.average - p5), abs(p95 - self.average))
  
  def rescale(self, val):
    return (val - self.average) / self.spread
  
  def rescale_all(self, vals):
    return [self.rescale(v) for v in vals]
  
  def backscale(self, val):
    return self.average + val * self.spread
