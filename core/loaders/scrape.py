import re
import logging
import requests
from bs4 import BeautifulSoup
#from gitenberg.metadata.pandata import Pandata
from django.conf import settings
from urlparse import urljoin

from regluit.core import models
from regluit.core.validation import identifier_cleaner, authlist_cleaner

logger = logging.getLogger(__name__)

CONTAINS_COVER = re.compile('cover')
CONTAINS_CC = re.compile('creativecommons.org')

class BaseScraper(object):    
    '''
    designed to make at least a decent gues for webpages that embed metadata
    '''
    def __init__(self, url):
        self.metadata = {}
        self.identifiers = {'http': url}
        self.doc = None
        self.base = url
        try:
            response = requests.get(url, headers={"User-Agent": settings.USER_AGENT})
            if response.status_code == 200:
                self.doc = BeautifulSoup(response.content, 'lxml')
                self.get_genre()
                self.get_title()
                self.get_language()
                self.get_description()
                self.get_identifiers()
                self.get_keywords()
                self.get_publisher()
                self.get_pubdate()
                self.get_authors()
                self.get_cover()
                self.get_downloads()
                self.get_license()
            if not self.metadata.get('title', None):
                self.set('title', '!!! missing title !!!')
            if not self.metadata.get('language', None):
                self.set('language', 'en')
        except requests.exceptions.RequestException as e:
            logger.error(e)
            self.metadata = {}
        self.metadata['identifiers'] = self.identifiers

    #
    # utilities
    #
    
    def set(self, name, value):
        self.metadata[name] = value
                
    def fetch_one_el_content(self, el_name):
        data_el = self.doc.find(el_name)
        value = ''
        if data_el:
            value = data_el.text
        return value 
    
    def check_metas(self, meta_list, **attrs):
        value = ''
        list_mode = attrs.pop('list_mode', 'longest')
        for meta_name in meta_list:
            attrs['name'] = meta_name
            
            metas = self.doc.find_all('meta', attrs=attrs)
            if len(metas) == 0:
                # some sites put schema.org metadata in metas
                del(attrs['name'])
                attrs['itemprop'] = meta_name
                metas = self.doc.find_all('meta', attrs=attrs)
                del(attrs['itemprop'])
            for meta in metas:
                el_value = meta.get('content', '').strip()
                if list_mode == 'longest':
                    if len(el_value) > len (value):
                        value = el_value
                elif list_mode == 'list':
                    if value == '':
                        value = [el_value] 
                    else:
                        value.append(el_value)
            if value:
                return value
        return value 
    
    def get_dt_dd(self, name):
        ''' get the content of <dd> after a <dt> containing name'''
        dt = self.doc.find('dt', string=re.compile(name))
        dd = dt.find_next_sibling('dd') if dt else None
        return dd.text if dd else None

    #
    # getters
    #

    def get_genre(self):
        value = self.check_metas(['DC.Type', 'dc.type', 'og:type'])
        if value and value in ('Text.Book', 'book'):
            self.set('genre', 'book')            

    def get_title(self):
        value = self.check_metas(['DC.Title', 'dc.title', 'citation_title', 'title'])
        if not value:
            value =  self.fetch_one_el_content('title')
        self.set('title', value)
        
    def get_language(self):
        value = self.check_metas(['DC.Language', 'dc.language', 'language', 'inLanguage'])
        self.set('language', value)

    def get_description(self):
        value = self.check_metas([
            'DC.Description',
            'dc.description',
            'og:description',
            'description'
        ])
        self.set('description',  value)

    def get_isbns(self):
        '''return a dict of edition keys and ISBNs'''
        isbns = {}
        label_map = {'epub': 'EPUB', 'mobi': 'Mobi', 
            'paper': 'Paperback', 'pdf':'PDF', 'hard':'Hardback'}
        for key in label_map.keys():
            isbn_key = 'isbn_{}'.format(key)
            value = self.check_metas(['citation_isbn'], type=label_map[key])
            value = identifier_cleaner('isbn')(value)
            if value:
                isbns[isbn_key] = value
                self.identifiers[isbn_key] = value
        return isbns

    def get_identifiers(self):
        value = self.check_metas(['DC.Identifier.URI'])
        if not value:
            value = self.doc.select_one('link[rel=canonical]')
            value = value['href'] if value else None
        value = identifier_cleaner('http')(value)
        if value:
            self.identifiers['http'] = value
        value = self.check_metas(['DC.Identifier.DOI', 'citation_doi'])
        value = identifier_cleaner('doi')(value)
        if value:
            self.identifiers['doi'] = value

        isbns = self.get_isbns()                
        ed_list = []
        if len(isbns):
            #need to create edition list
            for key in isbns.keys():
                isbn_type = key.split('_')[-1]
                ed_list.append({
                    'edition_note': isbn_type,
                    'edition_identifiers': {'isbn': isbns[key]}
                })
        else:
            value = self.check_metas(['citation_isbn'], list_mode='list')
            if len(value):
                for isbn in value:
                    isbn = identifier_cleaner('isbn')(isbn)
                    if isbn:
                        ed_list.append({
                            '_edition': isbn,
                            'edition_identifiers': {'isbn':isbn}
                        })
        if len(ed_list):
            self.set('edition_list', ed_list)
        
    def get_keywords(self):
        value = self.check_metas(['keywords']).strip(',;')
        if value:
            self.set('subjects', re.split(' *[;,] *', value))
            
    def get_publisher(self):
        value = self.check_metas(['citation_publisher', 'DC.Source'])
        if value:
            self.set('publisher', value)

    def get_pubdate(self):
        value = self.check_metas(['citation_publication_date', 'DC.Date.issued', 'datePublished'])
        if value:
            self.set('publication_date', value)

    def get_authors(self):
        value_list = self.check_metas([
            'DC.Creator.PersonalName',
            'citation_author',
            'author',
        ], list_mode='list')
        if not value_list:
            return
        creator_list = []
        value_list = authlist_cleaner(value_list)
        if len(value_list) == 1:
            self.set('creator',  {'author': {'agent_name': value_list[0]}})
            return
        for auth in value_list: 
             creator_list.append({'agent_name': auth})

        self.set('creator', {'authors': creator_list })
    
    def get_cover(self):
        image_url = self.check_metas(['og.image', 'image'])
        if not image_url:
            block = self.doc.find(class_=CONTAINS_COVER)
            block = block if block else self.doc
            img = block.find_all('img', src=CONTAINS_COVER)
            if img:
                cover_uri = img[0].get('src', None)
                if cover_uri:
                    image_url = urljoin(self.base, cover_uri)
        if image_url:
            self.set('covers', [{'image_url': image_url}])
                
    def get_downloads(self):
        for dl_type in ['epub', 'mobi', 'pdf']:
            dl_meta = 'citation_{}_url'.format(dl_type)
            value = self.check_metas([dl_meta])
            if value:
                self.set('download_url_{}'.format(dl_type), value)
                
    def get_license(self):
        '''only looks for cc licenses'''
        links = self.doc.find_all(href=CONTAINS_CC)
        for link in links:
            self.set('rights_url', link['href'])

    @classmethod
    def can_scrape(cls, url):
        ''' return True if the class can scrape the URL '''
        return True
        
class PressbooksScraper(BaseScraper):
    def get_downloads(self):
        for dl_type in ['epub', 'mobi', 'pdf']:
            download_el = self.doc.select_one('.{}'.format(dl_type))
            if download_el and download_el.find_parent():
                value = download_el.find_parent().get('href') 
                if value:
                    self.set('download_url_{}'.format(dl_type), value)

    def get_publisher(self):
        value = self.get_dt_dd('Publisher')
        if not value:
            value = self.doc.select_one('.cie-name')
            value = value.text if value else None
        if value:
            self.set('publisher', value)
        else:
            super(PressbooksScraper, self).get_publisher()
    
    def get_title(self):
        value = self.doc.select_one('.entry-title a[title]')
        value = value['title'] if value else None
        if value:
            self.set('title', value)
        else:
            super(PressbooksScraper, self).get_title()

    def get_isbns(self):
        '''add isbn identifiers and return a dict of edition keys and ISBNs'''
        isbns = {}
        for (key, label) in [('electronic', 'Ebook ISBN'), ('paper', 'Print ISBN')]:
            isbn = identifier_cleaner('isbn')(self.get_dt_dd(label))
            if isbn:
                self.identifiers['isbn_{}'.format(key)] = isbn
                isbns[key] = isbn
        return isbns
                
    @classmethod
    def can_scrape(cls, url):
        ''' return True if the class can scrape the URL '''
        return url.find('press.rebus.community') > 0 or url.find('pressbooks.com') > 0

def get_scraper(url):
    scrapers = [PressbooksScraper, BaseScraper]
    for scraper in scrapers:
        if scraper.can_scrape(url):
            return scraper(url)
            
def scrape_sitemap(url, maxnum=None):
    try:
        response = requests.get(url, headers={"User-Agent": settings.USER_AGENT})
        doc = BeautifulSoup(response.content, 'lxml')
        for page in doc.find_all('loc')[0:maxnum]:
            scraper = get_scraper(page.text)
            if scraper.metadata.get('genre', None) == 'book':
                yield scraper
    except requests.exceptions.RequestException as e:
        logger.error(e)
