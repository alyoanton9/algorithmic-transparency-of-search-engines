######################## Hack to enable local import ########################

import os, sys
sys.path.append(os.path.dirname(os.path.abspath(f'src/enable_local_import')))

from enable_local_import import enable_import
enable_import()

#############################################################################


import json

from ranking.local.diff_searching.processor import chunks_number, make_chunk_filename, make_order_filename, process_document, process_file_content, tokenize_corpus


if __name__ == '__main__':
  documents = []
  queries_buffer = []

  for i in range(1, chunks_number + 1):
    filename = make_chunk_filename(i)
    document = process_file_content(filename)
    documents.append(document)
  
  tokenized_corpus = tokenize_corpus(documents)

  # We didn't process each file actually,
  # because we only need ~50-100 queries
  # for our dataset.
  # Thus, we're fine with processing only 1 document.
  for tokenized_document in tokenized_corpus:
    queries_buffer = process_document(tokenized_corpus, tokenized_document, queries_buffer)

  order_filename = make_order_filename(words_in_query=1)
  with open(order_filename, 'w') as f:
    json.dump(queries_buffer, f, indent=4)
