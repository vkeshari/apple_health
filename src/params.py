from dataclasses import dataclass
from enum import Enum

from datetime import date

class ParseTimezone(Enum):
  CURRENT_TIMEZONE = 0
  DATA_TIMEZONE = 1

class ParserParams:
  INPUT_FILENAME = '20250530.xml'
  OUT_FILENAME_SUFFIX = ''

  START_DATE = date(2021, 1, 1)
  END_DATE = date(2025, 3, 1)
  PARSE_TIMEZONE = ParseTimezone.DATA_TIMEZONE

  PARSE_DATA = True
  SHOW_SUMMARY = False

  SKIP_IPHONE_RECORDS = ['BasalEnergyBurned',
                          'DistanceWalkingRunning',
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
                  RecordType('BasalEnergyBurned', 'Cal', AggregateType.SUM),
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
