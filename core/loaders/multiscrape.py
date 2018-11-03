import logging
import re
from urlparse import urljoin

from bs4 import BeautifulSoup
import requests

from django.conf import settings

from regluit.core.bookloader import add_from_bookdatas
from regluit.core.loaders.scrape import BaseScraper
from regluit.core.validation import identifier_cleaner

logger = logging.getLogger(__name__)
'''
use for web pages with multiple books
returns an iterator of scrapers
'''
        
class BaseMultiScraper(BaseScraper):
    parser_name = 'lxml'
    def __init__(self, url, doc):
        self.metadata = {}
        self.identifiers = {}
        self.doc = doc
        self.base = url
        self.get_all()
        if not self.metadata.get('title', None):
            self.set('title', '!!! missing title !!!')
        self.metadata['identifiers'] = self.identifiers

    @classmethod
    def login(cls):
        return requests

def multiscrape(url, scraper_class=BaseMultiScraper):
    try:
        response = scraper_class.get_response(url)
        if response.status_code == 200:
            doc = BeautifulSoup(response.content, scraper_class.parser_name)
            sections = scraper_class.divider(doc)
            for section in sections:
                yield scraper_class(url, section)
    except requests.exceptions.RequestException as e:
        logger.error(e)
        self.metadata = None


# following is code specific to edp-open.org; refactor when we add another


ISBNMATCH = re.compile(r'([\d\-]+)')
class EDPMultiScraper(BaseMultiScraper):
    @classmethod
    def divider(cls, doc):
        return doc.select('article.Bk')

    def get_isbns(self):
        '''return a dict of edition keys and ISBNs'''
        isbns = {}
        isbn_cleaner = identifier_cleaner('isbn', quiet=True)
        labels = ['epub', 'pdf', 'paper']
        info = self.doc.select_one('p.nfo').text
        isbntexts = re.split('ISBN', info)
        for isbntext in isbntexts[1:]:
            isbnmatch = ISBNMATCH.search(isbntext)
            if isbnmatch:
                isbn = isbn_cleaner(isbnmatch.group(0))
                isbns[labels.pop()] = isbn
        return isbns

    def get_downloads(self):
        dl = self.doc.select_one('nav.dl')
        links = dl.select('a.fulldl')
        for link in links:
            href = urljoin(self.base, link['href'])
            if href.endswith('.pdf'):
                self.set('download_url_pdf', href)
            elif  href.endswith('.epub'):
                self.set('download_url_epub', href)

    def get_language(self):
        if 'english' in self.base:
            self.set('language', 'en')
        else:
            self.set('language', 'fr')

    def get_title(self):
        value = self.doc.select_one('h2').text
        book_id = self.doc.select_one('h2')['id']
        self.identifiers['http'] = u'{}#{}'.format(self.base, book_id)
        self.set('title', value)

def edp_scrape():
    edp_urls = [
        'https://www.edp-open.org/books-in-french',
        'https://www.edp-open.org/books-in-english',
    ]
    for url in edp_urls:
        scrapers = multiscrape(url, scraper_class=EDPMultiScraper)
        add_from_bookdatas(scrapers)

