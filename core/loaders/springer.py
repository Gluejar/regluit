import re
import requests

from bs4 import BeautifulSoup
from urlparse import urljoin
from django.conf import settings

from regluit.core.validation import identifier_cleaner
from regluit.core.bookloader import add_from_bookdatas

from .scrape import BaseScraper, CONTAINS_CC

MENTIONS_CC = re.compile(r'CC BY(-NC)?(-ND|-SA)?', flags=re.I)
HAS_YEAR = re.compile(r'(19|20)\d\d')

class SpringerScraper(BaseScraper):
    def get_downloads(self):
        for dl_type in ['epub', 'mobi', 'pdf']:
            download_el = self.doc.find('a', title=re.compile(dl_type.upper()))
            if download_el:
                value = download_el.get('href') 
                if value:
                    value = urljoin(self.base, value)
                    self.set('download_url_{}'.format(dl_type), value)

    def get_description(self):
        desc = self.doc.select_one('#book-description')
        if desc:
            value = ''
            for div in desc.contents:
                text = div.string.replace(u'\xa0', u' ') if div.string else None
                if text:
                    value = u'{}<p>{}</p>'.format(value, text) 
            self.set('description', value)

    def get_keywords(self):
        value = []
        for kw in self.doc.select('.Keyword'):
            value.append(kw.text.strip())
        if value:
            if 'Open Access' in value:
                value.remove('Open Access')
            self.set('subjects',  value)
    
    def get_identifiers(self):
        super(SpringerScraper, self).get_identifiers()
        el =  self.doc.select_one('#doi-url')
        if el:
            value = identifier_cleaner('doi', quiet=True)(el.text)
            if value:
                self.identifiers['doi'] = value

    def get_isbns(self):
        isbns = {}
        el =  self.doc.select_one('#print-isbn')
        if el:
            value = identifier_cleaner('isbn', quiet=True)(el.text)
            if value:
                isbns['paper'] = value
        el =  self.doc.select_one('#electronic-isbn')
        if el:
            value = identifier_cleaner('isbn', quiet=True)(el.text)
            if value:
                isbns['electronic'] = value
        return isbns
    
    def get_title(self):
        el =  self.doc.select_one('#book-title')
        if el:
            value = el.text.strip()
            if value:
                value = value.replace('\n', ': ', 1)
                self.set('title', value)
        if not value:
            (SpringerScraper, self).get_title()
    
    def get_author_list(self):
        for el in self.doc.select('.authors__name'):
            yield el.text.strip().replace(u'\xa0', u' ')
            
    def get_license(self):
        '''only looks for cc licenses'''
        links = self.doc.find_all(href=CONTAINS_CC)
        for link in links:
            self.set('rights_url', link['href'])
            return
        mention = self.doc.find(string=MENTIONS_CC)   
        if mention:
            lic = MENTIONS_CC.search(mention).group(0)
            lic_url = 'https://creativecommons.org/licences/{}/'.format(lic[3:].lower())
            self.set('rights_url', lic_url)
            
    def get_pubdate(self):
        pubinfo = self.doc.select_one('#copyright-info')
        if pubinfo:
            yearmatch = HAS_YEAR.search(pubinfo.string)
            if yearmatch:
                self.set('publication_date', yearmatch.group(0))

    @classmethod
    def can_scrape(cls, url):
        ''' return True if the class can scrape the URL '''
        return url.find('10.1007') or url.find('10.1057')
        

search_url = 'https://link.springer.com/search/page/{}?facet-content-type=%22Book%22&package=openaccess'
def load_springer(num_pages):
    def springer_open_books(num_pages):
        for page in range(1, num_pages+1):
            url = search_url.format(page)
            response = requests.get(url, headers={"User-Agent": settings.USER_AGENT})
            if response.status_code == 200:
                base = response.url
                doc = BeautifulSoup(response.content, 'lxml')
                for link in doc.select('a.title'):
                    book_url = urljoin(base, link['href'])
                    yield SpringerScraper(book_url)
    return add_from_bookdatas(springer_open_books(num_pages))
