from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

import params as par

@dataclass
class TimezonePeriod:
  start_date: date
  end_date:   date
  tz:         timezone

class TimezoneHistory:
  _tz_pacific_daylight = timezone(-timedelta(hours = 8), name = 'PDT')
  _tz_british_summer = timezone(timedelta(hours = 1), name = 'BST')
  _tz_india_standard = timezone(timedelta(hours = 5, minutes = 30), name = 'IST')
  _tz_china_standard = timezone(timedelta(hours = 8), name = 'CST')

  # This list must be sorted by date
  _tz_history = [
      TimezonePeriod(start_date = date(2020, 1, 1),
                      end_date = date(2023, 5, 24),
                      tz = _tz_pacific_daylight),
      TimezonePeriod(start_date = date(2023, 5, 24),
                      end_date = date(2023, 12, 30),
                      tz = _tz_british_summer),
      TimezonePeriod(start_date = date(2023, 12, 30),
                      end_date = date(2024, 1, 21),
                      tz = _tz_india_standard),
      TimezonePeriod(start_date = date(2024, 1, 21),
                      end_date = date(2024, 2, 19),
                      tz = _tz_china_standard),
      TimezonePeriod(start_date = date(2024, 2, 19),
                      end_date = date(2024, 11, 3),
                      tz = _tz_india_standard),
      TimezonePeriod(start_date = date(2024, 11, 3),
                      end_date = date(2025, 2, 12),
                      tz = _tz_china_standard),
      TimezonePeriod(start_date = date(2025, 2, 12),
                      end_date = date(2025, 5, 31),
                      tz = _tz_india_standard)]
  _first_date = _tz_history[0].start_date

  last_end_date = _first_date
  for tzh in _tz_history:
    assert tzh.start_date >= last_end_date
    assert tzh.end_date > tzh.start_date
    last_end_date = tzh.end_date
  print("VALIDATED TIMEZONE HISTORY")

class TimezoneUtil:

  @classmethod
  def adjust_datetime_timezone(cls, dt):
    for tzh in TimezoneHistory._tz_history:
      adjusted_dt = dt.astimezone(tzh.tz)
      adjusted_date = adjusted_dt.date()
      if adjusted_date < TimezoneHistory._first_date:
        return None
      if adjusted_date <= tzh.end_date:
        return adjusted_dt
    
    return None

class DatetimeUtil:

  _datetime_formal_xml = '%Y-%m-%d %H:%M:%S %z'

  @classmethod
  def parse_xml_datetime(cls, datetime_string_from_xml, parse_timezone):
    dt_parsed = datetime.strptime(datetime_string_from_xml, cls._datetime_formal_xml)
    
    if parse_timezone == par.ParseTimezone.DATA_TIMEZONE:
      return TimezoneUtil.adjust_datetime_timezone(dt_parsed)
    elif parse_timezone == par.ParseTimezone.CURRENT_TIMEZONE:
      return dt_parsed

  @classmethod
  def check_datetime_range(cls, dt, start_date, end_date):
    if not dt:
      return False
    
    return dt.date() >= start_date and dt.date() < end_date
  
class CalendarUtil:

  _one_day = timedelta(days = 1)

  @classmethod
  def get_month_start_date(cls, d):
    return date(d.year, d.month, 1)
  
  @classmethod
  def get_week_start_date(cls, d):
    day_of_week = d.weekday()
    return d - day_of_week * cls._one_day
