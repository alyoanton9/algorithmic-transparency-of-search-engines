# It's necessary to add the local paths 'src/*'
# to 'sys.path' to enable importing modules
# of 'src' packages to other modules in 'src'.
import os
import sys

module_names = ['common', 'fusion', 'ranking', 'scraping', 'updating']


def enable_import():
  for module_name in module_names:
    sys.path.append(os.path.dirname(os.path.abspath(f'src/{module_name}')))
