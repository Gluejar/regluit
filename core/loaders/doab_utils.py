"""
doab_utils.py

"""

import re
import urlparse

import requests

from regluit.utils.lang import lang_to_language_code
from .utils import get_soup

def doab_lang_to_iso_639_1(lang):
    lang = lang_to_language_code(lang)
    return lang if lang else 'xx'


DOMAIN_TO_PROVIDER = dict([
    [u'adelaide.edu.au', u'University of Adelaide'],
    [u'aliprandi.org', u'Simone Aliprandi'],
    [u'antilia.to.it', u'antilia.to.it'],
    [u'antropologie.zcu.cz', u'AntropoWeb'],
    [u'aupress.ca', u'Athabasca University Press'],
    [u'bloomsburyacademic.com', u'Bloomsbury Academic'],
    [u'books.mdpi.com', u'MDPI Books'],
    [u'books.openedition.org', u'OpenEdition Books'],
    [u'books.scielo.org', u'SciELO'],
    [u'ccdigitalpress.org', u'Computers and Composition Digital Press'],
    [u'co-action.net', u'Co-Action Publishing'],
    [u'degruyter.com', u'De Gruyter Online'],
    [u'digitalcommons.usu.edu', u'DigitalCommons, Utah State University'],
    [u'dl.dropboxusercontent.com', u'Dropbox'],
    [u'doabooks.org', u'Directory of Open Access Books'],
    [u'doi.org', u'DOI Resolver'],
    [u'dropbox.com', u'Dropbox'],
    [u'dspace.ucalgary.ca', u'Institutional Repository at the University of Calgary'],
    [u'dx.doi.org', u'DOI Resolver'],
    [u'ebooks.iospress.nl', u'IOS Press Ebooks'],
    [u'hdl.handle.net', u'Handle Proxy'],
    [u'hw.oeaw.ac.at', u'Austrian Academy of Sciences'],
    [u'img.mdpi.org', u'MDPI Books'],
    [u'ledibooks.com', u'LediBooks'],
    [u'ledizioni.it', u'Ledizioni'],
    [u'leo.cilea.it', u'LEO '],
    [u'leo.cineca.it', u'Letteratura Elettronica Online'],
    [u'link.springer.com', u'Springer'],
    [u'maestrantonella.it', u'maestrantonella.it'],
    [u'oapen.org', u'OAPEN Library'],
    [u'openbookpublishers.com', u'Open Book Publishers'],
    [u'palgraveconnect.com', u'Palgrave Connect'],
    [u'press.openedition.org', u'OpenEdition Press'],
    [u'scribd.com', u'Scribd'],
    [u'springerlink.com', u'Springer'],
    [u'ubiquitypress.com', u'Ubiquity Press'],
    [u'unglueit-files.s3.amazonaws.com', u'Unglue.it'],
    [u'unimib.it', u'University of Milano-Bicocca'],
    [u'unito.it', u"University of Turin"],
    [u'windsor.scholarsportal.info', u'Scholars Portal'],
])

def url_to_provider(url):
    netloc = urlparse.urlparse(url).netloc.lower()
    if netloc in [u'dx.doi.org', u'doi.org', u'hdl.handle.net']:
        url = requests.get(url).url
        netloc = urlparse.urlparse(url).netloc
    if netloc.startswith('www.'):
        netloc = netloc[4:]
    return DOMAIN_TO_PROVIDER.get(netloc, netloc)

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
                urls.append(urlparse.urljoin(url, obj['href']))
            obj = doc.find('a', class_='epub_file')
            if obj:
                urls.append(urlparse.urljoin(url, obj['href']))
    elif FRONTIERSIN.search(url):
        booknum = FRONTIERSIN.search(url).group(1)
        urls.append(u'https://www.frontiersin.org/GetFile.aspx?ebook={}&fileformat=EPUB'.format(booknum))
        urls.append(u'https://www.frontiersin.org/GetFile.aspx?ebook={}&fileformat=PDF'.format(booknum))
    elif url.find(u'edp-open.org/books-in-') >= 0:
        # pages needing multi-scrape
        return urls
    else:
        urls.append(url)
    return urls

