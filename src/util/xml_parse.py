import numpy as np

import params as par
from . import timeutil

class XmlParse:
  _record_types = par.RecordParams.RECORD_TYPES
  _record_type_prefix = 'HKQuantityTypeIdentifier'

  _skip_iphone_records = par.ParserParams.SKIP_IPHONE_RECORDS
  _iphone_source_text = 'iPhone'

  _checkpoint_every_n_records = 1000000

  @classmethod
  def aggregate_by_hour(cls, records_by_date, records_to_agg_type):
    for r in records_by_date:
      for d in records_by_date[r]:
        for hr in records_by_date[r][d]:
          if records_to_agg_type[r] == par.AggregateType.SUM:
            records_by_date[r][d][hr] = np.sum(records_by_date[r][d][hr])
          elif records_to_agg_type[r] in [par.AggregateType.AVERAGE, par.AggregateType.MEDIAN]:
            records_by_date[r][d][hr] = np.average(records_by_date[r][d][hr])
    return records_by_date
  
  @classmethod
  def aggregate_by_day(cls, records_by_date, records_to_agg_type):
    for r in records_by_date:
      for d in records_by_date[r]:
        if records_to_agg_type[r] == par.AggregateType.SUM:
          records_by_date[r][d] = np.sum(list(records_by_date[r][d].values()))
        elif records_to_agg_type[r] == par.AggregateType.AVERAGE:
          records_by_date[r][d] = np.average(list(records_by_date[r][d].values()))
        elif records_to_agg_type[r] == par.AggregateType.MEDIAN:
          records_by_date[r][d] = np.percentile(list(records_by_date[r][d].values()),
                                                50, method = 'nearest')
    return records_by_date

  @classmethod
  def parse_xml_data(cls, xml_tree, start_date, end_date,
                      parse_timezone, show_checkpoints = False):
    records_to_units = {rt.record: rt.unit for rt in cls._record_types}
    records_to_agg_type = {rt.record: rt.aggregation for rt in cls._record_types}

    records_by_date = {rt.record: {} for rt in cls._record_types}
    full_record_names = {r: cls._record_type_prefix + r.name for r in records_by_date}
    
    skip_iphone_records_full_names = \
        [cls._record_type_prefix + sir.name for sir in cls._skip_iphone_records]
    for i, record in enumerate(xml_tree.getroot().findall('Record')):
      if show_checkpoints and i % cls._checkpoint_every_n_records == 0:
        print ("Processed: {}".format(i))
      record_datetime = timeutil.DatetimeUtil.parse_xml_datetime(
                            datetime_string_from_xml = record.attrib['endDate'],
                            parse_timezone = parse_timezone)
      if not timeutil.DatetimeUtil.check_datetime_range(record_datetime, start_date, end_date):
        continue

      if record.attrib['type'] in skip_iphone_records_full_names \
            and cls._iphone_source_text in record.attrib['sourceName']:
        continue
      
      for r in records_by_date:
        if record.attrib['type'] == full_record_names[r] \
              and record.attrib['unit'] == records_to_units[r]:
          record_date = record_datetime.date()
          record_hour = record_datetime.hour
          if record_date not in records_by_date[r]:
            records_by_date[r][record_date] = {}
          if record_hour not in records_by_date[r][record_date]:
            records_by_date[r][record_date][record_hour] = []
          
          v = eval(record.attrib['value'])
          records_by_date[r][record_date][record_hour].append(v)
          break
    
    cls.aggregate_by_hour(records_by_date, records_to_agg_type)
    cls.aggregate_by_day(records_by_date, records_to_agg_type)
    
    return records_by_date
