import json
import re


def pretty_dump_json(obj, filename: str):
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
