
class XmlDebug:
  
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
  def show_tree_summary(cls, tree):
    
    root = tree.getroot()

    print()
    print("TREE SUMMARY")
    cls.show_node_summary(root)
    
    type_unit_counts = {}
    record_metrics = {'total_records' : 0,
                      'missing_type' : 0,
                      'missing_start_date' : 0,
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
      if 'startDate' not in child.attrib:
        record_metrics['missing_start_date'] += 1
        skip_record = True
      if 'unit' not in child.attrib:
        record_metrics['missing_unit'] += 1
        missing_unit_record_types.add(child.attrib['type'])
        skip_record = True
      if 'value' not in child.attrib:
        record_metrics['missing_value'] += 1
        skip_record = True
      
      if not skip_record:
        t = child.attrib['type']
        if t.startswith('HKQuantityTypeIdentifierDietary'):
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
    
    print()
    print("RECORD TYPES")
    for i, (t, u) in enumerate(sorted(type_unit_counts.keys())):
      print("{index:3d}\t{count:8d}\t{unit:>10}\t{type}" \
                .format(index = i,
                        count = type_unit_counts[tuple([t, u])],
                        unit = u,
                        type = t))
