######################## Hack to enable local import ########################

import os, sys
sys.path.append(os.path.dirname(os.path.abspath(f'src/enable_local_import')))

from enable_local_import import enable_import
enable_import()

#############################################################################


import json

from datetime import datetime

from common.config import custom_date_format, index_path, updating_log
from updating.util import increase_version


if __name__ == '__main__':
  with open(updating_log) as f:
    logs = json.load(f)
    buffer = logs['updating']

  with open(index_path, 'r') as f:
    html_code = f.read()
    new_html_code, old_version = increase_version(html_code)

  updating_item = {
    'version': str(old_version + 1),
    'time': datetime.now().strftime(format=custom_date_format)
  }

  buffer.append(updating_item)

  with open(index_path, 'w') as f:
    f.write(new_html_code)

  with open(updating_log, 'w') as f:
    json.dump(logs, f, indent=4)
