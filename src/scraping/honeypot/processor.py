from datetime import datetime

from common.config import custom_date_format
from scraping.scraper import SearchResultItem, SearchResults


honeypot_domain = 'hydromel-chouchenn.eu.org'
honeypot_keyword = 'azpoicvsda'


def is_honeypot(link: str) -> bool:
  '''
  Check by the given link if website is honeypot.
  '''
  link = link.strip().strip('/')
  return link == f'https://{honeypot_domain}' or link == honeypot_domain


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


def add_search_results_to_logs_buffer(search_results: SearchResults, buffer: [dict]):
  position, title = get_honeypot_position_and_title(search_results.items)

  log_item = {
    'engine': search_results.engine,
    'query': search_results.query,
    'captcha': str(search_results.captcha),
    'no_results': str(search_results.no_results),
    'position': str(position),
    'title': title,
    'errors': search_results.internal_log,
    'time': datetime.now().strftime(format=custom_date_format)
  }

  buffer.append(log_item)
  return buffer
