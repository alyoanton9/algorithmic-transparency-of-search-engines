from common.config import data_www_dir
from common.site import chunk_keyword

import itertools
import re

from rank_bm25 import BM25, BM25L, BM25Okapi, BM25Plus


chunks_number = 200

documents_dir = f'{data_www_dir}chunks/'

orders_dir = 'temp/ranking/local/doc_orders/'

doc_orders_filename = f'{orders_dir}/bm25.json'

max_word_len = 4


def omit_signs(string: str):
  string = re.sub(r'[^A-Za-z0-9’ ]+', ' ', string)
  return string


def make_order_filename(words_in_query: int) -> str:
  filename_suffix = '_queries.json'
  if words_in_query == 1:
    local_filename = '1word' + filename_suffix
  elif words_in_query == 2:
    local_filename = '2words' + filename_suffix

  return orders_dir + local_filename


def make_chunk_filename(index: int) -> str:
  return documents_dir + 'chunk_' + str(index) + '.html'


def process_file_content(filename: str) -> str:
  '''
  Omit file's html tags,
  delete all signs (except apostrophes)
  from the file
  and return its contents as a string.
  '''
  start_line_of_content = 9
  end_line_of_content = -3
  with open(filename, 'r') as f:
    file_lines = f.readlines()
    file_lines = file_lines[start_line_of_content : end_line_of_content]
    file_list = list(itertools.chain.from_iterable(file_lines))
    file_str_with_signs = ''.join(file_list)
    file_str = omit_signs(file_str_with_signs)

  return file_str


def tokenize_corpus(documents: [str]) -> [[str]]:
  return [document.split() for document in documents]


def tokenize_query(query: str) -> [str]:
  return query.split()


def get_documents_order(query: str, bm25: BM25, ind: int) -> [int]:
  documents_scores = bm25.get_scores(query)
  chunk_indexes = list(range(1, chunks_number + 1))

  score_with_index = list(
    zip(documents_scores, chunk_indexes)
  )

  sorted_scores = sorted(score_with_index)
  order = [index for _, index in sorted_scores]
  
  with open(f'{orders_dir}/documents_order.log', 'a') as f:
    bm25_name = 'BM25'
    if ind == 0:
      bm25_name += 'L'
    if ind == 1:
      bm25_name += 'OKapi'
    if ind == 2:
      bm25_name += 'Plus'
    f.write(f'query: {query}\nbm25: {bm25_name}\nscore with index: {score_with_index}\norder: {list(reversed(order))}\n\n')
  
  return list(reversed(order))


def all_different(lists: [int]) -> bool:
  '''
  Check if all given lists
  are different collectively.
  '''
  different = True
  for i in range(len(lists)):
    for j in range(i + 1, len(lists)):
      if lists[i] == lists[j]:
        different = False
  
  return different


def process_document(tokenized_corpus: [[str]], tokenized_document: [str], buffer: [dict], queries: set[str]) -> [dict]:
  prev_word = ''
  word_ind = 1
  words_total = len(tokenized_document)

  for word in tokenized_document:
    if word != chunk_keyword and '’' not in word and len(word) >= max_word_len:
      query = chunk_keyword + ' ' + prev_word + ' ' + word
      # query = chunk_keyword + ' ' + word
      
      tokenized_query = tokenize_query(query)

      orders = []

      for ind, bm25 in enumerate([
        BM25L(tokenized_corpus),
        BM25Okapi(tokenized_corpus),
        BM25Plus(tokenized_corpus)
      ]):
        documents_order = get_documents_order(tokenized_query, bm25, ind)
        orders.append(documents_order)
      
      if all_different(orders) and (prev_word not in queries) and (word not in queries):
        query_entry = {
          'query': query,
          'orders': list(zip(
            ['BM25L', 'BM25Okapi', 'BM25Plus'],
            orders
          ))
        }

        buffer.append(query_entry)
        queries.add(prev_word)
        queries.add(word)
      
      prev_word = word

    if word_ind % 100 == 0:
      print(f'{word_ind}/{words_total} words processed')

    word_ind += 1
  
  return buffer
