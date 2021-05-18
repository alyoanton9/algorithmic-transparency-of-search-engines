######################## Hack to enable local import ########################

import os, sys
sys.path.append(os.path.dirname(os.path.abspath(f'src/enable_local_import')))

from enable_local_import import enable_import
enable_import()

#############################################################################


import json

from common.engine import Engine
from common.config import fusion_logs_dir, logs_dir, scraping_log, updating_log
from fusion.visiting import Visiting


def get_fusion_log(engine: str) -> str:
  '''
  Return the path of fusion log
  by engine's name.
  '''
  return f'{fusion_logs_dir}{engine}.json'


if __name__ == '__main__':
  with open(updating_log) as f:
    update_log = json.load(f)
    updates = update_log['updating']
  
  with open(scraping_log) as f:
    scraping_log = json.load(f)
    scrapings = scraping_log['scraping']
  
  for engine_item in Engine:
    engine = engine_item.value
    engine_visiting = Visiting(engine, scrapings, updates)
    
    all_visitors = engine_visiting.get_all_visitors()

    fusion_log = get_fusion_log(engine)
  
    with open(fusion_log, 'w') as f:
      json.dump(all_visitors, f, indent=4)
