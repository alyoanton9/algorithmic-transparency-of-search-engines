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
from util import is_domain

@dataclass
class ScrappingResult:
  position: int = -1
  title: str = ''
  captcha: bool = False
  no_results: bool = False


class Scrapping():
  
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


  def __init__(self, user_agent, driver, query, engine):
    self.user_agent = user_agent
    self.query = query
    self.engine = engine
    self.soup = self._make_soup(driver)


  def _make_soup(self, driver) -> BeautifulSoup:
    url = f'{self.search_refs[self.engine]}{self.query}'
    driver.get(url)
    time.sleep(3)
    return BeautifulSoup(driver.page_source, 'lxml')


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
        'time': datetime.now().strftime("%d/%m/%Y %H:%M:%S") # formated current time
      }

      temporary_log_list.append(scrapping_item)
