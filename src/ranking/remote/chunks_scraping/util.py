import json
import os
import re


def pretty_dump_json(obj, filename):
  '''
  Dump json 'obj' to file 'filename'.
  Then read this file to
  make long lists from 'obj' be written in one line
  without changing other indents.
  Before:
    [1,
     2,
     ...
    ]
  After:
    [1, 2, ...]
  '''
  with open(filename, 'w') as f:
    json.dump(obj, f, indent=4)
  
  with open(filename, 'r') as f:
    dumped_content = f.read()
  
  pretty_content = re.sub(r',\n            ', ', ', dumped_content)
  pretty_content = re.sub(r'\[\n            ', '[', pretty_content)
  pretty_content = re.sub(r'\n        \]', ']', pretty_content)

  with open(filename, 'w') as f:
    f.write(pretty_content)


def rotate_files(dirpath, file_prefix):
  '''
  Remove file with index '1',
  rename other files subtracting 1
  from each file's index.
  '''
  filepath_prefix = dirpath + file_prefix
  os.remove(f'{filepath_prefix}1')
  filepaths = os.listdir(dirpath)

  for ind in range(2, len(filepaths) + 1):
    filepath = filepath_prefix + str(ind)
    os.rename(filepath, filepath_prefix + str(ind - 1))
