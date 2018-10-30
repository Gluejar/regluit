import re
import logging
from urlparse import urlparse
import requests
from bs4 import BeautifulSoup
#from gitenberg.metadata.pandata import Pandata
from django.conf import settings
from urlparse import urljoin

from regluit.core import models
from regluit.core.validation import (
    authlist_cleaner,
    identifier_cleaner,
    valid_subject,
    validate_date,
)

logger = logging.getLogger(__name__)

CONTAINS_COVER = re.compile('cover')
CONTAINS_CC = re.compile('creativecommons.org')
CONTAINS_OCLCNUM = re.compile('worldcat.org/oclc/(\d+)')

class BaseScraper(object):
    '''
    designed to make at least a decent guess for webpages that embed metadata
    '''
    can_scrape_hosts = False
    can_scrape_strings = False
    parser_name = 'lxml'

    @classmethod
    def can_scrape(cls, url):
        ''' return True if the class can scrape the URL '''
        if not (cls.can_scrape_hosts or cls.can_scrape_strings):
            return True
        if cls.can_scrape_hosts:
            urlhost = urlparse(url).hostname
            if urlhost:
                for host in cls.can_scrape_hosts:
                    if urlhost.endswith(host):
                        return True
        if cls.can_scrape_strings:
            for pass_str in cls.can_scrape_strings:
                if url.find(pass_str) >= 0:
                    return True
        return False

    @classmethod
    def get_response(cls, url):
        try:
            return requests.get(url, headers={"User-Agent": settings.USER_AGENT})
        except requests.exceptions.RequestException as e:
            logger.error(e)

    def __init__(self, url):
        self.metadata = {}
        self.identifiers = {'http': url}
        self.doc = None
        self.base = url
        response = type(self).get_response(url)
        if response:
            if response.status_code == 200:
                self.base = response.url
                self.doc = BeautifulSoup(response.content, self.parser_name)
                for review in self.doc.find_all(itemtype="http://schema.org/Review"):
                    review.clear()
                self.get_all()
            if not self.metadata.get('title', None):
                self.set('title', '!!! missing title !!!')
            if not self.metadata.get('language', None):
                self.set('language', 'en')
        else:
            self.metadata = {}
        self.metadata['identifiers'] = self.identifiers

    #
    # utilities
    #

    def set(self, name, value):
        if isinstance(value,(str, unicode)):
            value= value.strip()
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
            attrs['name'] = re.compile('^{}$'.format(meta_name), flags=re.I)
            metas = self.doc.find_all('meta', attrs=attrs)
            if len(metas) == 0:
                # some sites put schema.org metadata in metas
                del(attrs['name'])
                attrs['itemprop'] = meta_name
                metas = self.doc.find_all('meta', attrs=attrs)
                del(attrs['itemprop'])
            if len(metas) == 0:
                # og metadata in often in 'property' not name
                attrs['property'] = meta_name
                metas = self.doc.find_all('meta', attrs=attrs)
                del(attrs['property'])
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
        return dd.text.strip() if dd and dd.text else None

    def get_itemprop(self, name, **attrs):
        value_list = []
        list_mode = attrs.pop('list_mode', 'list')
        attrs = {'itemprop': name}
        props = self.doc.find_all(attrs=attrs)
        attrs = {'property': name}
        props = props if props else  self.doc.find_all(attrs=attrs)
        for el in props:
            if list_mode == 'one_item':
                return el.text if el.text else el.get('content')
            else:
                if el.text:
                    value_list.append(el.text)
                elif el.has_key('content'):
                    value_list.append(el['content'])
        return value_list
                
    def get_all(self):
        self.setup()
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

    def setup(self):
        # use this method to get auxiliary resources based on doc
        pass
    #
    # getters
    #

    def get_genre(self):
        value = self.check_metas([r'dc\.type', 'og:type'])
        if value and value in ('Text.Book', 'book'):
            self.set('genre', 'book')

    def get_title(self):
        value = self.check_metas([r'dc\.title', 'citation_title', 'og:title', 'title'])
        if not value:
            value =  self.fetch_one_el_content('title')
        self.set('title', value)

    def get_language(self):
        value = self.check_metas([r'dc\.language', 'language', 'inLanguage'])
        self.set('language', value)

    def get_description(self):
        value = self.check_metas([
            r'dc\.description',
            'og:description',
            'description'
        ])
        self.set('description',  value)

    def get_isbns(self):
        '''return a dict of edition keys and ISBNs'''
        isbns = {}
        isbn_cleaner = identifier_cleaner('isbn', quiet=True)
        label_map = {'epub': 'EPUB', 'mobi': 'Mobi',
            'paper': 'Paperback', 'pdf':'PDF', 'hard':'Hardback'}
        for key in label_map.keys():
            isbn_key = 'isbn_{}'.format(key)
            value = self.check_metas(['citation_isbn'], type=label_map[key])
            value = isbn_cleaner(value)
            if value:
                isbns[isbn_key] = value
                self.identifiers[isbn_key] = value
        if not isbns:
            values = self.check_metas(['book:isbn', 'books:isbn'], list_mode='list')
            values = values if values else self.get_itemprop('isbn')
            if values:
                value = isbn_cleaner(values[0])
                isbns = {'':value} if value else {}
        return isbns

    def get_identifiers(self):
        value = self.check_metas([r'DC\.Identifier\.URI'])
        if not value:
            value = self.doc.select_one('link[rel=canonical]')
            value = value['href'] if value else None
        value = identifier_cleaner('http', quiet=True)(value)
        if value:
            self.identifiers['http'] = value
        value = self.check_metas([r'DC\.Identifier\.DOI', 'citation_doi'])
        value = identifier_cleaner('doi', quiet=True)(value)
        if value:
            self.identifiers['doi'] = value

        #look for oclc numbers
        links = self.doc.find_all(href=CONTAINS_OCLCNUM)
        for link in links:
            oclcmatch = CONTAINS_OCLCNUM.search(link['href'])
            if oclcmatch:
                value = identifier_cleaner('oclc', quiet=True)(oclcmatch.group(1))
                if value:
                    self.identifiers['oclc'] = value
                    break

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
                    isbn = identifier_cleaner('isbn', quiet=True)(isbn)
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
            subjects = []
            for subject in re.split(' *[;,] *', value):
                if valid_subject(subject):
                    subjects.append(subject)
            self.set('subjects', subjects)

    def get_publisher(self):
        value = self.check_metas(['citation_publisher', r'DC\.Source'])
        if value:
            self.set('publisher', value)

    def get_pubdate(self):
        value = self.get_itemprop('datePublished', list_mode='one_item')
        if not value:
            value = self.check_metas([
                'citation_publication_date', 'copyrightYear', r'DC\.Date\.issued', 'datePublished',
                'books:release_date', 'book:release_date', 
            ])
        if value:
            value = validate_date(value)
            if value:
                self.set('publication_date', value)

    def get_author_list(self):
        value_list = self.get_itemprop('author')
        if not value_list:
            value_list = self.check_metas([
                r'DC\.Creator\.PersonalName',
                'citation_author',
                'author',
            ], list_mode='list')
            if not value_list:
                return []
        return value_list

    def get_role(self):
        return 'author'

    def get_authors(self):
        role = self.get_role()
        value_list = self.get_author_list()
        creator_list = []
        value_list = authlist_cleaner(value_list)
        if len(value_list) == 0:
            return
        if len(value_list) == 1:
            self.set('creator',  {role: {'agent_name': value_list[0]}})
            return
        for auth in value_list:
             creator_list.append({'agent_name': auth})

        self.set('creator', {'{}s'.format(role): creator_list })

    def get_cover(self):
        image_url = self.check_metas(['og:image', 'image', 'twitter:image'])
        if not image_url:
            block = self.doc.find(class_=CONTAINS_COVER)
            block = block if block else self.doc
            img = block.find_all('img', src=CONTAINS_COVER)
            if img:
                image_url = img[0].get('src', None)
        if image_url:
            if not image_url.startswith('http'):
                image_url = urljoin(self.base, image_url)
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





