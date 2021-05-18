import re

from common.site import honeypot_page_title


# TODO consider making more generic
# like 'increase_number_inside_string'.
def increase_version(html_code: str) -> (str, int):
  title_version_regex = f'{honeypot_page_title}[0-9]*'
  title_version_match = re.search(title_version_regex, html_code)

  title_tail = title_version_match.group(0)
  title_tail = title_tail[len(honeypot_page_title) :]

  title_version = int(title_tail) if len(title_tail) > 0 else 0

  new_html_code = re.sub(title_version_regex, f'{honeypot_page_title}{title_version + 1}', html_code)

  return new_html_code, title_version
