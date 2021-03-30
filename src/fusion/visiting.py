# It's necessary to add the path of 'src/common'
# in 'sys.path' to import 'config', 'engine', 'util' modules
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath('src/common')))

import json
import re

from datetime import date

from common.config import access_dir
from common.engine import Engine
from common.util import FullDate, full_date_to_log_date, iso_date_to_full_date, log_date_to_full_date, separator
from util import get_title_version, get_jsons


class Visiting():

  current_year = 2021

  access_encoding = 'latin1'


  def __init__(self, engine, scrappings, updates):
    self.engine = engine
    self.scrappings = scrappings
    self.updates = updates
    self.access_logs = os.listdir(access_dir)
    self.engine_versions = {engine.value: [] for engine in Engine}


  def get_access_log_by_date(self, full_date) -> str:
    y = full_date.year
    m = full_date.month
    d = full_date.day
  
    searched_date = date(y, m, d)

    for access_log in self.access_logs:
      log_name = access_log[: -len('.log')]
      _, ms, ds = log_name.split('_')
      log_date = date(self.current_year, int(ms), int(ds))

      if log_date <= searched_date and (searched_date - log_date).days <= 6:
        return access_dir + separator + access_log


  def get_date_by_version(self, version) -> FullDate:
    for update in self.updates:
      if update['version'] == version:
        return log_date_to_full_date(update['time'])

    return FullDate()


  def get_visitors_by_dates(self, from_date, to_date, jsons) -> [dict]:
    visitors = []

    for j in jsons:
      date = iso_date_to_full_date(j['time_iso8601'])

      if from_date <= date and date <= to_date:
        remote_addr = j['remote_addr']
        remote_port = j['remote_port']
        user_agent = j['http_user_agent']
        uri = j['uri']
        visitors.append({
          'remote_addr': remote_addr,
          'remote_port': remote_port,
          'user_agent': user_agent,
          'uri': uri,
          'time': full_date_to_log_date(date)
        })

    return visitors


  def get_all_visitors(self) -> [dict]:
    all_visitors = []
    index = len(self.scrappings) - 1

    while index >= 0:
      scrapping = self.scrappings[index]
      index -= 1

      if scrapping['engine'] == self.engine:
        title = scrapping['title']

        if title != '':
          version = get_title_version(title)

          if version != '0' and version not in self.engine_versions[self.engine]:
            self.engine_versions[self.engine].append(version)
            from_date = self.get_date_by_version(version)
            to_date = self.get_date_by_version(str(int(version) + 1))
            jsons = get_jsons(self.get_access_log_by_date(from_date), self.access_encoding)
            visitors = self.get_visitors_by_dates(from_date, to_date, jsons)

            marked_visitors_item = {
                'engine': self.engine,
                'version': version,
                'visitors': visitors
            }

            all_visitors.append(marked_visitors_item)

    return all_visitors
