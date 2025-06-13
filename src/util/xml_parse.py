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
  def parse_xml_data(cls, xml_tree, start_date, end_date,
                      parse_timezone, show_checkpoints = False):
    records_to_units = {rt.record: rt.unit for rt in cls._record_types}
    records_to_agg_type = {rt.record: rt.aggregation for rt in cls._record_types}

    records_by_date = {rt.record: {} for rt in cls._record_types}
    full_record_names = {r: cls._record_type_prefix + r for r in records_by_date}
    
    skip_iphone_records_full_names = \
        [cls._record_type_prefix + sir for sir in cls._skip_iphone_records]
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
          if record_date not in records_by_date[r]:
            records_by_date[r][record_date] = []
          records_by_date[r][record_date].append(eval(record.attrib['value']))
          break
    
    for r in records_by_date:
      for d in records_by_date[r]:
        if records_to_agg_type[r] == par.AggregateType.SUM:
          sum_val = np.sum(records_by_date[r][d])
          records_by_date[r][d] = round(sum_val, 2)
        elif records_to_agg_type[r] == par.AggregateType.AVERAGE:
          avg_val = np.average(records_by_date[r][d])
          records_by_date[r][d] = round(avg_val, 2)
        elif records_to_agg_type[r] == par.AggregateType.MEDIAN:
          median_val = np.percentile(records_by_date[r][d], 50, method = 'nearest')
          records_by_date[r][d] = round(median_val, 2)
    
    return records_by_date
