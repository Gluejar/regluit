import logging
import re
import requests
import time
from urllib.parse import quote, unquote, urlparse, urlsplit, urlunsplit

from django.apps import apps
from django.conf import settings
from django.core.files.base import ContentFile
from django.forms import ValidationError

from regluit.core.validation import test_file
from regluit.core import models
#from . import Ebook, EbookFile

#Ebook = apps.get_model('core', 'Ebook')
#EbookFile = apps.get_model('core', 'EbookFile')

logger = logging.getLogger(__name__)

def type_for_url(url, content_type=None, force=False, disposition=''):
    url_disp = url + disposition
    if not url:
        return ''

    # check to see if we already know
    for ebook in models.Ebook.objects.filter(url=url):
        if ebook.format != 'online':
            return ebook.format

    if not force:
        if url.find('books.openedition.org') >= 0:
            return 'online'
    if content_type:
        ct = content_type
    else:
        ct, disposition = contenttyper.calc_type(url)
    url_disp = url + disposition
    binary_type = re.search("octet-stream", ct) or re.search("application/binary", ct)
    if re.search("pdf", ct):
        return "pdf"
    elif binary_type and re.search("pdf", url_disp, flags=re.I):
        return "pdf"
    elif binary_type and re.search("epub", url_disp, flags=re.I):
        return "epub"
    elif binary_type and re.search("mobi", url_disp, flags=re.I):
        return "mobi"
    elif re.search("text/plain", ct):
        return "text"
    elif re.search("text/html", ct):
        if url.find('oapen.org/view') >= 0:
            return "html"
        return "online"
    elif re.search("epub", ct):
        return "epub"
    elif re.search("mobi", ct):
        return "mobi"
    elif ct == '404':
        return ct
    # no content-type header!
    elif ct == '' and re.search("epub", url_disp, flags=re.I):
        return "epub"
    elif ct == '' and re.search("pdf", url_disp, flags=re.I):
        return "pdf"
    elif ct == '' and re.search("mobi", url_disp, flags=re.I):
        return "mobi"

    return "other"

def requote(url):
    # fallback for non-ascii, non-utf8 bytes in redirect location
    (scheme, netloc, path, query, fragment) = urlsplit(url)
    try:
        newpath = quote(unquote(path), encoding='latin1')
    except UnicodeEncodeError as uee:
        return ''
    return urlunsplit((scheme, netloc, newpath, query, fragment))
    
class ContentTyper(object):
    """ """
    def __init__(self):
        self.last_call = dict()

    def content_type(self, url):
        def handle_ude(url, ude):
            url = requote(url)
            try:
                return requests.get(url, allow_redirects=True)
            except:
                logger.error('Error processing %s after unicode error', url)

        try:
            try:
                r = requests.head(url, allow_redirects=True)
                if r.status_code == 405:
                    try:
                        r =  requests.get(url)
                    except UnicodeDecodeError as ude:
                        if 'utf-8' in str(ude):
                            r = handle_ude(url, ude)
            except UnicodeDecodeError as ude:
                if 'utf-8' in str(ude):
                    r = handle_ude(url, ude)
        except requests.exceptions.SSLError:
            try:
                r = requests.get(url, verify=False)
            except:
                logger.error('Error processing %s verification off', url)
                return '', ''
        except:
            logger.error('Error processing %s', url)
            return '', ''
        if not r:
            return '', ''
        if r.status_code == 404:
            logger.error('File not found (404) for %s', url)
            return '404', ''
        return r.headers.get('content-type', ''), r.headers.get('content-disposition', '')

    def calc_type(self, url):
        logger.info(url)
        # is there a delay associated with the url
        netloc = urlparse(url).netloc
        delay = 0.1 if 'oapen.org' in netloc else 1

        # wait if necessary
        last_call = self.last_call.get(netloc)
        if last_call is not None:
            now = time.time()
            min_time_next_call = last_call + delay
            if min_time_next_call > now:
                time.sleep(min_time_next_call-now)

        self.last_call[netloc] = time.time()

        # compute the content-type
        return self.content_type(url)

contenttyper = ContentTyper()

def load_ebookfile(url, format, user_agent=settings.USER_AGENT, method='GET', verify=True):
    '''
    return a ContentFile, format if a new ebook has been loaded
    '''
    ebfs = models.EbookFile.objects.filter(source=url)
    if ebfs:
        return None, ''
    try:
        if method == 'POST':
            response = requests.post(url, headers={"User-Agent": user_agent}, verify=verify)
        else:
            response = requests.get(url, headers={"User-Agent": user_agent}, verify=verify)

    except requests.exceptions.SSLError:
        logger.error('bad certificate? for %s', url)
        return None, ''
    except IOError as e:
        logger.error('could not open %s', url)
        return None, ''
    except UnicodeDecodeError as e:
        logger.error('decoding error for %s', url)
        url = requote(url)
        try:
            response = requests.get(url, headers={"User-Agent": user_agent}, verify=verify)
        except:
            return None, ''

    if response.status_code == 200:
        logger.debug(response.headers.get('content-type', ''))
        resp_format = type_for_url(url, 
                              content_type=response.headers.get('content-type', ''),
                              disposition=response.headers.get('content-disposition', ''))
        if resp_format == 'online' or (format != 'online' and resp_format != format):
            logger.warning('response format %s for %s is not correct', resp_format, url)
            return None, resp_format
    else:
        logger.warning('couldn\'t get %s', url)
        return None, ''

    contentfile = ContentFile(response.content)
    try:
        test_file(contentfile, resp_format)
        return contentfile, resp_format
    except ValidationError as e:
        logger.error('downloaded %s was not a valid %s', url, format)
        None, resp_format
        

