# It's necessary to add the path of 'src/common'
# in 'sys.path' to import 'config', 'engine', 'util' modules
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath('src/common')))

import json

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options

from processing import Scrapping
from util import keyword

from common.config import scrapping_log, gecko_path
from common.engine import Engine


if __name__ == '__main__':

  with open(scrapping_log) as f:
    logs = json.load(f)
    temporary_log_list = logs['scrapping']

  firefox_options = Options()
  user_agent = UserAgent().random
  firefox_options.add_argument("-headless")
  firefox_options.add_argument(f'user-agent={user_agent}')

  driver = webdriver.Firefox(executable_path=gecko_path, options=firefox_options)

  for engine_item in Engine:
    engine = engine_item.value
    scrapping = Scrapping(user_agent, driver, keyword, engine)
    scrapping.append_scrapping_result_to_logs(temporary_log_list)

  driver.quit()

  with open(scrapping_log, 'w') as f:
    json.dump(logs, f, indent=4)
