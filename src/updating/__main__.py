# It's necessary to add the path of 'src/common'
# in 'sys.path' to import 'config', 'engine', 'util' modules
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath('src/common')))


import json

from datetime import datetime

from common.config import updating_log
from util import increase_version, index_path


if __name__ == '__main__':

  with open(updating_log) as f:
    logs = json.load(f)
    temp = logs['updating']

  with open(index_path, 'r') as f:
    html = f.read()
    new_html, old_version = increase_version(html)

  updating_item = {
    'version': str(old_version + 1),
    'time': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
  }

  temp.append(updating_item)

  with open(index_path, 'w') as f:
    f.write(new_html)

  with open(updating_log, 'w') as f:
    json.dump(logs, f, indent=4)
