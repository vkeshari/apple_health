from datetime import date, datetime
from xml.etree import ElementTree as ET

import dataio
import params as par
from debug import xml_debug as xdb

def process_xml(in_tree, show_summary = False):
  start_time = datetime.now()

  if show_summary:
    xdb.XmlDebug.show_tree_summary(in_tree)

  processing_time = datetime.now() - start_time
  print()
  print("Data processed in {}".format(processing_time))
  return None

def write_data(data_dict, out_csv):
  start_time = datetime.now()

  write_time = datetime.now() - start_time
  print()
  print("Output written in {}".format(write_time))  


def parse_data():
  dio = dataio.DataIO()
  in_xml = dio.get_input_filepath(par.ParserParams.INPUT_FILENAME)
  out_csv = dio.get_output_filepath(par.ParserParams.OUTPUT_FILENAME)

  print("IN:\t{}".format(in_xml))
  print("OUT:\t{}".format(out_csv))

  start_time = datetime.now()
  in_tree = ET.parse(in_xml)
  parse_time = datetime.now() - start_time

  print()
  print("Input parsed in {}".format(parse_time))

  data_dict = process_xml(in_tree, show_summary = par.ParserParams.SHOW_SUMMARY)
  write_data(data_dict, out_csv)

  total_time = datetime.now() - start_time
  print()
  print("DONE in {}".format(total_time))

if __name__ == '__main__':
  parse_data()
