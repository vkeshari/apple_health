from datetime import date

class ParserParams:
  INPUT_FILENAME = '20250530.xml'
  OUTPUT_FILENAME = '20250530.csv'

  START_DATE = date(2021, 1, 1)
  END_DATE = date(2025, 3, 1)
  DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S %z'

  SHOW_SUMMARY = False
