import os

from dataclasses import dataclass


# path separator
separator = os.path.sep

page_title = 'Abacaba'


@dataclass
class FullDate:
  year: int = 0
  month: int = 0
  day: int = 0
  hour: int = 0
  minute: int = 0
  second: int = 0

  def __ge__(self, other):
    self_tuple = (self.year, self.month, self.day, self.hour, self.minute, self.second)
    other_tuple = (other.year, other.month, other.day, other.hour, other.minute, other.second)
    return self_tuple >= other_tuple


def log_date_to_full_date(log_date) -> FullDate:
  """
  Convert string date from logs
  to FullDate.
  Example: 26/02/2021 07:55:09 -> FullDate(2021, 2, 26, 7, 55, 9).
  """
  date, time = log_date.split(' ')
  d, m, y = map(int, date.split('/'))
  H, M, S = map(int, time.split(':'))
  return FullDate(year=y, month=m, day=d, hour=H, minute=M, second=S)


def iso_date_to_full_date(iso_date) -> FullDate:
  """
  Convert string date in iso format
  to FullDate.
  Example: 2021-03-06T23:29:18+00:00 -> FullDate(2021, 3, 6, 23, 29, 18).
  """
  date, time = iso_date.split('T')
  time = time.split('+')[0]
  y, m, d = map(int, date.split('-'))
  H, M, S = map(int, time.split(':'))
  return FullDate(year=y, month=m, day=d, hour=H, minute=M, second=S)


def full_date_to_log_date(full_date) -> str:
  """
  Convert FullDate
  to string "log-formated" date.
  Example: FullDate(2021, 3, 29, 13, 47, 5) -> 29/03/2021 13:47:05.
  """
  y = full_date.year
  m = full_date.month
  d = full_date.day
  H = full_date.hour
  M = full_date.minute
  S = full_date.second
  ys, ms, ds, Hs, Ms, Ss = map(lambda t: '{:0>2}'.format(t), [y, m, d, H, M, S])
  return ds + '/' + ms + '/' + ys + ' ' + Hs + ':' + Ms + ':' + Ss
