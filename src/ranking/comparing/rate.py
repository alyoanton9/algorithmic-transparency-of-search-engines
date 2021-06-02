from copy import deepcopy


def bubble_sort_rate(cut_set: [int], complete_set: [int]):
  def greater_and_ordered(x: int, y: int, order: dict[int, int]) -> (bool, bool):
    if y in order.keys():
      if x in order.keys():
        return order[x] > order[y], True
      else:
        return True, True
    else:
      return False, False

  if len(cut_set) == 0:
    return 0

  complete_size = len(complete_set)
  complete_set_copy = deepcopy(complete_set)
  order = {cut_set[i]: i for i in range(len(cut_set))}
  relevant_ordered_pairs = set()

  number_of_swaps = 0
  all_sorted = False

  for i in range(complete_size - 1):
    all_sorted = True

    for j in range(complete_size - i - 1):
      need_swap, ordered_pair = greater_and_ordered(complete_set_copy[j], complete_set_copy[j + 1], order)
      if ordered_pair:
        p1, p2 = sorted((complete_set_copy[j], complete_set_copy[j + 1]))
        relevant_ordered_pairs.add((p1, p2))
      if need_swap:
        complete_set_copy[j], complete_set_copy[j + 1] = complete_set_copy[j + 1], complete_set_copy[j]
        number_of_swaps += 1
        all_sorted = False

    if all_sorted:
      break

  if number_of_swaps == 0 and len(relevant_ordered_pairs) == 0:
    return 1

  rate = 1 - number_of_swaps / len(relevant_ordered_pairs)

  return rate
