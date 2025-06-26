import params as par

class Validator:

  @classmethod
  def validate_filename_suffix_format(cls, suffix):
    if suffix:
      assert suffix[0] == '_'
      assert not suffix[-1] == '_'
  
  @classmethod
  def validate_data_params(cls):
    cls.validate_filename_suffix_format(par.DataParams.FILENAME_SUFFIX)
    assert par.DataParams.END_DATE > par.DataParams.START_DATE
  
  @classmethod
  def validate_graph_dates(cls, graph_start_date, graph_end_date):
    assert graph_start_date >= par.DataParams.START_DATE
    assert graph_end_date <= par.DataParams.END_DATE
    assert graph_start_date < graph_end_date


  @classmethod
  def validate_parse_data(cls):
    if par.ParserParams.WRITE_DATA:
      assert par.ParserParams.PARSE_DATA
    cls.validate_data_params()

  @classmethod
  def validate_aggregate_data(cls):
    cls.validate_data_params()
    assert par.AggregationPeriod.DAILY not in par.AggregatorParams.AGGREGATION_PERIODS

  @classmethod
  def validate_build_graphs(cls):
    cls.validate_data_params()
    cls.validate_graph_dates(par.GraphParams.GRAPH_START_DATE, par.GraphParams.GRAPH_END_DATE)

  @classmethod
  def validate_bucketed_graphs(cls):
    cls.validate_data_params()
    cls.validate_graph_dates(par.BucketedGraphParams.GRAPH_START_DATE,
                              par.BucketedGraphParams.GRAPH_END_DATE)
    
    assert par.AggregationPeriod.MONTHLY not in par.BucketedGraphParams.AGGREGATION_PERIODS
    assert par.AggregationPeriod.QUARTERLY not in par.BucketedGraphParams.AGGREGATION_PERIODS
    
    if par.BucketedGraphParams.BUCKETING == par.BucketingType.RANDOMLY:
      assert 1 < par.BucketedGraphParams.NUM_RANDOM_BUCKETS <= 10

  @classmethod
  def validate_bucket_tuning(cls):
    cls.validate_data_params()

    assert 0 < par.BucketTuningParams.MIN_BUCKETS < par.BucketTuningParams.MAX_BUCKETS
    assert 0 < par.BucketTuningParams.BUCKET_STEP < \
                (par.BucketTuningParams.MAX_BUCKETS - par.BucketTuningParams.MIN_BUCKETS)
    assert 0 < par.BucketTuningParams.NUM_RUNS
  
  @classmethod
  def validate_record_comparison(cls):
    cls.validate_data_params()

    assert par.AggregationPeriod.QUARTERLY not in par.RecordComparisonParams.AGGREGATION_PERIODS
    assert all(0 <= pd for pd in par.RecordComparisonParams.MAX_PERIOD_DELTAS.values())
    assert all(0 < c < 1 for c in par.RecordComparisonParams.MIN_CORRELATIONS.values())


class RecordProperties:

  @classmethod
  def get_record_aggregation_types(cls):
    record_aggregation_types = {}
    for rt in par.RecordParams.RECORD_TYPES:
      record_aggregation_types[rt.record] = rt.aggregation
    return record_aggregation_types

  @classmethod
  def get_record_units(cls):
    record_units = {}
    for rt in par.RecordParams.RECORD_TYPES:
      record_units[rt.record] = rt.unit
    return record_units
  
  @classmethod
  def get_text_precision(cls):
    record_to_text_precision = {}
    for rhp in par.RecordGraphTextParams.RECORD_GRAPH_TEXT_PARAMS:
      record_type = rhp.record
      record_to_text_precision[record_type] = rhp.text_precision

    return record_to_text_precision


class RecordHistogramProperties:

  @classmethod
  def get_x_bounds(cls, major_x_ticks_spacing):
    record_to_xmin = {}
    record_to_xmax = {}
    record_to_num_bins = {}
    for rhp in par.RecordHistogramParams.RECORD_HISTOGRAM_PARAMS:
      record_type = rhp.record
      record_to_xmin[record_type] = rhp.xmin
      record_to_xmax[record_type] = rhp.xmax

      assert rhp.num_bins % major_x_ticks_spacing == 0
      record_to_num_bins[record_type] = rhp.num_bins
    
    return record_to_xmin, record_to_xmax, record_to_num_bins


class RecordLineGraphProperties:

  @classmethod
  def get_y_bounds(cls):
    record_to_ymin = {}
    record_to_ymax = {}
    for rlgp in par.RecordLineGraphParams.RECORD_LINE_GRAPH_PARAMS:
      record_type = rlgp.record
      record_to_ymin[record_type] = rlgp.ymin
      record_to_ymax[record_type] = rlgp.ymax
    
    return record_to_ymin, record_to_ymax
