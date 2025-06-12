from enum import Enum

from datetime import date

class ParseTimezone(Enum):
  CURRENT_TIMEZONE = 0
  DATA_TIMEZONE = 1

class ParserParams:
  INPUT_FILENAME = '20250530.xml'
  OUTPUT_FILENAME = '20250530.csv'

  START_DATE = date(2021, 1, 1)
  END_DATE = date(2025, 3, 1)
  PARSE_TIMEZONE = ParseTimezone.DATA_TIMEZONE

  SHOW_SUMMARY = True
