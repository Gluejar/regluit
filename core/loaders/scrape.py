import logging
import requests
from bs4 import BeautifulSoup
from gitenberg.metadata.pandata import Pandata
from django.conf import settings
from regluit.core import models

logger = logging.getLogger(__name__)

class BaseScraper(object):
    def __init__(self, url):
        self.metadata = Pandata()
        self.doc = None
        try:
            response = requests.get(url, headers={"User-Agent": settings.USER_AGENT})
            if response.status_code == 200:
                self.doc = BeautifulSoup(response.content, 'lxml')
                self.get_title()
                self.get_language()
                self.get_description()
            if not self.metadata.title:
                self.metadata.title = '!!! missing title !!!'
            if not self.metadata.language:
                self.metadata.language = 'en'
        except requests.exceptions.RequestException as e:
            logger.error(e)
            self.metadata = None

    def fetch_one_el_content(self, el_name):
        data_el = self.doc.find(el_name)
        value = ''
        if data_el:
            value = data_el.text
        return value 
    
    def check_metas(self, meta_list):
        value = ''
        for meta_name in meta_list:
            metas = self.doc.find_all('meta', attrs={'name': meta_name})
            
            for meta in metas:
                el_value = meta.get('content', '')
                if len(el_value) > len (value):
                    value = el_value
        return value 

    def get_title(self):
        value = self.check_metas(['DC.Title','dc.title','title'])
        if not value:
            value =  self.fetch_one_el_content('title')
        self.metadata.title = value
        
    def get_language(self):
        value = self.check_metas(['DC.Language','dc.language','language'])
        self.metadata.language = value

    def get_description(self):
        value = self.check_metas(['DC.Description','dc.description','description'])
        self.metadata.description =  value
