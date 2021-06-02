######################## Hack to enable local import ########################

import os, sys
sys.path.append(os.path.dirname(os.path.abspath(f'src/enable_local_import')))

from enable_local_import import enable_import
enable_import()

#############################################################################


import json

from ranking.local.diff_searching.processor import chunks_number, doc_orders_filename, make_chunk_filename, process_document, process_file_content, tokenize_corpus


if __name__ == '__main__':
  documents = []

  with open(doc_orders_filename, 'r') as f:
    queries_buffer = json.load(f)

  for i in range(1, chunks_number + 1):
    filename = make_chunk_filename(i)
    document = process_file_content(filename)
    documents.append(document)
  
  tokenized_corpus = tokenize_corpus(documents)
  found_queries = set()

  # We didn't process each file actually,
  # because we only need ~100-300 queries
  # for our dataset.
  # Thus, we're fine with processing only ~10 documents (1-word and 2-words).
  for ind, tokenized_document in enumerate(tokenized_corpus[:5]):
    print(f'document №{ind + 1} is being processed...')
    queries_buffer = process_document(tokenized_corpus, tokenized_document, queries_buffer, found_queries)

  with open(doc_orders_filename, 'w') as f:
    json.dump(queries_buffer, f, indent=4)
