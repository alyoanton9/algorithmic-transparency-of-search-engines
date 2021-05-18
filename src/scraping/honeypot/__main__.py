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

from common.config import scraping_log, gecko_path
from common.engine import Engine
from scraping.honeypot.processor import add_search_results_to_logs_buffer, honeypot_keyword
from scraping.scraper import Scraper


if __name__ == '__main__':

  with open(scraping_log) as f:
    logs = json.load(f)
    buffer = logs['scraping']

  user_agent = UserAgent().random

  firefox_options = Options()
  firefox_options.add_argument('-headless')
  firefox_options.add_argument(f'user-agent={user_agent}')

  driver = webdriver.Firefox(executable_path=gecko_path, options=firefox_options)

  for engine_item in Engine:
    engine = engine_item.value

    scraper = Scraper(user_agent, driver, honeypot_keyword, engine, with_omitted_results=False)
    search_results = scraper.obtain_first_page_search_results()
    buffer = add_search_results_to_logs_buffer(search_results, buffer)

  driver.quit()

  with open(scraping_log, 'w') as f:
    json.dump(logs, f, indent=4)
