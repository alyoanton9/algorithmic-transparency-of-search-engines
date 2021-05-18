import json
import re

from datetime import date

from common.config import access_logs_dir
from common.engine import Engine
from common.site import honeypot_page_title
from common.full_date import FullDate, full_date_to_log_date, iso_date_to_full_date, log_date_to_full_date


class Visiting():
  current_year = 2021

  access_encoding = 'latin1'


  def __init__(self, engine: str, scrapings: [dict], updates: [dict]):
    self.engine = engine
    self.scrapings = scrapings
    self.updates = updates
    self.access_logs = os.listdir(access_logs_dir)
    self.engine_versions = {engine.value: [] for engine in Engine}


  def get_all_visitors(self) -> [dict]:
    '''
    Return honeypot visitors corresponding to
    honeypot version obtained by the certain search engine.
    In more detail:
    Let's assume search engine detected n'th version
    of the honeypot. Go to updating log and find
    the period of time (from t1 to t2) when n'th version
    was available. Then go to access log and extract
    all visitors from t1 to t2. Return these visitors.
    Example:
      engine: google,
      version: n,
      visitors: [..]
    '''
    all_visitors = []
    index = len(self.scrapings) - 1

    while index >= 0:
      scraping = self.scrapings[index]
      index -= 1

      if scraping['engine'] == self.engine:
        title = scraping['title']

        if title != '':
          version = self._get_title_version_string(title)

          if version != '0' and version not in self.engine_versions[self.engine]:
            self.engine_versions[self.engine].append(version)

            from_date = self._get_date_by_version(version)
            to_date = self._get_date_by_version(str(int(version) + 1))
            
            jsons = self._get_file_jsons(self._get_access_log_by_date(from_date), self.access_encoding)
            visitors = self._get_visitors_by_dates(from_date, to_date, jsons)

            marked_visitors_item = {
              'engine': self.engine,
              'version': version,
              'visitors': visitors
            }

            all_visitors.append(marked_visitors_item)

    return all_visitors


  def _get_title_version_string(self, title_string: str) -> str:
    '''
    Return title's version as string
    which is suffix of given title string.
    Example: 'Abacaba10' -> '10'.
    '''
    version = '0'

    abacaba_match = re.findall(f'{honeypot_page_title}[0-9]*', title_string)
    if len(abacaba_match) > 0:
      version = abacaba_match[0][len(honeypot_page_title) :]
      if version == '':
        version = '0'

    return version


  def _get_access_log_by_date(self, full_date: FullDate) -> str:
    y = full_date.year
    m = full_date.month
    d = full_date.day
  
    searched_date = date(y, m, d)

    for access_log in self.access_logs:
      log_name = access_log[: -len('.log')]
      _, ms, ds = log_name.split('_')
      log_date = date(self.current_year, int(ms), int(ds))

      if log_date <= searched_date and (searched_date - log_date).days <= 6:
        return f'{access_logs_dir}{access_log}'


  def _get_date_by_version(self, version: str) -> FullDate:
    for update in self.updates:
      if update['version'] == version:
        return log_date_to_full_date(update['time'])

    return FullDate()


  def _get_file_jsons(self, filepath: str, encoding: str) -> [dict]:
    '''
    Get the list of jsons from file,
    each line of which is a dict.
    '''
    with open(filepath, encoding=encoding) as f:
      file_lines = f.readlines()

    jsons = []
    for line in file_lines:
      jsons.append(json.loads(line))

    return jsons


  def _get_visitors_by_dates(self, from_date: FullDate, to_date: FullDate, jsons: [dict]) -> [dict]:
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
