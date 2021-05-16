def filter_missing_indexes(list_with_gaps, complete_list):
  '''
  Exclude elements that don't
  present in 'list_with_gaps'
  from 'complete_list'.
  '''
  filtered = []
  gaps_set = set(list_with_gaps)

  for elem in complete_list:
    if elem in gaps_set:
      filtered.append(elem)
  
  return filtered


# Not sure about rightness of filtering duplicates way
def filter_duplicate_elements(list_) -> [int]:
  '''
  Exclude elements that are duplicates
  and not the first occurrences
  from 'list_'.
  '''
  unique_list_elements = set()
  filtered_list_ = []

  for element in list_:
    if element not in unique_list_elements:
      filtered_list_.append(element)
      unique_list_elements.add(element)
  
  return filtered_list_


def filter_element(element, list_) -> [int]:
  return list(
      filter(
          lambda x: x != element, list_
      )
  )
