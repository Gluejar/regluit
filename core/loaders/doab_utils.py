"""
doab_utils.py

"""

import re
import urlparse

import requests

from regluit.utils.lang import get_language_code
from .utils import get_soup

# utility functions for converting lists of individual items into individual items

# let's do a mapping of the DOAB languages into the language codes used 
# mostly, we just handle mispellings
# also null -> xx

EXTRA_LANG_MAP = dict([
    (u'deutsch', 'de'),
    (u'eng', 'en'),
    (u'englilsh', 'en'),
    (u'englilsh', 'en'),
    (u'englisch', 'en'),
    (u'espanol', 'es'),
    (u'ger', 'de'),
    (u'norwegian', 'no'),
    (u'por', 'pt'),
    (u'portugese', 'pt'),
    (u'spa', 'es'),
])

sep = re.compile(r'[ \-;^,/]+')
def doab_lang_to_iso_639_1(lang):
    if lang is None or not lang:
        return "xx"
    else:
        lang = sep.split(lang)[0]
        code = get_language_code(lang)
        if code:
            return code
        else:
            return EXTRA_LANG_MAP.get(lang.lower(), 'xx')


DOMAIN_TO_PROVIDER = dict([
    [u'www.doabooks.org', u'Directory of Open Access Books'],
    [u'www.oapen.org', u'OAPEN Library'],
    [u'books.openedition.org', u'OpenEdition Books'],
    [u'digitalcommons.usu.edu', u'DigitalCommons, Utah State University'],
    [u'www.aupress.ca', u'Athabasca University Press'],
    [u'dspace.ucalgary.ca', u'Institutional Repository at the University of Calgary'],
    [u'www.degruyter.com', u'De Gruyter Online'],
    [u'dx.doi.org', u'DOI Resolver'],
    [u'www.openbookpublishers.com', u'Open Book Publishers'],
    [u'www.adelaide.edu.au', u'University of Adelaide'],
    [u'hdl.handle.net', u'Handle Proxy'],
    [u'link.springer.com', u'Springer'],
    [u'www.bloomsburyacademic.com', u'Bloomsbury Academic'],
    [u'www.ledizioni.it', u'Ledizioni'],
    [u'ccdigitalpress.org', u'Computers and Composition Digital Press'],
    [u'leo.cilea.it', u'LEO '],
    [u'www.springerlink.com', u'Springer'],
    [u'www.palgraveconnect.com', u'Palgrave Connect'],
    [u'www.ubiquitypress.com', u'Ubiquity Press'],
    [u'ebooks.iospress.nl', u'IOS Press Ebooks'],
    [u'antropologie.zcu.cz', u'AntropoWeb'],
    [u'www.unito.it', u"University of Turin"],
    [u'leo.cineca.it', u'Letteratura Elettronica Online'],
    [u'hw.oeaw.ac.at', u'Austrian Academy of Sciences'],
    [u'www.co-action.net', u'Co-Action Publishing'],
    [u'www.aliprandi.org', u'Simone Aliprandi'],
    [u'www.maestrantonella.it', u'maestrantonella.it'],
    [u'www.antilia.to.it', u'antilia.to.it'],
    [u'www.scribd.com', u'Scribd'],
    [u'ledibooks.com', u'LediBooks'],
    [u'press.openedition.org', u'OpenEdition Press'],
    [u'oapen.org', u'OAPEN Library'],
    [u'www.ebooks.iospress.nl', u'IOS Press Ebooks'],
    [u'windsor.scholarsportal.info', u'Scholars Portal'],
    [u'www.unimib.it', u'University of Milano-Bicocca'],
    [u'books.mdpi.com', u'MDPI Books'],
    [u'www.dropbox.com', u'Dropbox'],
    [u'dl.dropboxusercontent.com', u'Dropbox'],
])

def url_to_provider(url):
    netloc = urlparse.urlparse(url).netloc
    return DOMAIN_TO_PROVIDER.get(netloc, netloc)

FRONTIERSIN = re.compile(r'frontiersin.org/books/[^/]+/(\d+)')

def online_to_download(url):
    urls = []
    if url.find(u'mdpi.com/books/pdfview/book/') >= 0:
        doc = get_soup(url)
        if doc:
            obj = doc.find('object', type='application/pdf')
            if obj:
                urls.append(obj['data'].split('#')[0])
    elif url.find(u'books.scielo.org/') >= 0:
        doc = get_soup(url)
        if doc:
            obj = doc.find('a', class_='pdf_file')
            if obj:
                urls.append(urlparse.urljoin(url, obj['href']))
            obj = doc.find('a', class_='epub_file')
            if obj:
                urls.append(urlparse.urljoin(url, obj['href']))
    elif FRONTIERSIN.search(url):
        booknum = FRONTIERSIN.search(url).group(1)
        urls.append(u'https://www.frontiersin.org/GetFile.aspx?ebook={}&fileformat=EPUB'.format(booknum))
        urls.append(u'https://www.frontiersin.org/GetFile.aspx?ebook={}&fileformat=PDF'.format(booknum))
    else:
        urls.append(url)
    return urls

