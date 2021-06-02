import re


honeypot_page_title = 'Abacaba'

chunk_keyword = 'azpoicvsdu'


def omit_keyword_quotes(string: str) -> str:
  '''
  Omit quotes '"' in the string
  which has 'chunk_keyword' as substring.
  Before:
    '"azpoicvsdu" blabla'
  After:
    'azpoicvsdu blabla' 
  '''
  return re.sub(f'"{chunk_keyword}"', f'{chunk_keyword}', string)


def add_keyword_quotes(string: str) -> str:
  '''
  Opposite to 'omit_keyword_quotes'.
  '''
  return re.sub(f'{chunk_keyword}', f'"{chunk_keyword}"', string) 
