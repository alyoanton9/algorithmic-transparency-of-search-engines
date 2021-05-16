import os
import sys
sys.path.append(os.path.dirname(os.path.abspath('src/common')))
sys.path.append(os.path.dirname(os.path.abspath('src/ranking')))
sys.path.append(os.path.dirname(os.path.abspath('src/scraping')))

from dataclasses import dataclass
from statistics import mean

from ranking.comparing.ranking_function import RankingFunction
from ranking.comparing.util import filter_duplicate_elements, filter_element, filter_missing_indexes
from scraping.chunks.process import omit_keyword_quotes


# custom types
query_order = [dict]
rate_by_function = dict[RankingFunction, float]

# dict keys
query_str = 'query'
order_str = 'order'
orders_str = f'{order_str}s'


@dataclass
class QueryRate:
  query: str # Currently helpful for debugging only, but may be used for further statistics.
  rate: rate_by_function

  def set_rate(self, function: RankingFunction, rate: float):
    self.rate[function] = rate

  def get_number_of_functions(self) -> int:
    return len(self.rate)


@dataclass
class EngineRate:
  engine: str
  rate: rate_by_function

  def to_dict(self) -> dict:
    return {
      'engine': self.engine,
      'rate': self.rate
    }

  def set_rate(self, function: RankingFunction, rate: float):
    self.rate[function] = rate

  def set_rates(self, rates: [float]):
    for func in RankingFunction:
      func_index = func.value - 1
      func_name = func.name
      self.set_rate(function=func_name, rate=rates[func_index])


class RateCalculator():
  def __init__(self, engine: str, rate_func, engine_orders: query_order, ranking_funcs_orders: query_order):
    self.engine = engine
    self.rate = rate_func
    self.engine_orders = engine_orders
    self.ranking_func_orders = ranking_funcs_orders


  def calculate_engine_rate(self) -> EngineRate:
    query_rates = self._calc_query_rates()
    engine_rate = EngineRate(engine=self.engine, rate={})
    
    number_of_ranking_functions = query_rates[0].get_number_of_functions()
    all_ranking_functions_rates = [[] for _ in range(number_of_ranking_functions)]

    for query_rate in query_rates:
      for func in RankingFunction:
        func_index = func.value - 1
        func_name = func.name
        func_query_rate = query_rate.rate[func_name]

        all_ranking_functions_rates[func_index].append(func_query_rate)

    mean_query_rates = list(map(mean, all_ranking_functions_rates))

    engine_rate.set_rates(mean_query_rates)

    return engine_rate


  def _calc_query_rates(self) -> [QueryRate]:
    query_rates = []
  
    for engine_query_order in self.engine_orders:
      query = engine_query_order[query_str]
      engine_order = engine_query_order[order_str]
      ranking_func_order = self._find_query_order_by_query(query)
      query_rate = QueryRate(query=query, rate={})

      for named_ranking_func_order in ranking_func_order[orders_str]:
        # Unfortunately, ranking functions orders are written
        # in bad-structured format:
        #   {
        #     query: str,
        #     orders: [
        #       [function_name: str, function_order: [int]]
        #     ]
        function_name = named_ranking_func_order[0]
        function_order = named_ranking_func_order[1]

        filtered_function_order = filter_missing_indexes(list_with_gaps=engine_order, complete_list=function_order)
        if len(filtered_function_order) != len(engine_order):
          engine_order = filter_duplicate_elements(engine_order)
          engine_order = filter_element(element=-1, list_=engine_order)

        function_rate = self.rate(engine_order, filtered_function_order)
        query_rate.set_rate(function=function_name, rate=function_rate)

      query_rates.append(query_rate)
  
    return query_rates


  def _find_query_order_by_query(self, query: str) -> dict:
    target_query_order = {}
    query = omit_keyword_quotes(query)

    for query_order in self.ranking_func_orders:
      if query_order[query_str] == query:
        target_query_order = query_order
        break
      
    if target_query_order == {}:
      raise Exception(f'No dict with \'{query}\' query')
    else:
      return target_query_order
