from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from dateutil import relativedelta as rd

import params as par

@dataclass
class TimezonePeriod:
  start_date: date
  end_date:   date
  tz:         timezone

class TimezoneHistory:
  _tz_pacific_daylight = timezone(-timedelta(hours = 7), name = 'PDT')
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
  def check_date_range(cls, d, start_date, end_date):
    if not d:
      return False
    
    return d >= start_date and d < end_date

  @classmethod
  def check_datetime_range(cls, dt, start_date, end_date):
    if not dt:
      return False
    
    return cls.check_date_range(dt.date(), start_date, end_date)

class Timestamp:

  _timestamp_format = '%Y%m%d%H%M%S'

  @classmethod
  def get_timestamp(cls):
    return datetime.now().strftime(cls._timestamp_format)


class CalendarUtil:

  _one_day = rd.relativedelta(days = 1)
  _one_week = rd.relativedelta(weeks = 1)
  _one_month = rd.relativedelta(months = 1)
  _one_quarter = 3 * _one_month
  _quarter_start_months = [1, 4, 7, 10]
  
  @classmethod
  def get_week_start_date(cls, d):
    day_of_week = d.weekday()
    return d - day_of_week * cls._one_day

  @classmethod
  def get_month_start_date(cls, d):
    return date(d.year, d.month, 1)

  @classmethod
  def get_quarter_start_date(cls, d):
    if d.month in cls._quarter_start_months:
      return date(d.year, d.month, 1)
    else:
      for sm in cls._quarter_start_months:
        if d.month - sm < 3:
          return date(d.year, sm, 1)
  
  @classmethod
  def get_period_start_date(cls, d, period):
    if period == par.AggregationPeriod.DAILY:
      return d
    elif period == par.AggregationPeriod.WEEKLY:
      return cls.get_week_start_date(d)
    elif period == par.AggregationPeriod.MONTHLY:
      return cls.get_month_start_date(d)
    elif period == par.AggregationPeriod.QUARTERLY:
      return cls.get_quarter_start_date(d)
  
  @classmethod
  def get_next_day(cls, d):
    return d + cls._one_day
  
  @classmethod
  def get_next_week(cls, d):
    return d + cls._one_week
  
  @classmethod
  def get_next_month(cls, d):
    return d + cls._one_month
  
  @classmethod
  def get_next_quarter(cls, d):
    return d + cls._one_quarter
  
  @classmethod
  def get_next_period(cls, d, period):
    if period == par.AggregationPeriod.DAILY:
      return cls.get_next_day(d)
    elif period == par.AggregationPeriod.WEEKLY:
      return cls.get_next_week(d)
    elif period == par.AggregationPeriod.MONTHLY:
      return cls.get_next_month(d)
    elif period == par.AggregationPeriod.QUARTERLY:
      return cls.get_next_quarter(d)
  
  @classmethod
  def get_next_period_start_date(cls, d, period):
    return cls.get_next_period(cls.get_period_start_date(d, period), period)
