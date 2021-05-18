######################## Hack to enable local import ########################

import os, sys
sys.path.append(os.path.dirname(os.path.abspath(f'src/enable_local_import')))

from enable_local_import import enable_import
enable_import()

#############################################################################


import json

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from common.config import gecko_path
from common.engine import Engine
from ranking.remote.chunks_scraping.util import pretty_dump_json
from scraping.scraper import Scraper
from scraping.chunks.processor import find_chunk_index


queries_dir = 'src/ranking/queries/'

current_query_filename = queries_dir + 'query_1'

orders_dir = 'src/ranking/remote/doc_orders/'


def rotate_files(dirpath: str, file_prefix: str):
  '''
  Remove file with index '1',
  rename other files subtracting 1
  from each file's index.
  '''
  filepath_prefix = dirpath + file_prefix
  os.remove(f'{filepath_prefix}1')
  filepaths = os.listdir(dirpath)

  for ind in range(2, len(filepaths) + 1):
    filepath = filepath_prefix + str(ind)
    os.rename(filepath, filepath_prefix + str(ind - 1))


if __name__ == '__main__':
  firefox_options = Options()
  user_agent = UserAgent().random
  firefox_options.add_argument("-headless")
  firefox_options.add_argument(f'user-agent={user_agent}')

  driver = webdriver.Firefox(executable_path=gecko_path, options=firefox_options)

  with open(current_query_filename, 'r') as f:
    query = f.read()

  for engine_item in Engine:
    engine = engine_item.value

    if engine != Engine.GOOGLE.value and engine != Engine.YANDEX.value:
      continue

    engine_orders_filename = f'{orders_dir}{engine}.json'
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
