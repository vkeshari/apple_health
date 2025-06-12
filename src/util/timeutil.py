from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

import params as par

@dataclass
class TimezonePeriod:
  start_date: date
  end_date:   date
  tz:         timezone

TZ_PACIFIC_DAYLIGHT = timezone(-timedelta(hours = 8), name = 'PDT')
TZ_BRITISH_SUMMER = timezone(timedelta(hours = 1), name = 'BST')
TZ_INDIA_STANDARD = timezone(timedelta(hours = 5, minutes = 30), name = 'IST')
TZ_CHINA_STANDARD = timezone(timedelta(hours = 8), name = 'CST')

# This list must be sorted by date
TZ_HISTORY = [
    TimezonePeriod(start_date = date(2020, 1, 1),
                    end_date = date(2023, 5, 24),
                    tz = TZ_PACIFIC_DAYLIGHT),
    TimezonePeriod(start_date = date(2023, 5, 24),
                    end_date = date(2023, 12, 30),
                    tz = TZ_BRITISH_SUMMER),
    TimezonePeriod(start_date = date(2023, 12, 30),
                    end_date = date(2024, 1, 21),
                    tz = TZ_INDIA_STANDARD),
    TimezonePeriod(start_date = date(2024, 1, 21),
                    end_date = date(2024, 2, 19),
                    tz = TZ_CHINA_STANDARD),
    TimezonePeriod(start_date = date(2024, 2, 19),
                    end_date = date(2024, 11, 3),
                    tz = TZ_INDIA_STANDARD),
    TimezonePeriod(start_date = date(2024, 11, 3),
                    end_date = date(2025, 2, 12),
                    tz = TZ_CHINA_STANDARD),
    TimezonePeriod(start_date = date(2025, 2, 12),
                    end_date = date(2025, 5, 31),
                    tz = TZ_INDIA_STANDARD)]
FIRST_DATE = TZ_HISTORY[0].start_date

last_end_date = FIRST_DATE
for tzh in TZ_HISTORY:
  assert tzh.end_date > tzh.start_date
  assert tzh.end_date > last_end_date
  last_end_date = tzh.end_date
print("VALIDATED TZ_HISTORY")

class TimezoneUtil:

  @classmethod
  def adjust_datetime_timezone(cls, dt):
    for tzh in TZ_HISTORY:
      adjusted_dt = dt.astimezone(tzh.tz)
      adjusted_date = adjusted_dt.date()
      if adjusted_date < FIRST_DATE:
        return None
      if adjusted_date <= tzh.end_date:
        return adjusted_dt
    
    return None

DATETIME_FORMAT_XML = '%Y-%m-%d %H:%M:%S %z'

class DatetimeUtil:

  @classmethod
  def parse_xml_datetime(cls, datetime_string_from_xml, parse_timezone):
    dt_parsed = datetime.strptime(datetime_string_from_xml, DATETIME_FORMAT_XML)
    
    if parse_timezone == par.ParseTimezone.DATA_TIMEZONE:
      return TimezoneUtil.adjust_datetime_timezone(dt_parsed)
    elif parse_timezone == par.ParseTimezone.CURRENT_TIMEZONE:
      return dt_parsed

  @classmethod
  def check_datetime_range(cls, dt, start_date, end_date):
    dt_date = dt.date()
    return dt_date >= start_date and dt_date < end_date
