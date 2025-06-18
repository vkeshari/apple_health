from datetime import datetime
from xml.etree import ElementTree as ET

import params as par
from util import csvutil, dataio, paramutil
from util import xml_debug as xdb
from util import xml_parse as xpr

def process_xml(in_tree, start_date, end_date, parse_timezone,
                show_summary = False, parse_data = True):
  start_time = datetime.now()
  
  if show_summary:
    xdb.XmlDebug.show_tree_summary(in_tree, start_date, end_date, parse_timezone)
  if not parse_data:
    return None
  
  print()
  print("PROCESSING DATA")
  records_by_date = xpr.XmlParse.parse_xml_data(in_tree, start_date, end_date,
                                                parse_timezone,
                                                show_checkpoints = True)
  data_dict = csvutil.XmlToCsv.xml_dict_to_csv_dict(records_by_date)
  
  print()
  print("Data processed in {}".format(datetime.now() - start_time))

  return data_dict


def parse_data():
  paramutil.Validator.validate_parse_data()

  dio = dataio.DataIO()
  in_xml = dio.get_raw_xml_filepath(par.ParserParams.INPUT_FILENAME)
  print("IN:\t{}".format(in_xml))

  start_time = datetime.now()
  in_tree = ET.parse(in_xml)

  print()
  print("Input read in {}".format(datetime.now() - start_time))

  data_dict = process_xml(in_tree,
                            start_date = par.ParserParams.START_DATE,
                            end_date = par.ParserParams.END_DATE,
                            parse_timezone = par.ParserParams.PARSE_TIMEZONE,
                            show_summary = par.ParserParams.SHOW_SUMMARY,
                            parse_data = par.ParserParams.PARSE_DATA)
  if par.ParserParams.WRITE_DATA:
    out_csv_filename = "{tz}_{start}_{end}{suffix}.csv".format(
                          tz = par.ParserParams.PARSE_TIMEZONE.name,
                          start = par.ParserParams.START_DATE.strftime("%Y%m%d"),
                          end = par.ParserParams.END_DATE.strftime("%Y%m%d"),
                          suffix = par.ParserParams.OUT_FILENAME_SUFFIX)
    out_csv = dio.get_parsed_csv_filepath(out_csv_filename)
    csvutil.CsvIO.write_data_csv(out_csv, data_dict)

  print()
  print("DONE in {}".format(datetime.now() - start_time))

if __name__ == '__main__':
  parse_data()
