# It's necessary to add the path of 'src/scraping'
# in 'sys.path' to import 'scraper', 'chunks' modules
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath('src/common')))
sys.path.append(os.path.dirname(os.path.abspath('src/scraping')))

import re

from scraping.scraper import SearchResultItem
from scraping.chunks.prefix_mapping import chunk_prefixes, chunk_prefix_len
from scraping.util import chunk_keyword


def omit_keyword_quotes(string) -> str:
  '''
  Omit quotes '"' in the string
  which has 'chunk_keyword' as substring.
  Before:
    '"azpoicvsdu" blabla'
  After:
    'azpoicvsdu blabla' 
  '''
  return re.sub(f'"{chunk_keyword}"', f'{chunk_keyword}', string)


def find_chunk_index(search_result_item: SearchResultItem) -> int:
  chunk_index = -1

  title = omit_keyword_quotes(search_result_item.title)
  link = search_result_item.link

  chunk_match = re.search(r'(chunk(_)?)(\d+)', title)
  if chunk_match != None:
    chunk_index = int(chunk_match.group(3))

  else:
    title_prefix = title[: chunk_prefix_len]
  
    if title_prefix in chunk_prefixes.keys():
      chunk_index = chunk_prefixes[title_prefix]

    else:
      chunk_match = re.search(r'(chunk_)(\d+)', link)

      if chunk_match != None:
        chunk_index = int(chunk_match.group(2))
  
      else:
        print('no appropriate index for', title)

  return chunk_index
