from csv import DictWriter
from datetime import datetime
from xml.etree import ElementTree as ET

import dataio
import params as par
from util import xml_debug as xdb
from util import xml_parse as xpr

DATE_FIELD_CSV = 'date'

def build_csv_dict(records_by_date):
  fields = [DATE_FIELD_CSV] + sorted(records_by_date.keys())

  data_dict = {}
  for r in records_by_date:
    for d in records_by_date[r]:
      if d not in data_dict:
        data_dict[d] = {}
      data_dict[d][r] = records_by_date[r][d]
  
  return fields, data_dict

def process_xml(in_tree, start_date, end_date, parse_timezone,
                show_summary = False, parse_data = True):
  start_time = datetime.now()
  
  if show_summary:
    xdb.XmlDebug.show_tree_summary(in_tree, start_date, end_date, parse_timezone)
  if not parse_data:
    return None, None
  
  print()
  print("PROCESSING DATA")
  records_by_date = xpr.XmlParse.parse_xml_data(in_tree, start_date, end_date,
                                                parse_timezone,
                                                show_checkpoints = True)
  print("DATA PROCESSED")

  fields, data_dict = build_csv_dict(records_by_date)
  
  processing_time = datetime.now() - start_time
  print()
  print("Data processed in {}".format(processing_time))

  return fields, data_dict

def write_data(fields, data_dict, out_csv):
  start_time = datetime.now()

  with open(out_csv, 'w', newline = '') as csv_file:
    writer = DictWriter(csv_file, fieldnames = fields, restval = 'NA')
    writer.writeheader()

    for d in sorted(data_dict.keys()):
      writer.writerow({DATE_FIELD_CSV: str(d)} | data_dict[d])

  write_time = datetime.now() - start_time
  print()
  print("Output written in {}".format(write_time))  


def parse_data():
  dio = dataio.DataIO()
  in_xml = dio.get_raw_xml_filepath(par.ParserParams.INPUT_FILENAME)

  out_csv_filename = "{tz}_{start}_{end}{suffix}.csv".format(
                        tz = par.ParserParams.PARSE_TIMEZONE.name,
                        start = par.ParserParams.START_DATE.strftime("%Y%m%d"),
                        end = par.ParserParams.END_DATE.strftime("%Y%m%d"),
                        suffix = par.ParserParams.OUT_FILENAME_SUFFIX)
  out_csv = dio.get_parsed_csv_filepath(out_csv_filename)

  print("IN:\t{}".format(in_xml))
  print("OUT:\t{}".format(out_csv))

  start_time = datetime.now()
  in_tree = ET.parse(in_xml)
  parse_time = datetime.now() - start_time

  print()
  print("Input read in {}".format(parse_time))

  fields, data_dict = process_xml(in_tree,
                                  start_date = par.ParserParams.START_DATE,
                                  end_date = par.ParserParams.END_DATE,
                                  parse_timezone = par.ParserParams.PARSE_TIMEZONE,
                                  show_summary = par.ParserParams.SHOW_SUMMARY,
                                  parse_data = par.ParserParams.PARSE_DATA)
  if par.ParserParams.PARSE_DATA:
    write_data(fields, data_dict, out_csv)

  total_time = datetime.now() - start_time
  print()
  print("DONE in {}".format(total_time))

if __name__ == '__main__':
  parse_data()
