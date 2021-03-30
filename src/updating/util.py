# It's necessary to add the path of 'src/common'
# in 'sys.path' to import 'config', 'engine', 'util' modules
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath('src/common')))


import re

from common.util import page_title, separator


# path of 'index.html'
index_path = 'data' + separator + 'www' + separator + 'index.html'

def increase_version(html) -> (str, int):
  title_version_regex = f'{page_title}[0-9]*'
  match = re.search(title_version_regex, html)
  title_tail = match.group(0)[len(page_title) :]
  n = int(title_tail) if len(title_tail) > 0 else 0
  new_html = re.sub(title_version_regex, f'{page_title}{n+1}', html)
  return new_html, n

