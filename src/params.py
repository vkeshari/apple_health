from dataclasses import dataclass
from enum import Enum, unique

from datetime import date

# Activity Record Types

@unique
class Activity(Enum):
  ActiveEnergyBurned = 0
  AppleExerciseTime = 1
  AppleStandTime = 2
  BodyMass = 3
  DistanceWalkingRunning = 4
  FlightsClimbed = 5
  HeartRate = 6
  HeartRateRecoveryOneMinute = 7
  PhysicalEffort = 8
  RespiratoryRate = 9
  RestingHeartRate = 10
  StairAscentSpeed = 11
  StairDescentSpeed = 12
  StepCount = 13
  TimeInDaylight = 14
  VO2Max = 15
  WalkingAsymmetryPercentage = 16
  WalkingDoubleSupportPercentage = 17
  WalkingSpeed = 18


# Script Configs

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
  SKIP_IPHONE_RECORDS = [Activity.DistanceWalkingRunning,
                          Activity.FlightsClimbed,
                          Activity.StepCount]

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

  NUM_RUNS = 20

class CorrelationType(Enum):
  PEARSON = 0
  SPEARMAN = 1
  KENDALL = 2

class RecordComparisonParams:
  # Does not support QUARTERLY, due to small no. of data points
  AGGREGATION_PERIODS = [AggregationPeriod.DAILY,
                          AggregationPeriod.WEEKLY,
                          AggregationPeriod.MONTHLY]
  
  MAX_PERIOD_DELTAS = {AggregationPeriod.DAILY: 14,
                        AggregationPeriod.WEEKLY: 6,
                        AggregationPeriod.MONTHLY: 3}
  
  MIN_CORRELATIONS = {CorrelationType.PEARSON: 0.8,
                      CorrelationType.SPEARMAN: 0.8,
                      CorrelationType.KENDALL: 0.8}


# Record and Graph Configs

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
      RecordType(Activity.ActiveEnergyBurned, 'Cal', AggregateType.SUM),
      RecordType(Activity.AppleExerciseTime, 'min', AggregateType.SUM),
      RecordType(Activity.AppleStandTime, 'min', AggregateType.SUM),
      RecordType(Activity.BodyMass, 'kg', AggregateType.AVERAGE),
      RecordType(Activity.DistanceWalkingRunning, 'km', AggregateType.SUM),
      RecordType(Activity.FlightsClimbed, 'count', AggregateType.SUM),
      RecordType(Activity.HeartRate, 'count/min', AggregateType.MEDIAN),
      RecordType(Activity.HeartRateRecoveryOneMinute, 'count/min', AggregateType.MEDIAN),
      RecordType(Activity.PhysicalEffort, 'kcal/hr·kg', AggregateType.MEDIAN),
      RecordType(Activity.RespiratoryRate, 'count/min', AggregateType.MEDIAN),
      RecordType(Activity.RestingHeartRate, 'count/min', AggregateType.MEDIAN),
      RecordType(Activity.StairAscentSpeed, 'm/s', AggregateType.MEDIAN),
      RecordType(Activity.StairDescentSpeed, 'm/s', AggregateType.MEDIAN),
      RecordType(Activity.StepCount, 'count', AggregateType.SUM),
      RecordType(Activity.TimeInDaylight, 'min', AggregateType.SUM),
      RecordType(Activity.VO2Max, 'mL/min·kg', AggregateType.AVERAGE),
      RecordType(Activity.WalkingAsymmetryPercentage, '%', AggregateType.AVERAGE),
      RecordType(Activity.WalkingDoubleSupportPercentage, '%', AggregateType.AVERAGE),
      RecordType(Activity.WalkingSpeed, 'km/hr', AggregateType.MEDIAN)]

@dataclass
class GraphTextParams:
  record:         str
  text_precision: int

class RecordGraphTextParams:
  RECORD_GRAPH_TEXT_PARAMS = [
      GraphTextParams(Activity.ActiveEnergyBurned, 0),
      GraphTextParams(Activity.AppleExerciseTime, 0),
      GraphTextParams(Activity.AppleStandTime, 0),
      GraphTextParams(Activity.BodyMass, 1),
      GraphTextParams(Activity.DistanceWalkingRunning, 1),
      GraphTextParams(Activity.FlightsClimbed, 0),
      GraphTextParams(Activity.HeartRate, 0),
      GraphTextParams(Activity.HeartRateRecoveryOneMinute, 0),
      GraphTextParams(Activity.PhysicalEffort, 1),
      GraphTextParams(Activity.RespiratoryRate, 1),
      GraphTextParams(Activity.RestingHeartRate, 0),
      GraphTextParams(Activity.StairAscentSpeed, 1),
      GraphTextParams(Activity.StairDescentSpeed, 1),
      GraphTextParams(Activity.StepCount, 0),
      GraphTextParams(Activity.TimeInDaylight, 0),
      GraphTextParams(Activity.VO2Max, 1),
      GraphTextParams(Activity.WalkingAsymmetryPercentage, 2),
      GraphTextParams(Activity.WalkingDoubleSupportPercentage, 2),
      GraphTextParams(Activity.WalkingSpeed, 1)]

@dataclass
class HistogramParams:
  record:   str
  xmin:     int
  xmax:     int
  num_bins: int

class RecordHistogramParams:
  RECORD_HISTOGRAM_PARAMS = [
      HistogramParams(Activity.ActiveEnergyBurned, 600, 2400, 30),
      HistogramParams(Activity.AppleExerciseTime, 30, 330, 30),
      HistogramParams(Activity.AppleStandTime, 100, 550, 30),
      HistogramParams(Activity.DistanceWalkingRunning, 5, 35, 30),
      HistogramParams(Activity.FlightsClimbed, 0, 90, 30),
      HistogramParams(Activity.StepCount, 6000, 42000, 30),
      HistogramParams(Activity.TimeInDaylight, 0, 360, 30)]

@dataclass
class LineGraphParams:
  record: str
  ymin:   int
  ymax:   int

class RecordLineGraphParams:
  RECORD_LINE_GRAPH_PARAMS = [
      LineGraphParams(Activity.ActiveEnergyBurned, 0, 2500),
      LineGraphParams(Activity.AppleExerciseTime, 0, 300),
      LineGraphParams(Activity.AppleStandTime, 0, 500),
      LineGraphParams(Activity.BodyMass, 70, 100),
      LineGraphParams(Activity.DistanceWalkingRunning, 0, 25),
      LineGraphParams(Activity.FlightsClimbed, 0, 100),
      LineGraphParams(Activity.HeartRate, 40, 120),
      LineGraphParams(Activity.HeartRateRecoveryOneMinute, 20, 60),
      LineGraphParams(Activity.PhysicalEffort, 2, 6),
      LineGraphParams(Activity.RespiratoryRate, 8, 24),
      LineGraphParams(Activity.RestingHeartRate, 20, 80),
      LineGraphParams(Activity.StairAscentSpeed, 0, 1),
      LineGraphParams(Activity.StairDescentSpeed, 0, 1),
      LineGraphParams(Activity.StepCount, 0, 40000),
      LineGraphParams(Activity.TimeInDaylight, 0, 400),
      LineGraphParams(Activity.VO2Max, 30, 50),
      LineGraphParams(Activity.WalkingAsymmetryPercentage, 0, 100),
      LineGraphParams(Activity.WalkingDoubleSupportPercentage, 20, 40),
      LineGraphParams(Activity.WalkingSpeed, 2, 8)]
