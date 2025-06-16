from pathlib import Path

class DataIO:
  def __init__(self):
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
