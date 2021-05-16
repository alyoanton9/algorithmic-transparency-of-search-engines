from enum import Enum, auto


class RankingFunction(Enum):
  '''
  Ranking functions implemented in
  'rank_bm25' library that are
  used locally in this work.
  '''
  BM25L = auto()
  BM25Okapi = auto()
  BM25Plus = auto()
