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
