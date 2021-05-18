######################## Hack to enable local import ########################

import os, sys
sys.path.append(os.path.dirname(os.path.abspath(f'src/enable_local_import')))

from enable_local_import import enable_import
enable_import()

#############################################################################


import json

from common.engine import Engine
from ranking.local.diff_searching.processor import make_order_filename
from ranking.comparing.rate import pairwise_ordered_rate
from ranking.comparing.rate_calculator import RateCalculator, query_order


engine_orders_dirpath = 'src/ranking/remote/doc_orders/'

result_similarity_dirpath = 'src/ranking/comparing/results/'

query_str = 'query'


def get_engine_orders(engine: str) -> query_order:
  with open(f'{engine_orders_dirpath}{engine}.json', 'r') as f:
    orders = json.load(f)

  return orders


def filter_duplicate_queries(orders) -> query_order:
  queries = set()
  filtered_orders = []

  for query_order_dict in orders:
    query = query_order_dict[query_str]
    if query not in queries:
      filtered_orders.append(query_order_dict)
      queries.add(query)
  
  return filtered_orders


def get_ranking_functions_orders() -> query_order:
  orders = []
  for i in [1, 2]:
    orders_filename = make_order_filename(i)
    with open(orders_filename, 'r') as f:
      orders += json.load(f)

  filtered_orders = filter_duplicate_queries(orders)

  return filtered_orders


if __name__ == '__main__':
  ranking_functions_orders = get_ranking_functions_orders()

  for engine in [Engine.GOOGLE.value, Engine.YANDEX.value]:
    engine_result_similarity_dirpath = f'{result_similarity_dirpath}{engine}.json'

    with open(engine_result_similarity_dirpath, 'r') as f:
      buffer = json.load(f)

    engine_orders = get_engine_orders(engine)
    queries_number = len(engine_orders)

    rate_calculator = RateCalculator(engine, pairwise_ordered_rate, engine_orders, ranking_functions_orders)
    engine_rate = rate_calculator.calculate_engine_rate()

    engine_rate_with_dataset_size = engine_rate.to_dict()
    engine_rate_with_dataset_size.update(
      {'queries number': queries_number}
    )

    buffer.append(engine_rate_with_dataset_size)

    with open(engine_result_similarity_dirpath, 'w') as f:
      json.dump(buffer, f, indent=4)
