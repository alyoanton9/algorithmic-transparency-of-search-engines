# It's necessary to add the path of 'src/common'
# in 'sys.path' to import 'scraping.chunks' module
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath('src/common')))
sys.path.append(os.path.dirname(os.path.abspath('src/scraping')))
sys.path.append(os.path.dirname(os.path.abspath('src/scraping/chunks')))
sys.path.append(os.path.dirname(os.path.abspath('src/ranking/remote/chunks_scraping')))

import json

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from ranking.remote.chunks_scraping.util import pretty_dump_json, rotate_files
from common.config import gecko_path
from common.engine import Engine
from scraping.scraper import Scraper
from scraping.chunks.process import find_chunk_index


queries_dir = 'src/ranking/queries/'

current_query_filename = queries_dir + 'query_1'

orders_dir = 'src/ranking/remote/doc_orders/'


if __name__ == '__main__':
  firefox_options = Options()
  user_agent = UserAgent().random
  firefox_options.add_argument("-headless")
  firefox_options.add_argument(f'user-agent={user_agent}')

  driver = webdriver.Firefox(executable_path=gecko_path, options=firefox_options)

  with open(current_query_filename, 'r') as f:
    query = f.read()
  
  # need it to monitor scheduled srcaping
  print('query:', query)

  for engine_item in Engine:
    engine = engine_item.value

    if engine != Engine.GOOGLE.value and engine != Engine.YANDEX.value:
      continue

    engine_orders_filename = orders_dir + engine + '.json'
    with open(engine_orders_filename) as f:
      orders_buffer = json.load(f)

    scraper = Scraper(user_agent, driver, query, engine, with_omitted_results=True)
    search_results = scraper.obtain_all_pages_search_results()

    chunks_order = []
    for search_result_item in search_results.items:
      chunk_index = find_chunk_index(search_result_item)
      chunks_order.append(chunk_index)
    
    order_item = {
      'query': query,
      'order': chunks_order
    }
    orders_buffer.append(order_item)

    pretty_dump_json(obj=orders_buffer, filename=engine_orders_filename)
  
  driver.quit()

  rotate_files(queries_dir, 'query_')
