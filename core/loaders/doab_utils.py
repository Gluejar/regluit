"""
doab_utils.py

"""
import logging
import re
from urllib.parse import urlparse, urljoin

import requests

from regluit.utils.lang import lang_to_language_code
from .soup import get_soup

logger = logging.getLogger(__name__)

def doab_lang_to_iso_639_1(lang):
    lang = lang_to_language_code(lang)
    return lang if lang else 'xx'


FRONTIERSIN = re.compile(r'frontiersin.org/books/[^/]+/(\d+)')

def online_to_download(url):
    urls = []
    if not url:
        return urls
    if url.find(u'mdpi.com/books/pdfview/book/') >= 0:
        doc = get_soup(url)
        if doc:
            obj = doc.find('object', type='application/pdf')
            if obj:
                urls.append(obj['data'].split('#')[0])
    elif url.find(u'books.scielo.org/') >= 0:
        if url[-4:] in ['epub', '.pdf']:
            return [url] 
        doc = get_soup(url)
        if doc:
            obj = doc.find('a', class_='pdf_file')
            if obj:
                urls.append(urljoin(url, obj['href']))
            obj = doc.find('a', class_='epub_file')
            if obj:
                urls.append(urljoin(url, obj['href']))
    elif FRONTIERSIN.search(url):
        booknum = FRONTIERSIN.search(url).group(1)
        urls.append(u'https://www.frontiersin.org/GetFile.aspx?ebook={}&fileformat=EPUB'.format(booknum))
        urls.append(u'https://www.frontiersin.org/GetFile.aspx?ebook={}&fileformat=PDF'.format(booknum))
    elif url.find(u'edp-open.org/books-in-') >= 0:
        # pages needing multi-scrape
        return urls
    else:
        urls.append(url)
    if not urls:
        logging.warning('no valid download urls for %s', url)
    return urls

