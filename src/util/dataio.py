from pathlib import Path

import params as par

class DataIO:
  def __init__(self, data_params):
    self.data_params = data_params

    current_dir = Path.cwd()
    assert current_dir.parts[-1] == 'apple_health', "Must run from folder apple_health"

    self.raw_data_dir = current_dir / 'data' / 'raw'
    self.raw_data_dir.mkdir(exist_ok = True, parents = True)

    self.parsed_data_dir = current_dir / 'data' / 'parsed'
    self.parsed_data_dir.mkdir(exist_ok = True, parents = True)

    self.graph_dir = current_dir / 'out'
    self.graph_dir.mkdir(exist_ok = True, parents = True)
  
  def get_raw_xml_filepath(self, filename):
    return self.raw_data_dir / filename
  
  def get_parsed_csv_filepath(self, filename):
    return self.parsed_data_dir / filename
  
  def get_graph_filepath(self, filename):
    return self.graph_dir / filename

  def get_csv_file(self, period = None):
    if period and not period == par.AggregationPeriod.DAILY:
      csv_filename = "{tz}_{start}_{end}{suffix}_{period}.csv".format(
                          tz = self.data_params.PARSE_TIMEZONE.name,
                          start = self.data_params.START_DATE.strftime("%Y%m%d"),
                          end = self.data_params.END_DATE.strftime("%Y%m%d"),
                          suffix = self.data_params.FILENAME_SUFFIX,
                          period = period.name)
    else:
      csv_filename = "{tz}_{start}_{end}{suffix}.csv".format(
                          tz = self.data_params.PARSE_TIMEZONE.name,
                          start = self.data_params.START_DATE.strftime("%Y%m%d"),
                          end = self.data_params.END_DATE.strftime("%Y%m%d"),
                          suffix = self.data_params.FILENAME_SUFFIX)

    return self.get_parsed_csv_filepath(csv_filename)
