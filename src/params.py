from dataclasses import dataclass
from enum import Enum

from datetime import date

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
  RECORD_TYPES = [RecordType('ActiveEnergyBurned', 'Cal', AggregateType.SUM),
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

class ParseTimezone(Enum):
  CURRENT_TIMEZONE = 0
  DATA_TIMEZONE = 1

class ParserParams:
  INPUT_FILENAME = '20250530.xml'

  OUT_FILENAME_SUFFIX = ''
  START_DATE = date(2021, 1, 1)
  END_DATE = date(2025, 3, 1)
  PARSE_TIMEZONE = ParseTimezone.DATA_TIMEZONE

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

  SHOW_RECORD_UNIT_COUNTS = False
  SHOW_RECORD_SOURCE_COUNTS = True

class AggregationPeriod(Enum):
  DAILY = 0
  WEEKLY = 1
  MONTHLY = 2

class AggregatorParams:
  # These are used only to decide what input file to read
  FILENAME_SUFFIX =''
  START_DATE = date(2021, 1, 1)
  END_DATE = date(2025, 3, 1)
  PARSE_TIMEZONE = ParseTimezone.DATA_TIMEZONE
  
  AGGREGATION_PERIODS = [AggregationPeriod.WEEKLY,
                        AggregationPeriod.MONTHLY]
  
  WRITE_DATA = True

@dataclass
class HistogramLimits:
  record:     str
  xmin:       int
  xmax:       int
  num_bins:   int

class RecordHistogramLimits:
  RECORD_HISTOGRAM_LIMITS = [
      HistogramLimits('ActiveEnergyBurned', 600, 2400, 30),
      HistogramLimits('AppleExerciseTime', 30, 330, 30),
      HistogramLimits('AppleStandTime', 100, 550, 30),
      HistogramLimits('DistanceWalkingRunning', 5, 35, 30),
      HistogramLimits('FlightsClimbed', 0, 90, 30),
      HistogramLimits('StepCount', 6000, 42000, 30),
      HistogramLimits('TimeInDaylight', 0, 360, 30)]
      

class AggregateGraphParams:
  # These are used only to decide what input files to read
  FILENAME_SUFFIX =''
  DATA_START_DATE = date(2021, 1, 1)
  DATA_END_DATE = date(2025, 3, 1)
  PARSE_TIMEZONE = ParseTimezone.DATA_TIMEZONE

  GRAPH_START_DATE = date(2021, 1, 1)
  GRAPH_END_DATE = date(2025, 3, 1)

  AGGREGATION_PERIODS = [AggregationPeriod.DAILY,
                          AggregationPeriod.WEEKLY,
                          AggregationPeriod.MONTHLY]

  HISTOGRAMS = True
  LINE_GPAPHS = True
