from . import timeutil

class XmlDebug:
  
  _skip_dietary_data = True
  _show_orphaned_dates = False

  @classmethod
  def show_node_summary(cls, node):
    print("{}".format(node.tag))
    print("\t{} attribute(s)".format(len(node.attrib)))
    for a, v in node.attrib.items():
      print("\t\t{}:\t{}".format(a, v))
    
    print("\t{} children".format(len(node)))
    for i, child in enumerate(node):
      print("\t\t{}:\t{}".format(i, child.tag))
      if i >= 5:
        print("\t\t...")
        break
  
  @classmethod
  def show_tree_summary(cls, tree, start_date, end_date, parse_timezone):
    root = tree.getroot()

    print()
    print("TREE SUMMARY")
    cls.show_node_summary(root)
    
    type_unit_counts = {}
    orphan_date_records = {}
    record_metrics = {'total_records' : 0,
                      'missing_type' : 0,
                      'missing_start_date' : 0,
                      'missing_end_date' : 0,
                      'orphan_start_date': 0,
                      'orphan_end_date': 0,
                      'outside_date_range': 0,
                      'missing_unit' : 0,
                      'missing_value' : 0}
    missing_unit_record_types = set()
    skipped_record_types = set()
    
    for child in root:
      if not child.tag == 'Record':
        continue
      record_metrics['total_records'] += 1
      
      skip_record = False
      if 'type' not in child.attrib:
        record_metrics['missing_type'] += 1
        skip_record = True
      if 'unit' not in child.attrib:
        record_metrics['missing_unit'] += 1
        missing_unit_record_types.add(child.attrib['type'])
        skip_record = True
      if 'value' not in child.attrib:
        record_metrics['missing_value'] += 1
        skip_record = True
      
      if 'startDate' not in child.attrib:
        record_metrics['missing_start_date'] += 1
        skip_record = True
      elif 'endDate' not in child.attrib:
        record_metrics['missing_end_date'] += 1
        skip_record = True
      else:
        start_dt_parsed = \
            timeutil.DatetimeUtil.parse_xml_datetime(child.attrib['startDate'], parse_timezone)
        end_dt_parsed = \
            timeutil.DatetimeUtil.parse_xml_datetime(child.attrib['endDate'], parse_timezone)

        if not start_dt_parsed:
          record_metrics['orphan_start_date'] += 1
          t = child.attrib['type']
          if t not in orphan_date_records:
            orphan_date_records[t] = set()
          date_string = child.attrib['startDate'][:10]
          orphan_date_records[t].add(date_string)
          skip_record = True
        if not end_dt_parsed:
          record_metrics['orphan_end_date'] += 1
          t = child.attrib['type']
          if t not in orphan_date_records:
            orphan_date_records[t] = set()
          date_string = child.attrib['startDate'][:10]
          orphan_date_records[t].add(date_string)
          skip_record = True
        
        if start_dt_parsed and end_dt_parsed:
          start_time_in_range = \
              timeutil.DatetimeUtil.check_datetime_range(start_dt_parsed, start_date, end_date)
          end_time_in_range = \
              timeutil.DatetimeUtil.check_datetime_range(end_dt_parsed, start_date, end_date)
          if not start_time_in_range or not end_time_in_range:
            record_metrics['outside_date_range'] += 1
            skip_record = True
      
      if not skip_record:
        t = child.attrib['type']
        if cls._skip_dietary_data and t.startswith('HKQuantityTypeIdentifierDietary'):
          skipped_record_types.add(t)
          continue
        
        u = child.attrib['unit']
        tu_tuple = tuple([t, u])
        if not tu_tuple in type_unit_counts:
          type_unit_counts[tu_tuple] = 0
        type_unit_counts[tu_tuple] += 1
    
    print()
    print("RECORD SUMMARY")
    print(record_metrics)
    print("MISSING UNIT RECORD TYPES: {}".format(len(missing_unit_record_types)))
    print(missing_unit_record_types)
    print("SKIPPED RECORD TYPES: {}".format(len(skipped_record_types)))
    print(skipped_record_types)
    print("ORPHAN DATE RECORDS")
    for t in orphan_date_records:
      print(t)
      if cls._show_orphaned_dates:
        print(sorted(orphan_date_records[t]))
    
    print()
    print("RECORD TYPES")
    for i, tu in enumerate(sorted(type_unit_counts.keys())):
      print("{index:3d}\t{count:8d}\t{unit:>10}\t{type}" \
                .format(index = i,
                        count = type_unit_counts[tu],
                        unit = tu[1],
                        type = tu[0]))
