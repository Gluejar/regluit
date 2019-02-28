import logging
import re
import time
import urlparse

import requests

from django.conf import settings
from django.core.files.base import ContentFile

from regluit.core.models import (
    Ebook, EbookFile, path_for_file,
)
from regluit.core.pdf import staple_pdf

from .utils import get_soup


logger = logging.getLogger(__name__)

DROPBOX_DL = re.compile(r'"(https://dl.dropboxusercontent.com/content_link/[^"]+)"')
DELAY = 5.0

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
        pass
    elif ebook.url.find(u'dropbox.com/s/') >= 0:
        for ebf in ebf_if_harvested(ebook.url):
            return ebf, False
        limiter(ebook.provider)
        if ebook.url.find(u'dl=0') >= 0:
            dl_url = ebook.url.replace(u'dl=0', u'dl=1')
            return make_dl_ebook(dl_url, ebook)
        response = requests.get(ebook.url, headers={"User-Agent": settings.USER_AGENT})
        if response.status_code == 200:
            match_dl = DROPBOX_DL.search(response.content)
            if match_dl:
                return make_dl_ebook(match_dl.group(1), ebook)
            else:
                logger.warning('couldn\'t get {}'.format(ebook.url))
        else:
            logger.warning('couldn\'t get dl for {}'.format(ebook.url))

    elif ebook.url.find(u'jbe-platform.com/content/books/') >= 0:
        for ebf in ebf_if_harvested(ebook.url):
            return ebf, False
        limiter(ebook.provider)
        doc = get_soup(ebook.url)
        if doc:
            obj = doc.select_one('div.fulltexticoncontainer-PDF a')
            if obj:
                dl_url = urlparse.urljoin(ebook.url, obj['href'])
                return make_dl_ebook(dl_url, ebook)
            else:
                logger.warning('couldn\'t get dl_url for {}'.format(ebook.url))
        else:
            logger.warning('couldn\'t get soup for {}'.format(ebook.url))
    elif ebook.url.find(u'degruyter') >= 0:
        for ebf in ebf_if_harvested(ebook.url):
            return ebf, False
        limiter(ebook.provider)
        doc = get_soup(ebook.url, settings.GOOGLEBOT_UA)
        if doc:
            try:
                base = doc.find('base')['href']
            except:
                base = ebook.url
            made = None
            obj = doc.select_one('a.epub-link')
            if obj:
                dl_url = urlparse.urljoin(base, obj['href'])
                made = make_dl_ebook(dl_url, ebook)
            pdflinks = [urlparse.urljoin(base, a['href']) for a in doc.select('a.pdf-link')]
            if pdflinks:
                made = make_stapled_ebook(pdflinks, ebook)
            if made:
                return made
            else:
                logger.warning('couldn\'t get dl_url for {}'.format(ebook.url))
        else:
            logger.warning('couldn\'t get soup for {}'.format(ebook.url))

    return None, False

def ebf_if_harvested(url):
    onlines = EbookFile.objects.filter(source=url)
    if onlines:
        return onlines
    return  EbookFile.objects.none()

def make_dl_ebook(url, ebook):
    response = requests.get(url, headers={"User-Agent": settings.USER_AGENT})
    if response.status_code == 200:
        filesize = int(response.headers.get("Content-Length", 0))
        filesize = filesize if filesize else None
        format = type_for_url(url, content_type=response.headers.get('content-type'))
        if format != 'online':
            return make_harvested_ebook(response.content, ebook, format, filesize=filesize)
        else:
            logger.warning('download format for {} is not ebook'.format(url))
    else:
        logger.warning('couldn\'t get {}'.format(url))
    return None, False

def make_stapled_ebook(urllist, ebook):
    pdffile =  staple_pdf(urllist, settings.GOOGLEBOT_UA)
    if not pdffile:
        return None, False
    return make_harvested_ebook(pdffile.getvalue(), ebook, 'pdf')

def make_harvested_ebook(content, ebook, format, filesize=0):
    if not filesize:
        filesize = len(content)
    new_ebf = EbookFile.objects.create(
        edition=ebook.edition,
        format=format,
        source=ebook.url,
    )
    new_ebf.file.save(path_for_file(new_ebf, None), ContentFile(content))
    new_ebf.save()
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
    return new_ebf, True
