import re
import logging
import requests
from bs4 import BeautifulSoup
#from gitenberg.metadata.pandata import Pandata
from django.conf import settings
from urlparse import urljoin

from regluit.core import models
from regluit.core.validation import identifier_cleaner

logger = logging.getLogger(__name__)

CONTAINS_COVER = re.compile('cover')

class BaseScraper(object):
    def __init__(self, url):
        self.metadata = {}
        self.identifiers = {'http': url}
        self.doc = None
        self.base = url
        try:
            response = requests.get(url, headers={"User-Agent": settings.USER_AGENT})
            if response.status_code == 200:
                self.doc = BeautifulSoup(response.content, 'lxml')
                self.get_title()
                self.get_language()
                self.get_description()
                self.get_identifiers()
                self.get_keywords()
                self.get_publisher()
                self.get_pubdate()
                self.get_authors()
                self.get_cover()
            if not self.metadata.get('title', None):
                self.set('title', '!!! missing title !!!')
            if not self.metadata.get('language', None):
                self.set('language', 'en')
        except requests.exceptions.RequestException as e:
            logger.error(e)
            self.metadata = None
        self.metadata['identifiers'] = self.identifiers
    
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

    def get_title(self):
        value = self.check_metas(['DC.Title','dc.title', 'citation_title', 'title'])
        if not value:
            value =  self.fetch_one_el_content('title')
        self.set('title', value)
        
    def get_language(self):
        value = self.check_metas(['DC.Language','dc.language','language'])
        self.set('language', value)

    def get_description(self):
        value = self.check_metas(['DC.Description','dc.description','description'])
        self.set('description',  value)

    def get_identifiers(self):
        value = self.check_metas(['DC.Identifier.URI'])
        value = identifier_cleaner('http')(value)
        if value:
            self.identifiers['http'] = value
        value = self.check_metas(['DC.Identifier.DOI', 'citation_doi'])
        value = identifier_cleaner('doi')(value)
        if value:
            self.identifiers['doi'] = value
        isbns = {}
        label_map = {'epub': 'EPUB', 'mobi': 'Mobi', 'paper': 
            'Paperback', 'pdf': 'PDF', 'hard':'Hardback'}
        for key in label_map.keys():
            isbn_key = 'isbn_{}'.format(key)
            value = self.check_metas(['citation_isbn'], type=label_map[key])
            value = identifier_cleaner('isbn')(value)
            if value:
                isbns[isbn_key] = value
                
        ed_list = []
        if len(isbns):
            #need to create edition list
            for key in isbns.keys():
                isbn_type = key.split('_')[-1]
                ed_list.append({
                    'edition': isbn_type,
                    'edition_identifiers': {'isbn': isbns[key]}
                })
        else:
            value = self.check_metas(['citation_isbn'], list_mode='list')
            if len(value):
                for isbn in value:
                    isbn = identifier_cleaner('isbn')(isbn)
                    if isbn:
                        ed_list.append({
                            'edition': isbn,
                            'edition_identifiers': {'isbn': isbn}
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
        value = self.check_metas(['citation_publication_date', 'DC.Date.issued'])
        if value:
            self.set('publication_date', value)

    def get_authors(self):
        value_list = self.check_metas(['DC.Creator.PersonalName', 'citation_author',], list_mode='list')
        if not value_list:
            return
        if len(value_list) == 1:
            creator = {'author': {'agent_name': value_list[0]}}
        else:
            creator_list = []
            for auth in value_list: 
                 creator_list.append({'agent_name': auth})
            creator = {'authors': creator_list }
                
        self.set('creator', creator)
    
    def get_cover(self):
        block = self.doc.find(class_=CONTAINS_COVER)
        block = block if block else self.doc
        img = block.find_all('img', src=CONTAINS_COVER)
        if img:
            cover_uri = img[0].get('src', None)
            if cover_uri:
                self.set('covers', [{'image_url': urljoin(self.base, cover_uri)}])