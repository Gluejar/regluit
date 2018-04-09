"""
doab_utils.py

"""

import re
import urlparse

import requests

frm .utils import get_soup

# utility functions for converting lists of individual items into individual items

# let's do a mapping of the DOAB languages into the language codes used 
# by Google Books API and unglue.it
# https://en.wikipedia.org/wiki/ISO_639-1 (2 letter)
# http://stackoverflow.com/questions/1665667/python-list-filtering-and-transformation

# from looking at the DOAB languages that don't map obviously to ISO 639.1, I looked 
# at a few example. the pattern I discern and conjecture as holding for the remainder 
# is that ^ means a separator for languages in
# works with multiple languages.  I will map to the first language.

# also null -> xx

LANG_MAP = dict([
    ('English', 'en'),
    ('German', 'de'),
    ('de', 'de'),
    ('fr', 'fr'),
    ('Italian', 'it'),
    ('Dutch', 'nt'),
    ('english', 'en'),
    ('en', 'en'),
    ('French', 'fr'),
    ('En', 'en'),
    ('italian', 'it'),
    ('de^it^rm', 'de'),  # de /it/rm http://www.doabooks.org/doab?func=search&template=&query=Sprachatlas+des+Dolomitenladinischen+und+angrenzender+Gebiete
    ('de^English', 'de'), # eg., http://www.doabooks.org/doab?func=search&template=&query=Robert+Neumann%3A+Mit+eigener+Feder
    ('german', 'de'),
    ('Czech', 'cs'),
    ('Deutsch', 'de'),
    ('Italian / English', 'it'), # http://www.doabooks.org/doab?func=search&template=&query=JLIS
    ('English; French', 'en'),
    ('Englilsh ; Cree', 'en'),
    ('English; French; Cree; Michif; Chinese; Ukrainian', 'en'),
    ('Englisch', 'en'),
    ('Spanish', 'es'),
    ('English;', 'en'),
    ('de^la', 'de'),
    ('de^English^fr^es', 'de'),
    ('English; Italian', 'en'),
    ('Espanol', 'es'),
    ('Welsh', 'cy'),
    ('English; Czech', 'en'),
    ('Englilsh', 'en'),
    ('German;', 'de'),
    ('German; English', 'de'),
    ('Russian;', 'ru')
])

def doab_lang_to_iso_639_1(lang):
    if lang is None or not lang:
        return "xx"
    return LANG_MAP.get(lang, 'xx')


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
    if url.find(u'mdpi.com/books/pdfview') >= 0:
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
        urls.append(u'https://www.frontiersin.org/GetFile.aspx?ebook={1001}&fileformat=EPUB'.format(booknum))
        urls.append(u'https://www.frontiersin.org/GetFile.aspx?ebook={1001}&fileformat=PDF'.format(booknum))
    else:
        urls.append(url)
    return urls

