# It's necessary to add the path of 'src/common'
# in 'sys.path' to import 'config', 'engine', 'util' modules
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath('src/scrapping')))

from datetime import datetime

from scraping.scraper import SearchResultItem, SearchResults
from scraping.util import is_honeypot

# TODO rename module?


def get_honeypot_position_and_title(search_result_items: [SearchResultItem]) -> (int, str):
  position = -1

  for ind, result_item in enumerate(search_result_items):
    if is_honeypot(result_item.link):
      position = ind
      break
  
  if position != -1:
    return position + 1, search_result_items[ind].title
  else:
    return position, ''


def add_search_results_to_logs_buffer(search_results: SearchResults, logs_buffer: []):
  position, title = get_honeypot_position_and_title(search_results.items)

  # TODO don't convert to strings everything
  log_item = {
    'engine': search_results.engine,
    'query': search_results.query,
    'captcha': str(search_results.captcha),
    'no_results': str(search_results.no_results),
    'position': str(position),
    'title': title,
    'errors': search_results.internal_log,
    'time': datetime.now().strftime(format='%d/%m/%Y %H:%M:%S') # TODO check format
  }

  logs_buffer.append(log_item)
  return logs_buffer
