# domain name of honeypot
domain = 'hydromel-chouchenn.eu.org'

# keyword to search by
keyword = 'azpoicvsda'


def is_domain(link) -> bool:
  """
  Check if website is honeypot
  by the given link.
  """
  link = link.strip().strip('/')
  return link == f'https://{domain}' or link == domain