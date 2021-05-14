honeypot_domain = 'hydromel-chouchenn.eu.org'
honeypot_keyword = 'azpoicvsda'

chunk_keyword = 'azpoicvsdu'


def is_honeypot(link) -> bool:
  """
  Check if website is honeypot
  by the given link.
  """
  link = link.strip().strip('/')
  return link == f'https://{honeypot_domain}' or link == honeypot_domain
