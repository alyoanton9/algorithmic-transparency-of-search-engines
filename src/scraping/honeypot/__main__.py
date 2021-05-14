# It's necessary to add the path of 'src/common'
# in 'sys.path' to import 'config', 'engine', 'util' modules
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath('src/common')))
sys.path.append(os.path.dirname(os.path.abspath('src/scrapping')))

import json

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options

from common.config import scrapping_log, gecko_path
from common.engine import Engine
from scraping.honeypot.process import add_search_results_to_logs_buffer
from scraping.scraper import Scraper
from scraping.util import honeypot_keyword


if __name__ == '__main__':

  with open(scrapping_log) as f:
    logs = json.load(f)
    logs_buffer = logs['scrapping']

  user_agent = UserAgent().random

  firefox_options = Options()
  firefox_options.add_argument('-headless')
  firefox_options.add_argument(f'user-agent={user_agent}')

  driver = webdriver.Firefox(executable_path=gecko_path, options=firefox_options)

  for engine_item in Engine:
    engine = engine_item.value

    scraper = Scraper(user_agent, driver, honeypot_keyword, engine, with_omitted_results=False) # TODO change to False
    search_results = scraper.obtain_first_page_search_results()
    logs_buffer = add_search_results_to_logs_buffer(search_results, logs_buffer)

  driver.quit()

  with open(scrapping_log, 'w') as f:
    json.dump(logs, f, indent=4)
