# It's necessary to add the path of 'src/common'
# in 'sys.path' to import 'config', 'engine', 'util' modules
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath('src/common')))

import json
import re

from common.config import logs_dir
from common.util import page_title, separator


def get_fusion_log(engine) -> str:
  """
  Return path of fusion log
  by engine name.
  """
  return logs_dir + separator + 'fusion' + separator + f'{engine}.json'

# TODO check type
def get_jsons(filepath, encoding) -> [dict]:
  """
  Get list of jsons from file,
  each line of which is a dict.
  """
  with open(filepath, encoding=encoding) as f:
    file_lines = f.readlines()
  
  jsons = []
  for line in file_lines:
    jsons.append(json.loads(line))

  return jsons


def get_title_version(title_string):
  """
  Return title's version as string
  which is suffix of given title string.
  Example: 'Abacaba10' -> '10'.
  """
  version = '0'

  abacaba_match = re.findall(f'{page_title}[0-9]*', title_string)
  if len(abacaba_match) > 0:
    version = abacaba_match[0][len(page_title) :]
    if version == '':
      version = '0'

  return version
