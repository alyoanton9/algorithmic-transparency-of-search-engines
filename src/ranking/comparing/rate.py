def pairwise_ordered_rate(x, y):
  '''
  Calculate similarity rate of
  2 lists which are permutations of
  the same unique elements.
  Count the number of pairs ('a', 'b')
  such that either
  'a' precedes 'b' in both 'x' and 'y'
  or
  'a' follows 'b' in both lists,
  and divide it by total number of
  pairs in the list.
  Example:
    x = [1, 4, 3]
    y = [3, 1, 4]
    same_ordered_pairs = 1 # (1, 4)
    total_pairs = 3 # (1, 4), (1, 3), (4, 3)
    similarity_rate = 1/3
  '''
  size = len(x)

  y_pred_pairs = set()

  for i in range(size):
    for j in range(i + 1, size):
      y_pred_pairs.add((y[i], y[j]))

  total_pairs = len(y_pred_pairs)
  same_ordered_pairs = 0

  for i in range(size):
    for j in range(i + 1, size):
      x_pair = (x[i], x[j])
      if x_pair in y_pred_pairs:
        same_ordered_pairs += 1

  return same_ordered_pairs / total_pairs if total_pairs > 0 else 1
