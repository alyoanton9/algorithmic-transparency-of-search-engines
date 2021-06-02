######################## Hack to enable local import ########################

import os, sys
sys.path.append(os.path.dirname(os.path.abspath(f'src/enable_local_import')))

from enable_local_import import enable_import
enable_import()

#############################################################################


import json

from common.engine import Engine
from ranking.comparing.rate import bubble_sort_rate
from ranking.comparing.rate_calculator import RateCalculator, query_order


engine_orders_dirpath = 'temp/ranking/remote/doc_orders/'

ranking_functions_orders_path = 'temp/ranking/local/doc_orders/bm25.json'

query_order_log_dirpath = 'logs/query_orders/'

query_rates_dirpath = 'results/ranking/comparing/'

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
  with open(ranking_functions_orders_path, 'r') as f:
    orders = json.load(f)
  filtered_orders = filter_duplicate_queries(orders)

  return filtered_orders


if __name__ == '__main__':
  ranking_functions_orders = get_ranking_functions_orders()

  for engine in [Engine.GOOGLE.value, Engine.YANDEX.value]:
    query_order_buffer = []
    query_rate_buffer = []

    engine_orders = get_engine_orders(engine)
    queries_number = len(engine_orders)

    rate_calculator = RateCalculator(engine, bubble_sort_rate, engine_orders, ranking_functions_orders)
    query_rates, query_orders = rate_calculator.calculate_query_rates_and_orders()

    with open(f'{query_order_log_dirpath}{engine}.json', 'w') as f:
      json.dump(query_orders, f, indent=4)

    with open(f'{query_rates_dirpath}{engine}.json', 'w') as f:
      json.dump(query_rates, f, indent=4)
