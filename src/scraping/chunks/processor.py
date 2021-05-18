import re

from common.site import omit_keyword_quotes
from scraping.chunks.prefix_mapping import chunk_prefixes, chunk_prefix_len
from scraping.scraper import SearchResultItem


def find_chunk_index(search_result_item: SearchResultItem) -> int:
  '''
  Return index of chunk document
  by title and link extracted from SERP:
  Example:
    link: https://hydromel-chouchenn.eu.org/chunks/chunk_83
    index: 83

    title: azpoicvsdu un mt mll. uf ehq iull rqoquvq yq, ea ygoh thq ...
    index: 43
    ^ Because chunk_prefixes = {... 'azpoicvsdu un mt mll' : 43 ...}
  '''
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
