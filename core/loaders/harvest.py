"""
code for harvesting 'online' ebooks
"""
import logging
import re
import time
from urllib.parse import urlparse, urljoin

import requests

from django.conf import settings
from django.core.files.base import ContentFile

from regluit.core.models import (
    Ebook, EbookFile, path_for_file,
)
from regluit.core.pdf import staple_pdf

from .utils import get_soup, type_for_url


logger = logging.getLogger(__name__)

DROPBOX_DL = re.compile(r'"(https://dl.dropboxusercontent.com/content_link/[^"]+)"')
DELAY = 5.0
OPENBOOKPUB =  re.compile(r'openbookpublishers.com/+(reader|product|/?download/book)/(\d+)')

class RateLimiter(object):
    def __init__(self):
        self.last = {}

    def delay(self, provider):
        if provider in self.last:
            prev = self.last[provider]
            pres = time.time()
            if pres - prev < DELAY:
                time.sleep(float(DELAY - pres + prev))
        self.last[provider] = time.time()
        return

rl = RateLimiter()

def dl_online(ebook, limiter=rl.delay):
    if ebook.format != 'online':
        return None, 0
    for do_harvest, harvester in harvesters(ebook):
        if do_harvest:
            for ebf in ebf_if_harvested(ebook.url):
                return ebf, 0
            limiter(ebook.provider)
            return harvester(ebook)
    return None, 0


def harvesters(ebook):
    yield ebook.url.find(u'dropbox.com/s/') >= 0, harvest_dropbox
    yield ebook.url.find(u'jbe-platform.com/content/books/') >= 0, harvest_jbe
    yield ebook.provider == u'De Gruyter Online', harvest_degruyter
    yield OPENBOOKPUB.search(ebook.url), harvest_obp
    yield ebook.provider == 'Transcript-Verlag', harvest_transcript
    yield ebook.provider == 'ksp.kit.edu', harvest_ksp
    yield ebook.provider == 'digitalis.uc.pt', harvest_digitalis
    yield ebook.provider == 'nomos-elibrary.de', harvest_nomos
    yield ebook.provider == 'frontiersin.org', harvest_frontiersin
    yield ebook.url.find('link.springer') >= 0, harvest_springerlink
    yield ebook.provider == 'OAPEN Library', harvest_oapen
    yield ebook.provider == 'pulp.up.ac.za', harvest_pulp
    yield ebook.provider == 'bloomsburycollections.com', harvest_bloomsbury

def ebf_if_harvested(url):
    onlines = EbookFile.objects.filter(source=url)
    if onlines:
        return onlines
    return  EbookFile.objects.none()


def make_dl_ebook(url, ebook, user_agent=settings.USER_AGENT, method='GET'):
    if not url:
        logger.warning('no url for ebook %s', ebook.id)
        return None, 0
    logger.info('making %s' % url)

    # check to see if url already harvested
    new_prev = []
    for ebf in ebf_if_harvested(url):
        new_ebf = EbookFile.objects.create(
            edition=ebf.edition,
            format=ebf.format,
            file=ebf.file,
            source=ebook.url,
        )
        new_prev.append(new_ebf)
    if new_prev:
        return new_prev[0], len(new_prev)

    if method == 'POST':
        response = requests.post(url, headers={"User-Agent": user_agent})
    else:
        response = requests.get(url, headers={"User-Agent": user_agent})
    if response.status_code == 200:
        filesize = int(response.headers.get("Content-Length", 0))
        filesize = filesize if filesize else None
        format = type_for_url(url, 
                              content_type=response.headers.get('content-type', ''),
                              disposition=response.headers.get('content-disposition', ''))
        if format != 'online':
            return make_harvested_ebook(response.content, ebook, format, filesize=filesize)
        else:
            logger.warning('download format for %s is not ebook', url)
    else:
        logger.warning('couldn\'t get %s', url)
    return None, 0

def make_stapled_ebook(urllist, ebook, user_agent=settings.USER_AGENT, strip_covers=False):
    pdffile = staple_pdf(urllist, user_agent, strip_covers=strip_covers)
    if not pdffile:
        return None, 0
    return make_harvested_ebook(pdffile.getvalue(), ebook, 'pdf')

def make_harvested_ebook(content, ebook, format, filesize=0):
    if not filesize:
        filesize = len(content)
    new_ebf = EbookFile.objects.create(
        edition=ebook.edition,
        format=format,
        source=ebook.url,
    )
    try:
        new_ebf.file.save(path_for_file(new_ebf, None), ContentFile(content))
        new_ebf.save()
    except MemoryError:  #huge pdf files cause problems here
        logger.error("memory error saving ebook file for %s", ebook.url)
        new_ebf.delete()
        return None, 0

    new_ebook = Ebook.objects.create(
        edition=ebook.edition,
        format=format,
        provider='Unglue.it',
        url=new_ebf.file.url,
        rights=ebook.rights,
        filesize=filesize,
        version_label=ebook.version_label,
        version_iter=ebook.version_iter,
    )
    new_ebf.ebook = new_ebook
    new_ebf.save()
    return new_ebf, 1

def harvest_obp(ebook):    
    match = OPENBOOKPUB.search(ebook.url)
    booknum = None
    if match and match.group(1) in ('product', 'reader'):
        prodnum = match.group(2)
        prod_url = 'https://www.openbookpublishers.com/product/{}'.format(prodnum)
        doc = get_soup(prod_url, settings.GOOGLEBOT_UA)
        if doc:
            obj = doc.find('button', value='Download')
            if obj:
                booknum = obj.get('onclick')
                if booknum:
                    booknum = OPENBOOKPUB.search(booknum).group(2)
        else:
            logger.warning('couldn\'t get soup for %s', prod_url)
    else:
        booknum = match.group(2)
    if not booknum:
        logger.warning('couldn\'t get booknum for %s', ebook.url)
        return None, 0
    dl_url = 'https://www.openbookpublishers.com//download/book_content/{}'.format(booknum)
    made = make_dl_ebook(dl_url, ebook, user_agent=settings.GOOGLEBOT_UA, method='POST')
    return made

DEGRUYTERFULL = re.compile(r'/downloadpdf/title/.*')
DEGRUYTERCHAP = re.compile(r'/downloadpdf/book/.*')
COMPLETE = re.compile(r'complete ebook', flags=re.I)

def harvest_degruyter(ebook):
    doc = get_soup(ebook.url, settings.GOOGLEBOT_UA)
    if doc:
        try:
            base = doc.find('base')['href']
        except:
            base = ebook.url
        made = None
        
        # check for epubs
        obj = doc.select_one('a.epub-link')
        if obj:
            dl_url = urljoin(base, obj['href'])
            made = make_dl_ebook(dl_url, ebook, user_agent=settings.GOOGLEBOT_UA)

        # check for complete ebook
        obj = doc.find('a', string=COMPLETE)
        if obj:
            obj = obj.parent.parent.parent.select_one('a.pdf-link')
        else:
            obj = doc.find('a', href=DEGRUYTERFULL)
        if obj:
            dl_url = urljoin(base, obj['href'])
            made = make_dl_ebook(dl_url, ebook, user_agent=settings.GOOGLEBOT_UA)
            return made

        # staple the chapters
        pdflinks = [urljoin(base, a['href']) for a in doc.find_all('a', href=DEGRUYTERCHAP)]
        stapled = None
        if pdflinks:
            stapled = make_stapled_ebook(pdflinks, ebook, user_agent=settings.GOOGLEBOT_UA)
        if stapled:
            return stapled
        elif made:
            return made
        else:
            logger.warning('couldn\'t get dl_url for %s', ebook.url)
    else:
        logger.warning('couldn\'t get soup for %s', ebook.url)
    return None, 0

def harvest_dropbox(ebook):
    if ebook.url.find(u'dl=0') >= 0:
        dl_url = ebook.url.replace(u'dl=0', u'dl=1')
        return make_dl_ebook(dl_url, ebook)
    elif ebook.url.find(u'?') < 0:
        dl_url = ebook.url + u'?dl=1'
        return make_dl_ebook(dl_url, ebook)
    response = requests.get(ebook.url, headers={"User-Agent": settings.USER_AGENT})
    if response.status_code == 200:
        match_dl = DROPBOX_DL.search(response.content)
        if match_dl:
            return make_dl_ebook(match_dl.group(1), ebook)
        else:
            logger.warning('couldn\'t get %s', ebook.url)
    else:
        logger.warning('couldn\'t get dl for %s', ebook.url)
    return None, 0 
        
def harvest_jbe(ebook): 
    doc = get_soup(ebook.url)
    if doc:
        obj = doc.select_one('div.pdfItem a')
        if obj:
            dl_url = urljoin(ebook.url, obj['href'])
            return make_dl_ebook(dl_url, ebook)
        else:
            logger.warning('couldn\'t get dl_url for %s', ebook.url)
    else:
        logger.warning('couldn\'t get soup for %s', ebook.url)
    return None, 0

def harvest_transcript(ebook): 
    num = 0
    harvested = None
    doc = get_soup(ebook.url)
    if doc:
        objs = doc.select('a.content--link')
        for obj in objs:
            dl_url = urljoin(ebook.url, obj['href'])
            if dl_url.endswith('.pdf') or dl_url.endswith('.epub'):
                harvested, made = make_dl_ebook(dl_url, ebook)
                num += made
    if not harvested:
        logger.warning('couldn\'t get any dl_url for %s', ebook.url)
    return harvested, num

def harvest_ksp(ebook): 
    doc = get_soup(ebook.url)
    if doc:
        obj = doc.select_one('p.linkForPDF a')
        if obj:
            dl_url = urljoin(ebook.url, obj['href'])
            return make_dl_ebook(dl_url, ebook)
        else:
            logger.warning('couldn\'t get dl_url for %s', ebook.url)
    else:
        logger.warning('couldn\'t get soup for %s', ebook.url)
    return None, 0

def harvest_digitalis(ebook): 
    doc = get_soup(ebook.url)
    if doc:
        obj = doc.find('meta', attrs={"name": "citation_pdf_url"})
        if obj:
            dl_url = urljoin(ebook.url, obj.get('content', None))
            if dl_url:
                return make_dl_ebook(dl_url, ebook)
        else:
            logger.warning('couldn\'t get dl_url for %s', ebook.url)
    else:
        logger.warning('couldn\'t get soup for %s', ebook.url)
    return None, 0

NOMOSPDF = re.compile('download_full_pdf')
def harvest_nomos(ebook): 
    doc = get_soup(ebook.url)
    if doc:
        obj = doc.find('a', href=NOMOSPDF)
        if obj:
            dl_url = urljoin(ebook.url, obj['href'])
            return make_dl_ebook(dl_url, ebook)
        else:
            logger.warning('will try stabling a book for %s', ebook.url)

        # staple the chapters
        chaps = doc.select('li.access[data-doi]')
        
        pdflinks = []
        for chap in chaps:
            link = urljoin(
                'https://www.nomos-elibrary.de',
                chap['data-doi'] + '.pdf?download_full_pdf=1'
            )
            if link not in pdflinks:
                pdflinks.append(link)
        stapled = None
        if pdflinks:
            stapled = make_stapled_ebook(pdflinks, ebook, user_agent=settings.GOOGLEBOT_UA)
        if stapled:
            return stapled
        else:
            logger.warning('couldn\'t staple ebook  %s', ebook.url)
    else:
        logger.warning('couldn\'t get soup for %s', ebook.url)
    return None, 0

def harvest_frontiersin(ebook): 
    num = 0
    harvested = None
    doc = get_soup(ebook.url)
    if doc:
        for obj in doc.select('button[data-href]'):
            dl_url = obj['data-href']
            harvested, made = make_dl_ebook(
                dl_url,
                ebook,
                user_agent=requests.utils.default_user_agent(),
            )
            num += made
    if num == 0:
        logger.warning('couldn\'t get any dl_url for %s', ebook.url)
    return harvested, num

SPRINGERDL = re.compile(r'(EPUB|PDF|MOBI)')

def harvest_springerlink(ebook): 
    num = 0
    harvested = None
    doc = get_soup(ebook.url)
    if doc:
        found = []
        for obj in doc.find_all('a', title=SPRINGERDL):
            if obj.get('href'):
                dl_url = urljoin(ebook.url, obj.get('href'))
                if dl_url in found:
                    continue
                else:
                    found.append(dl_url)
                harvested, made = make_dl_ebook(dl_url, ebook)
                num += made
    if num == 0:
        logger.warning('couldn\'t get any dl_url for %s', ebook.url)
    return harvested, num

OAPENPDF = re.compile('^/bitstream.*\.pdf')

def harvest_oapen(ebook):
    for old_ebook in ebook.edition.work.ebooks():
        if (old_ebook.id != ebook.id and
                old_ebook.provider == ebook.provider and
                old_ebook.format == 'pdf'):            
            ebook.delete()
            return None, 0

    harvested = None
    made = 0
    if ebook.url.find('oapen.org/record') < 0:
        return None, 0

    doc = get_soup(ebook.url)
    try:
        base = doc.find('base')['href']
    except:
        base = ebook.url
    
    if doc:
        obj = doc.find('a', href=OAPENPDF)
        if obj:
            dl_url =  urljoin(base, obj['href'])
            harvested, made = make_dl_ebook(dl_url, ebook)
    if made == 0:
        logger.warning('couldn\'t get any dl_url for %s', ebook.url)
    return harvested, made


EDOCMAN = re.compile('component/edocman/')
def harvest_pulp(ebook):
    def edocman(url):
        if not EDOCMAN.search(url):
            return
        return url + '/download?Itemid='
    dl_url = edocman(ebook.url)
    if dl_url:
        return make_dl_ebook(dl_url, ebook, user_agent=requests.utils.default_user_agent())
    doc = get_soup(ebook.url)
    harvested = None
    made = 0
    if doc:
        obj = doc.find('a', href=EDOCMAN)
        if obj:
            dl_url =  edocman(urljoin(ebook.url, obj['href']))
            harvested, made = make_dl_ebook(dl_url, ebook,
                                            user_agent=requests.utils.default_user_agent())
    if made == 0:
        logger.warning('couldn\'t get any dl_url for %s or %s', ebook.url, dl_url)
    return harvested, made


def harvest_bloomsbury(ebook):
    doc = get_soup(ebook.url)
    if doc:
        pdflinks = []
        try:
            base = doc.find('base')['href']
        except:
            base = ebook.url
        for obj in doc.select('li.pdf-chapter--title a[href]'):
            if obj:
                chap = urljoin(base, obj['href']) + '.pdf?dl'
            pdflinks.append(chap)
        if pdflinks:
            stapled = make_stapled_ebook(pdflinks, ebook, strip_covers=True)
        if stapled:
            return stapled
        else:
            logger.warning('couldn\'t staple %s', pdflinks)
    else:
        logger.warning('couldn\'t get soup for %s', ebook.url)
    return None, 0

