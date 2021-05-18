from common.config import data_www_dir
from common.site import chunk_keyword

import itertools

from rank_bm25 import BM25, BM25L, BM25Okapi, BM25Plus


chunks_number = 200

documents_dir = f'{data_www_dir}chunks/'

orders_dir = 'src/ranking/local/doc_orders/'


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
  Delete all extra whitespaces from the file,
  omit file's html tags,
  and return its contents as a string.
  '''
  start_line_of_content = 9
  end_line_of_content = -3
  with open(filename, 'r') as f:
    file_lines = f.readlines()
    file_lines = file_lines[start_line_of_content : end_line_of_content]
    file_list = list(itertools.chain.from_iterable(file_lines))
    file_str = ''.join(file_list)

  return file_str


def tokenize_corpus(documents: [str]) -> [[str]]:
  return [document.split() for document in documents]


def tokenize_query(query: str) -> [str]:
  return query.split()


def get_documents_order(query: str, bm25: BM25) -> [int]:
  documents_scores = bm25.get_scores(query)
  chunk_indexes = list(range(1, chunks_number + 1))

  score_with_index = list(
    zip(documents_scores, chunk_indexes)
  )

  sorted_scores = sorted(score_with_index)
  order = [index for _, index in sorted_scores]

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


def process_document(tokenized_corpus: [[str]], tokenized_document: [str], queries_buffer: [dict]) -> [dict]:
  # prev_word = ''
  word_ind = 1

  for word in tokenized_document:
    if word != chunk_keyword:
      # query = chunk_keyword + ' ' + prev_word + ' ' + word
      query = chunk_keyword + ' ' + word
      
      tokenized_query = tokenize_query(chunk_keyword + ' ' + word)

      orders = []

      for bm25 in [
        BM25L(tokenized_corpus),
        BM25Okapi(tokenized_corpus),
        BM25Plus(tokenized_corpus)
      ]:
        documents_order = get_documents_order(tokenized_query, bm25)
        orders.append(documents_order)
      
      if all_different(orders):
        query_entry = {
          'query': query,
          'orders': list(zip(
            ['BM25L', 'BM25Okapi', 'BM25Plus'],
            orders
          ))
        }

        queries_buffer.append(query_entry)
      
      word_ind += 1
  
  return queries_buffer
