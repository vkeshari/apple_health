from dataclasses import dataclass
from enum import Enum

from datetime import date

class ParseTimezone(Enum):
  # Parse all data in current timezone
  #   (this is the timezone in which Apple Health Data was exported)
  CURRENT_TIMEZONE = 0

  # Parse all data in the best estimate of the data's timezone
  #   (as defined in util.timeutil.TimezoneHistory)
  DATA_TIMEZONE = 1

class DataParams:
  # These are used to decide what input CSV file(s) to read or write
  FILENAME_SUFFIX = ''
  START_DATE = date(2021, 1, 1)
  END_DATE = date(2025, 3, 1)
  PARSE_TIMEZONE = ParseTimezone.DATA_TIMEZONE

class ParserParams:
  INPUT_FILENAME = '20250530.xml'

  # Configure summary in XmlDebugParams
  SHOW_SUMMARY = False

  PARSE_DATA = True
  WRITE_DATA = True

  # These records are double-counted by iPhone. Only include data from Apple Watch.
  SKIP_IPHONE_RECORDS = ['DistanceWalkingRunning',
                          'FlightsClimbed',
                          'StepCount']

class XmlDebugParams:
  SKIP_DIETARTY_DATA = True
  SHOW_SKIPPED_RECORDS = False

  SHOW_MISSING_UNIT_RECORDS = False

  SHOW_ORPHANED_RECORDS = False
  SHOW_ORPHANED_DATES = False

  SHOW_RECORD_UNIT_COUNTS = True
  SHOW_RECORD_SOURCE_COUNTS = False

class AggregationPeriod(Enum):
  DAILY = 0
  WEEKLY = 1
  MONTHLY = 2
  QUARTERLY = 3

class AggregatorParams:
  # Does not support DAILY, by definition
  AGGREGATION_PERIODS = [AggregationPeriod.WEEKLY,
                        AggregationPeriod.MONTHLY,
                        AggregationPeriod.QUARTERLY]
  
  WRITE_DATA = True

class GraphParams:
  GRAPH_START_DATE = date(2021, 1, 1)
  GRAPH_END_DATE = date(2025, 3, 1)

  AGGREGATION_PERIODS = [AggregationPeriod.DAILY,
                          AggregationPeriod.WEEKLY,
                          AggregationPeriod.MONTHLY,
                          AggregationPeriod.QUARTERLY]

  HISTOGRAMS = False
  LINE_GRAPHS = True

class BucketingType(Enum):
  RANDOMLY = 0
  BY_YEAR = 1

class BucketedGraphParams:
  GRAPH_START_DATE = date(2021, 1, 1)
  GRAPH_END_DATE = date(2025, 1, 1)

  # Does not support MONTHLY or QUARTERLY, due to small no. of data points
  AGGREGATION_PERIODS = [AggregationPeriod.DAILY,
                          AggregationPeriod.WEEKLY]
  BUCKETING = BucketingType.RANDOMLY
  NUM_RANDOM_BUCKETS = 10

class BucketTuningParams:
  MIN_BUCKETS = 1
  MAX_BUCKETS = 60
  BUCKET_STEP = 1


# Record and graph configs

class AggregateType(Enum):
  SUM = 0
  AVERAGE = 1
  MEDIAN = 2

@dataclass
class RecordType:
  record:      str
  unit:        str
  aggregation: AggregateType

class RecordParams:
  RECORD_TYPES = [
      RecordType('ActiveEnergyBurned', 'Cal', AggregateType.SUM),
      RecordType('AppleExerciseTime', 'min', AggregateType.SUM),
      RecordType('AppleStandTime', 'min', AggregateType.SUM),
      RecordType('BodyMass', 'kg', AggregateType.AVERAGE),
      RecordType('DistanceWalkingRunning', 'km', AggregateType.SUM),
      RecordType('FlightsClimbed', 'count', AggregateType.SUM),
      RecordType('HeartRate', 'count/min', AggregateType.MEDIAN),
      RecordType('HeartRateRecoveryOneMinute', 'count/min', AggregateType.MEDIAN),
      RecordType('PhysicalEffort', 'kcal/hr·kg', AggregateType.MEDIAN),
      RecordType('RespiratoryRate', 'count/min', AggregateType.MEDIAN),
      RecordType('RestingHeartRate', 'count/min', AggregateType.MEDIAN),
      RecordType('StairAscentSpeed', 'm/s', AggregateType.MEDIAN),
      RecordType('StairDescentSpeed', 'm/s', AggregateType.MEDIAN),
      RecordType('StepCount', 'count', AggregateType.SUM),
      RecordType('TimeInDaylight', 'min', AggregateType.SUM),
      RecordType('VO2Max', 'mL/min·kg', AggregateType.AVERAGE),
      RecordType('WalkingAsymmetryPercentage', '%', AggregateType.AVERAGE),
      RecordType('WalkingDoubleSupportPercentage', '%', AggregateType.AVERAGE),
      RecordType('WalkingSpeed', 'km/hr', AggregateType.MEDIAN)]

@dataclass
class GraphTextParams:
  record:         str
  text_precision: int

class RecordGraphTextParams:
  RECORD_GRAPH_TEXT_PARAMS = [
      GraphTextParams('ActiveEnergyBurned', 0),
      GraphTextParams('AppleExerciseTime', 0),
      GraphTextParams('AppleStandTime', 0),
      GraphTextParams('BodyMass', 1),
      GraphTextParams('DistanceWalkingRunning', 1),
      GraphTextParams('FlightsClimbed', 0),
      GraphTextParams('HeartRate', 0),
      GraphTextParams('HeartRateRecoveryOneMinute', 0),
      GraphTextParams('PhysicalEffort', 1),
      GraphTextParams('RespiratoryRate', 1),
      GraphTextParams('RestingHeartRate', 0),
      GraphTextParams('StairAscentSpeed', 1),
      GraphTextParams('StairDescentSpeed', 1),
      GraphTextParams('StepCount', 0),
      GraphTextParams('TimeInDaylight', 0),
      GraphTextParams('VO2Max', 1),
      GraphTextParams('WalkingAsymmetryPercentage', 2),
      GraphTextParams('WalkingDoubleSupportPercentage', 2),
      GraphTextParams('WalkingSpeed', 1)]

@dataclass
class HistogramParams:
  record:   str
  xmin:     int
  xmax:     int
  num_bins: int

class RecordHistogramParams:
  RECORD_HISTOGRAM_PARAMS = [
      HistogramParams('ActiveEnergyBurned', 600, 2400, 30),
      HistogramParams('AppleExerciseTime', 30, 330, 30),
      HistogramParams('AppleStandTime', 100, 550, 30),
      HistogramParams('DistanceWalkingRunning', 5, 35, 30),
      HistogramParams('FlightsClimbed', 0, 90, 30),
      HistogramParams('StepCount', 6000, 42000, 30),
      HistogramParams('TimeInDaylight', 0, 360, 30)]

@dataclass
class LineGraphParams:
  record: str
  ymin:   int
  ymax:   int

class RecordLineGraphParams:
  RECORD_LINE_GRAPH_PARAMS = [
      LineGraphParams('ActiveEnergyBurned', 0, 2500),
      LineGraphParams('AppleExerciseTime', 0, 300),
      LineGraphParams('AppleStandTime', 0, 500),
      LineGraphParams('BodyMass', 70, 100),
      LineGraphParams('DistanceWalkingRunning', 0, 25),
      LineGraphParams('FlightsClimbed', 0, 100),
      LineGraphParams('HeartRate', 40, 160),
      LineGraphParams('HeartRateRecoveryOneMinute', 20, 60),
      LineGraphParams('PhysicalEffort', 2, 6),
      LineGraphParams('RespiratoryRate', 8, 24),
      LineGraphParams('RestingHeartRate', 20, 80),
      LineGraphParams('StairAscentSpeed', 0, 1),
      LineGraphParams('StairDescentSpeed', 0, 1),
      LineGraphParams('StepCount', 0, 40000),
      LineGraphParams('TimeInDaylight', 0, 400),
      LineGraphParams('VO2Max', 30, 50),
      LineGraphParams('WalkingAsymmetryPercentage', 0, 100),
      LineGraphParams('WalkingDoubleSupportPercentage', 20, 40),
      LineGraphParams('WalkingSpeed', 2, 8)]
