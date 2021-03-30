# It's necessary to add the path of 'src/common'
# in 'sys.path' to import 'config', 'engine', 'util' modules
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath('src/common')))

import json

from common.engine import Engine
from common.config import fusion_dir, scrapping_log, updating_log
from common.util import separator
from visiting import Visiting
from util import get_fusion_log


if __name__ == '__main__':

  with open(updating_log) as f:
    update_log = json.load(f)
    updates = update_log['updating']
  
  with open(scrapping_log) as f:
    scrapping_log = json.load(f)
    scrappings = scrapping_log['scrapping']
  
  for engine_item in Engine:
    engine = engine_item.value
    engine_visiting = Visiting(engine, scrappings, updates)
    
    all_visitors = engine_visiting.get_all_visitors()

    fusion_log = get_fusion_log(engine)
  
    with open(fusion_log, 'w') as f:
      json.dump(all_visitors, f, indent=4)
