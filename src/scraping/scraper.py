# It's necessary to add the path of 'src/common'
# in 'sys.path' to import 'config', 'engine', 'util' modules
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath('src/common')))

import time

from bs4 import BeautifulSoup
from dataclasses import dataclass
from datetime import datetime

from common.engine import Engine
from .util import is_honeypot


@dataclass
class SearchResultItem:
  title: str = ''
  link: str = ''


@dataclass
class ScrapeResult:
  items: [SearchResultItem]
  captcha: bool = False
  no_results: bool = False

  def append_scrape_result(self, other):
    if other.captcha == True:
      self.captcha = True

    elif other.no_results == True:
      self.no_results = True
    
    else:
      self.items += other.items


@dataclass
class SearchResults:
  engine: str # TODO change type to Engine everywhere
  query: str
  items: [SearchResultItem]
  captcha: bool = False
  no_results: bool = True
  internal_log: str = ''


class Scraper():
  
  search_refs = {
    Engine.GOOGLE.value: 'https://www.google.com/search?q=',
    Engine.STARTPAGE.value: 'https://www.startpage.com/do/dsearch?query=',
    Engine.BING.value: 'https://www.bing.com/search?q=',
    Engine.DUCKDUCKGO.value: 'https://duckduckgo.com/?q=',
    Engine.ASK.value: 'https://www.ask.com/web?o=0&l=dir&qo=homepageSearchBox&q=',
    Engine.MOJEEK.value: 'https://www.mojeek.com/search?q=',
    Engine.EXALEAD.value: 'http://www.exalead.com/search/web/results/?q=',
    Engine.LYCOS.value: 'https://search.lycos.com/web/?q=',
    Engine.YANDEX.value: 'https://yandex.ru/search/?text=',
    Engine.SWISSCOWS.value: 'https://swisscows.com/web?query='
  }

  secs_to_load_page = 3


  def __init__(self, user_agent, driver, query, engine, with_omitted_results):
    self.user_agent = user_agent
    self.driver = driver
    self.query = query
    self.engine = engine
    self.soup = self._make_soup(with_omitted_results)


  def obtain_first_page_search_results(self) -> SearchResults:
    return self._obtain_search_results(all_pages=False)
  

  def obtain_all_pages_search_results(self) -> SearchResults:
    return self._obtain_search_results(all_pages=True)


  def _make_soup(self, with_omitted_results) -> BeautifulSoup:
    url = f'{self.search_refs[self.engine]}{self.query}'
    if with_omitted_results:
      if self.engine == Engine.GOOGLE.value:
        url += '&filter=0'

    self.driver.get(url)
    time.sleep(self.secs_to_load_page)

    return BeautifulSoup(self.driver.page_source, 'lxml')


  def _obtain_all_pages_scrape_result(self) -> ScrapeResult:
    scrape_results = ScrapeResult(items=[])
    soup = self.soup

    while soup != None: #TODO remove != None
      scrape_results.append_scrape_result(self._scrape())
      soup = self._get_next_soup()

    return scrape_results


  # TODO add type of func argument
  def _obtain_search_results(self, all_pages: bool) -> SearchResults:
    scrape_result = ScrapeResult(items=[])
    internal_exception = ''

    try:
      if all_pages:
        while self.soup != None: #TODO remove != None
          scrape_result.append_scrape_result(self._scrape())
          self.soup = self._get_next_soup()
      else:
        scrape_result = self._scrape()

    except Exception as e:
      internal_exception = str(e)
    
    finally:
      internal_log = internal_exception
      if scrape_result.captcha:
        internal_log += ' | User agent: ' + self.user_agent

      search_results = SearchResults(
        engine=self.engine,
        query=self.query,
        items=scrape_result.items,
        captcha=scrape_result.captcha,
        no_results=scrape_result.no_results,
        internal_log=internal_log
      )

      return search_results


  def _get_next_soup(self) -> BeautifulSoup:
    try:
      if self.engine == Engine.GOOGLE.value:
        self.driver.find_element_by_id('pnnext').click()

      if self.engine == Engine.STARTPAGE.value:
        self.driver.find_element_by_class_name('next').click()

      if self.engine == Engine.YANDEX.value:
        self.driver.find_element_by_class_name('pager__item_kind_next').click()

    except: # no next pages
      return None

    time.sleep(self.secs_to_load_page)
    soup = BeautifulSoup(self.driver.page_source, 'lxml')

    return soup


  def _scrape(self) -> ScrapeResult:
    if self.engine == Engine.GOOGLE.value:
      return self._scrape_google()
    
    if self.engine == Engine.STARTPAGE.value:
      return self._scrape_startpage()

    if self.engine == Engine.BING.value:
      return self._scrape_bing()
    
    if self.engine == Engine.DUCKDUCKGO.value:
      return self._scrape_startpage()

    if self.engine == Engine.ASK.value:
      return self._scrape_ask()
    
    if self.engine == Engine.MOJEEK.value:
      return self._scrape_mojeek()

    if self.engine == Engine.EXALEAD.value:
      return self._scrape_exalead()
    
    if self.engine == Engine.LYCOS.value:
      return self._scrape_lycos()

    if self.engine == Engine.YANDEX.value:
      return self._scrape_yandex()

    if self.engine == Engine.SWISSCOWS.value:
      return self._scrape_swisscows()


  def _scrape_google(self) -> ScrapeResult:
    if self.soup.find(name='form', id='captcha-form') != None:
        return ScrapeResult(items=[], captcha=True)
        
    else:
      return self._common_scrape(
          title_tag_name='h3',
          title_class='DKV0Md',
          link_tag_name='div',
          link_class='NJjxre'
      )


  def _scrape_startpage(self) -> ScrapeResult:
    if self.soup.find(name='div', class_='show-results') == None:
      return ScrapeResult(items=[], captcha=True)

    else:
      return self._common_scrape(
          title_tag_name='a',
          title_class='w-gl__result-title',
          link_tag_name='a',
          link_class='w-gl__result-url',
      )


  # TODO think about making generic
  def _scrape_bing(self) -> ScrapeResult:
    titles = self.soup.find_all(name='li', class_='b_algo')
    titles = list(
      map(lambda s: s.find(name='h2').text, titles)
    )
  
    links = self.soup.find_all(name='div', class_='b_attribution')
    filtered_links = filter(
      lambda s: s.find(name='div', class_='b_adurl') == None,
      links
    )
    links = list(
      map(lambda s: s.text, filtered_links)
    )

    search_result_items_zipped = list(
      zip(titles, links)
    )
    search_result_items = [
      SearchResultItem(title, link)
      for title, link in search_result_items_zipped
    ]

    return ScrapeResult(items=search_result_items)


  def _scrape_duckduckgo(self) -> ScrapeResult:
    return self._common_scrape(
        title_tag_name='a',
        title_class='result__a',
        link_tag_name='a',
        link_class='result__url'
    )


  def _scrape_ask(self) -> ScrapeResult:
    return self._common_scrape(
        title_tag_name='a',
        title_class='result-link',
        link_tag_name='p',
        link_class='PartialSearchResults-item-url'
    )


  def _scrape_mojeek(self) -> ScrapeResult:
    if self.soup.find(name='div', class_='results') == None:
      return ScrapeResult(items=[], no_results=True)

    else:
      return self._common_scrape(
          title_tag_name='a',
          title_class='ob',
          link_tag_name='p',
          link_class='i'
      )


  def _scrape_exalead(self) -> ScrapeResult:
    if self.soup.body.find(name='div', id='content').find(name='form') != None:
      return ScrapeResult(items=[], captcha=True)

    elif self.soup.body.find(name='div', id='noResults') != None:
      return ScrapeResult(items=[], no_results=True)

    else:
      return self._common_scrape(
          title_tag_name='a',
          title_class='title',
          link_tag_name='a',
          link_class='ellipsis'
      )


  def _scrape_lycos(self) -> ScrapeResult:
    return self._common_scrape(
      title_tag_name='a',
      title_class='result-link',
      link_tag_name='span',
      link_class='result-url'
    )


  def _scrape_yandex(self) -> ScrapeResult:
    return self._common_scrape(
      title_tag_name='div',
      title_class='organic__url-text',
      link_tag_name='a',
      link_class='link_theme_outer'
    )


  def _scrape_swisscows(self) -> ScrapeResult:
    return self._common_scrape(
      title_tag_name='h2',
      title_class='title',
      link_tag_name='cite',
      link_class='site'
    )


  def _common_scrape(self, title_tag_name, title_class, link_tag_name, link_class) -> ScrapeResult:
    titles = self.soup.find_all(name=title_tag_name, class_=title_class)
    titles = list(
      map(lambda s: s.text, titles)
    )
  
    links = self.soup.find_all(name=link_tag_name, class_=link_class)
    links = list(
      map(lambda s: s.text, links)
    )

    search_result_items_zipped = list(
      zip(titles, links)
    )
    search_result_items = [
      SearchResultItem(title, link)
      for title, link in search_result_items_zipped
    ]

    return ScrapeResult(items=search_result_items)

'''
  def _find_position(self, links) -> int:
    for i in range(len(links)):
      if is_domain(links[i]):
        return i + 1
    return -1


  def _detect_domain_position_and_title(self, link_tag, link_class, title_tag, title_class) -> (int, str):
    title = ''

    all_links_on_page = self.soup.find_all(name=link_tag, class_=link_class)
    all_links_on_page = map(lambda s: s.text, all_links_on_page)
    all_links_on_page = list(all_links_on_page)

    position = self._find_position(all_links_on_page)

    all_titles_on_page = self.soup.find_all(name=title_tag, class_=title_class)
    all_titles_on_page = map(lambda s: s.text, all_titles_on_page)
    all_titles_on_page = list(all_titles_on_page)

    if position != -1:
      title = all_titles_on_page[position - 1]
    
    return position, title


  def _get_scrapping_result_of_google(self) -> ScrappingResult:
    if self.soup.find(name='form', id='captcha-form') != None:
        return ScrappingResult(captcha=True)

    else:
        position, title = self._detect_domain_position_and_title(
          link_tag='div',
          link_class='NJjxre',
          title_tag='h3',
          title_class='DKV0Md'
        )
        return ScrappingResult(position, title)


  def _get_scrapping_result_of_startpage(self) -> ScrappingResult:
    position, title = self._detect_domain_position_and_title(
      link_tag='a',
      link_class='w-gl__result-url',
      title_tag='a',
      title_class='w-gl__result-title'
    )

    return ScrappingResult(position, title)


  def _get_scrapping_result_of_bing(self) -> ScrappingResult:
    all_links_on_page = self.soup.find_all(name='div', class_='b_attribution')
    all_links_on_page = filter(lambda t: t.find(name='div', class_='b_adurl') == None, all_links_on_page)
    all_links_on_page = map(lambda s: s.text, all_links_on_page)

    position = self._find_position(list(all_links_on_page))

    all_titles_on_page = self.soup.find_all(name='li', class_='b_algo')
    all_titles_on_page = map(lambda s: s.find(name='h2').text, all_titles_on_page)
    all_titles_on_page = list(all_titles_on_page)

    if position != -1:
      title = all_titles_on_page[position - 1]
      return ScrappingResult(position, title)
    
    else:
      return ScrappingResult()


  def _get_scrapping_result_of_duckduckgo(self) -> ScrappingResult:
    position, title = self._detect_domain_position_and_title(
      link_tag='a',
      link_class='result__url',
      title_tag='a',
      title_class='result__a'
    )

    return ScrappingResult(position, title)


  def _get_scrapping_result_of_ask(self) -> ScrappingResult:
    position, title = self._detect_domain_position_and_title(
      link_tag='p',
      link_class='PartialSearchResults-item-url',
      title_tag='a',
      title_class='result-link'
    )

    return ScrappingResult(position, title)


  def _get_scrapping_result_of_mojeek(self) -> ScrappingResult:
    if self.soup.find(name='div', class_='results') == None:
      return ScrappingResult(no_results=True)

    else:
      position, title = self._detect_domain_position_and_title(
        link_tag='p',
        link_class='i',
        title_tag='a',
        title_class='ob'
      )
      return ScrappingResult(position, title)


  def _get_scrapping_result_of_exalead(self) -> ScrappingResult:
    if self.soup.body.find(name='div', id='content').find(name='form') != None:
      return ScrappingResult(captcha=True)

    elif self.soup.body.find(name='div', id='noResults') != None:
      return ScrappingResult(no_results=True)

    else:
      position, title = self._detect_domain_position_and_title(
        link_tag='a',
        link_class='ellipsis',
        title_tag='a',
        title_class='title'
      )
      return ScrappingResult(position, title)


  def _get_scrapping_result_of_lycos(self) -> ScrappingResult:
    position, title = self._detect_domain_position_and_title(
      link_tag='span',
      link_class='result-url',
      title_tag='a',
      title_class='result-link'
    )

    return ScrappingResult(position, title)


  def _get_scrapping_result_of_yandex(self) -> ScrappingResult:
    if self.soup.find('div', class_='captcha-wrapper') != None:
      return ScrappingResult(captcha=True)

    else:
      position, title = self._detect_domain_position_and_title(
        link_tag='a',
        link_class='link_theme_outer',
        title_tag='div',
        title_class='organic__url-text'
      )
      return ScrappingResult(position, title)


  def _get_scrapping_result_of_swisscows(self) -> ScrappingResult:
    position, title = self._detect_domain_position_and_title(
      link_tag='cite',
      link_class='site',
      title_tag='h2',
      title_class='title'
    )

    return ScrappingResult(position, title)


  def append_scrapping_result_to_logs(self, temporary_log_list) -> None:
    scrapping_result = ScrappingResult()
    errors = ''

    try:
      if self.engine == Engine.GOOGLE.value:
        scrapping_result = self._get_scrapping_result_of_google()
      if self.engine == Engine.STARTPAGE.value:
        scrapping_result = self._get_scrapping_result_of_startpage()
      if self.engine == Engine.BING.value:
        scrapping_result = self._get_scrapping_result_of_bing()
      if self.engine == Engine.DUCKDUCKGO.value:
        scrapping_result = self._get_scrapping_result_of_duckduckgo()
      if self.engine == Engine.ASK.value:
        scrapping_result = self._get_scrapping_result_of_ask()
      if self.engine == Engine.MOJEEK.value:
        scrapping_result = self._get_scrapping_result_of_mojeek()
      if self.engine == Engine.EXALEAD.value:
        scrapping_result = self._get_scrapping_result_of_exalead()
      if self.engine == Engine.LYCOS.value:
        scrapping_result = self._get_scrapping_result_of_lycos()
      if self.engine == Engine.YANDEX.value:
        scrapping_result = self._get_scrapping_result_of_yandex()
      if self.engine == Engine.SWISSCOWS.value:
        scrapping_result = self._get_scrapping_result_of_swisscows()

    except Exception as e:
      errors = str(e)

    finally:
      scrapping_item = {
        'engine': self.engine,
        'query': self.query,
        'captcha': str(scrapping_result.captcha),
        'no_results': str(scrapping_result.no_results),
        'position': str(scrapping_result.position),
        'title': scrapping_result.title,
        'errors': errors if not scrapping_result.captcha else errors + ' | User agent: ' + self.user_agent,
        'time': datetime.now().strftime("%d/%m/%Y %H:%M:%S") # formatted current time
      }

      temporary_log_list.append(scrapping_item)
'''