import re
from urlparse import urljoin

import requests
from bs4 import BeautifulSoup

from django.conf import settings

from regluit.core.validation import identifier_cleaner
from regluit.core.bookloader import add_from_bookdatas

from .scrape import BaseScraper, CONTAINS_CC

MENTIONS_CC = re.compile(r'CC BY(-NC)?(-ND|-SA)?', flags=re.I)
HAS_YEAR = re.compile(r'(19|20)\d\d')

class SpringerScraper(BaseScraper):
    can_scrape_strings =['10.1007', '10.1057']
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
                text = div.get_text() if hasattr(div, 'get_text') else div.string
                if text:
                    text = text.replace(u'\xa0', u' ')
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
        value = ''
        if el:
            value = el.text.strip()
        else:
            el =  self.doc.select_one('.page-title')
            if el:
                value = el.text.strip()
        if value:
            value = value.replace('\n', ': ', 1)
            self.set('title', value)
        else:
            super(SpringerScraper, self).get_title()

    def get_role(self):
        if self.doc.select_one('#editors'):
            return 'editor'
        return 'author'

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
            lic_url = 'https://creativecommons.org/licenses/{}/'.format(lic[3:].lower())
            self.set('rights_url', lic_url)

    def get_pubdate(self):
        pubinfo = self.doc.select_one('#copyright-info')
        if pubinfo:
            yearmatch = HAS_YEAR.search(pubinfo.string)
            if yearmatch:
                self.set('publication_date', yearmatch.group(0))

    def get_publisher(self):
        self.set('publisher', 'Springer')

search_url = 'https://link.springer.com/search/page/{}?facet-content-type=%22Book%22&package=openaccess'
def load_springer(startpage=1, endpage=None):
    def springer_open_books(startpage, endpage):
        endpage = endpage if endpage else startpage + 10
        for page in range(startpage, endpage + 1):
            url = search_url.format(page)
            try:
                response = requests.get(url, headers={"User-Agent": settings.USER_AGENT})
                if response.status_code == 200:
                    base = response.url
                    doc = BeautifulSoup(response.content, 'lxml')
                    for link in doc.select('a.title'):
                        book_url = urljoin(base, link['href'])
                        yield SpringerScraper(book_url)
            except requests.exceptions.ConnectionError:
                print 'couldn\'t connect to %s' % url
    return add_from_bookdatas(springer_open_books(startpage, endpage))
