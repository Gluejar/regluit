"""
code for harvesting 'online' ebooks
"""
import json
import logging
import re
import time
from urllib.parse import urljoin, quote

import requests

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from regluit.core import models
from regluit.core.models import loader
from regluit.core.parameters import GOOD_PROVIDERS, DOWNLOADABLE
from regluit.core.pdf import staple_pdf

from .soup import get_soup
from .doab_utils import STOREPROVIDERS

logger = logging.getLogger(__name__)

DROPBOX_DL = re.compile(r'"(https://dl.dropboxusercontent.com/content_link/[^"]+)"')
DELAY = 1.0

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

def set_bookshop(ebook):
    ebook.format = 'bookshop'
    ebook.save()
    return None, 0


def dl_online(ebook, limiter=rl.delay, format='online', force=False):
    if ebook.format != format or (not force and ebook.provider in DONT_HARVEST):
        return None, 0
    if ebook.provider in STOREPROVIDERS:
        return set_bookshop(ebook)
    if ebook.ebook_files.exists():
        return ebook.ebook_files.first(), 0
    for do_harvest, harvester in harvesters(ebook):
        if do_harvest:
            for ebf in ebf_if_harvested(ebook.url):
                clean_archive(ebf)
                return ebf, 0
            limiter(ebook.provider)
            return harvester(ebook)
    return None, 0

def archive_dl(ebook, limiter=rl.delay, force=False):
    """ status codes
        0 : archive exists
        1 : archive made
       -1 : urls does not return an ebook file
    """
    status = -1
    ebf = None
    if ebook.ebook_files.filter(asking=False).exists():
        status = 0
    elif models.EbookFile.objects.filter(source=ebook.url, format=ebook.format).exists():
        status = 0
    else:
        dl_cf, fmt = loader.load_ebookfile(ebook.url, ebook.format)
        if dl_cf:
            ebf, num =  make_harvested_ebook(dl_cf, ebook, fmt, filesize=dl_cf.size)
            clean_archive(ebf)
            status = 1
        else:
            logger.warning('download format %s for %s is not ebook', ebook.format, ebook.url)
        limiter(ebook.provider)
        if not ebf:
            status = -1
    return status

def clean_archive(ebf):
    fsize = ebf.ebook.filesize
    ebook = ebf.ebook
    if not fsize or ebf.asking == 1 or ebook.format not in DOWNLOADABLE or not ebook.active:
        return
    # find duplicate files by looking at filesize
    old_ebooks = models.Ebook.objects.filter(filesize=fsize, provider=ebf.ebook.provider,
        edition__work=ebf.edition.work, format=ebf.format
    ).exclude(id=ebf.ebook.id)
    for old_ebook in old_ebooks:
        old_ebook.active = False
        for oldebf in old_ebook.ebook_files.exclude(id=ebf.id):
            if oldebf.file != ebf.file:
                # save storage by deleting redundant files
                oldebf.file.delete()
                oldebf.file = ebf.file
                oldebf.save()
        old_ebook.save()


CMPPROVIDERS = [
    'books.open.tudelft.nl',
    'ebooks.epublishing.ekt.gr',
    'ebooks.uminho.pt',
    'editorial.inudi.edu.pe',
    'editorial.ucatolicaluisamigo.edu.co',
    'editorial.uniagustiniana.edu.co',
    'fcjp.derecho.unap.edu.pe',
    'fedoabooks.unina.it',
    'humanities-digital-library.org',
    'idicap.com',
    'libri.unimi.it',
    'llibres.urv.cat',
    'Scholars Portal',
    'monographs.uc.pt',
    'omp.ub.rub.de',
    'omp.zrc-sazu.si',
    'openpress.mtsu.edu',
    'teiresias-supplements.mcgill.ca',
    'textbooks.open.tudelft.nl',
]
DONT_HARVEST = [
    'Unglue.it',
    'Github',
    'Project Gutenberg',
    'Google Books',
    'OpenEdition Books',
]
MANUAL_HARVEST = [
    'cabidigitallibrary.org',
    'books.google.be',
    'books.google.ch',
    'books.google.nl',
]

def harvesters(ebook):
    yield ebook.provider == 'OAPEN Library', harvest_oapen
    yield ebook.provider in GOOD_PROVIDERS, harvest_generic
    yield ebook.provider in MANUAL_HARVEST, harvest_manual
    yield 'dropbox.com/s/' in ebook.url, harvest_dropbox
    yield ebook.provider == 'jbe-platform.com', harvest_jbe
    yield ebook.provider == u'De Gruyter Online', harvest_degruyter
    yield ebook.provider == 'Open Book Publishers', harvest_obp
    yield ebook.provider == 'Transcript-Verlag', harvest_transcript
    yield ebook.provider == 'shop.budrich.de', harvest_budrich
    yield ebook.provider == 'ksp.kit.edu', harvest_ksp
    yield ebook.provider in ['repositorio.americana.edu.co'], harvest_dspace2
    yield ebook.provider == 'nomos-elibrary.de', harvest_nomos
    yield ebook.provider == 'digitalis.uc.pt', harvest_digitalis
    yield 'frontiersin.org' in ebook.provider, harvest_frontiersin
    yield ebook.provider in ['Palgrave Connect', 'Springer', 'springer.com'], harvest_springerlink
    yield ebook.provider == 'pulp.up.ac.za', harvest_pulp
    yield ebook.provider == 'bloomsburycollections.com', harvest_bloomsbury
    yield ebook.provider == 'Athabasca University Press', harvest_athabasca
    yield 'digitalcommons.usu.edu' in ebook.url, harvest_usu
    yield ebook.provider == 'libros.fahce.unlp.edu.ar', harvest_fahce
    yield ebook.provider in ['digital.library.unt.edu', 'texashistory.unt.edu'], harvest_unt
    yield ebook.provider in ['diposit.ub.edu', 'orbi.ulg.ac.be', 'orbi.uliege.be',
                             'acikerisim.kapadokya.edu.tr',], harvest_dspace
    yield ebook.provider in CMPPROVIDERS, harvest_cmp
    yield 'mdpi' in ebook.provider.lower(), harvest_mdpi
    yield ebook.provider == 'idunn.no', harvest_idunn
    yield ebook.provider == 'press.ucalgary.ca', harvest_calgary
    yield ebook.provider in ['Ledizioni', 'bibsciences.org',
                             'heiup.uni-heidelberg.de', 'e-archivo.uc3m.es'], harvest_generic
    yield ebook.provider == 'muse.jhu.edu', harvest_muse
    yield ebook.provider == 'direct.mit.edu', harvest_mitpress
    yield ebook.provider == 'IOS Press Ebooks', harvest_ios
    yield ebook.provider == 'elgaronline.com', harvest_elgar
    yield ebook.provider == 'worldscientific.com', harvest_wsp
    yield ebook.provider in ['edition-open-access.de', 'edition-open-sources.org'], harvest_mprl
    yield ebook.provider == 'rti.org', harvest_rti
    yield ebook.provider == 'edoc.unibas.ch', harvest_unibas
    yield 'pensoft' in ebook.provider, harvest_pensoft
    yield ebook.provider == 'edp-open.org', harvest_edp
    yield ebook.provider == 'laboutique.edpsciences.fr', harvest_edpsciences
    yield ebook.provider == 'waxmann.com', harvest_waxmann
    yield ebook.provider == 'pbsociety.org.pl', harvest_ojs
    yield 'sciendo.com' in ebook.provider, harvest_sciendo
    yield ebook.provider == 'edition-topoi.org', harvest_topoi
    yield ebook.provider == 'meson.press', harvest_meson    
    yield 'brill' in ebook.provider, harvest_brill
    yield ebook.provider == 'DOI Resolver', harvest_doi
    yield ebook.provider in ['apps.crossref.org', 'mr.crossref.org'], harvest_doi_coaccess
    yield ebook.provider == 'ispf-lab.cnr.it', harvest_ipsflab 
    yield ebook.provider == 'libros.uchile.cl', harvest_libroschile
    yield ebook.provider == 'smithsonian.figshare.com', harvest_figshare
    yield ebook.provider == 'fupress.com', harvest_fupress
    yield ebook.provider == 'funlam.edu.co', harvest_funlam
    yield ebook.provider == 'elibrary.duncker-humblot.com', harvest_dunckerhumblot
    yield ebook.provider == 'cornellopen.org', harvest_cornellopen
    yield ebook.provider == 'esv.info', harvest_esv
    yield ebook.provider == 'fulcrum.org', harvest_fulcrum
    yield ebook.provider in ('epress.lib.uts.edu.au', 'utsepress.lib.uts.edu.au'), harvest_ubiquity
    yield ebook.provider == 'orkana.no', harvest_orkana
    yield ebook.provider == 'euna.una.ac.cr', harvest_euna
    yield ebook.provider == 'openresearchlibrary.org', harvest_orl
    yield ebook.provider == 'pressesagro.be', harvest_pressesagro
    yield ebook.provider == 'buponline.com', harvest_buponline
    yield ebook.provider == 'intechopen.com', harvest_intech
    yield ebook.provider == 'usmcu.edu', harvest_usmcu
    yield ebook.provider == 'lalibreria.upv.es', harvest_upv
    yield ebook.provider == 'cambridge.org', harvest_cambridge
    yield ebook.provider == 'exonpublications.com', harvest_exon
    yield ebook.provider == 'ressources.una-editions.fr', harvest_una
    yield ebook.provider == 'wbg-wissenverbindet.de', harvest_wbg
    yield ebook.provider == 'urn.kb.se', harvest_kb
    yield ebook.provider == 'publikationen.bibliothek.kit.edu', harvest_kit
    yield ebook.provider == 'iupress.istanbul.edu.tr', harvest_istanbul
    yield ebook.provider == 'editorialbonaventuriana.usb.edu.co', harvest_editorialbonaventuriana
    yield ebook.provider == 'verlag.gta.arch.ethz.ch', harvest_gta
    yield ebook.provider == 'manchesteruniversitypress.co.uk', harvest_manu

def ebf_if_harvested(url):
    onlines = models.EbookFile.objects.filter(source=url)
    if onlines.exists():
        return onlines
    return  models.EbookFile.objects.none()


def make_dl_ebook(url, ebook, user_agent=settings.USER_AGENT, method='GET',  verify=True):
    if not url:
        logger.warning('no url for ebook %s', ebook.id)
        return None, 0
    logger.info('making %s' % url)

    # check to see if url already harvested
    for ebf in ebf_if_harvested(url):
        # these ebookfiles are created to short-circuit dl_online to avoid re-harvest
        if ebf.ebook == ebook:
            return ebf, 0
        new_ebf = models.EbookFile.objects.create(
            edition=ebf.edition,
            format=ebf.format,
            file=ebf.file,
            source=ebook.url,
            ebook=ebook,
        )
        logger.info("Previously harvested")
        return new_ebf, 0

    
    dl_cf, fmt = loader.load_ebookfile(url, ebook.format,
                                       user_agent=user_agent, method=method, verify=verify)
    if dl_cf:
        return make_harvested_ebook(dl_cf, ebook, fmt, filesize=dl_cf.size)
    else:
        logger.warning('download format %s for %s is not ebook', ebook.format, url)
    return None, 0

def redirect_ebook(ebook):
    """ returns an ebook and status :
        -3 : bad return code or problem
        -1 : deleted
        -2 : dead, but we need to keep items
         0 : replaced with existing
         1 : url updated
         
    """
    try:
        r = requests.head(ebook.url, allow_redirects=True)
    except requests.exceptions.ConnectionError as e:
        logger.error("Connection refused for %s", url)
        logger.error(e)
        return ebook, -3
    
    if r.status_code == 404:
        if not models.Ebook.ebook_files.exists():
            logger.info('deleting ebook for dead url', ebook.url)
            ebook.delete()
            return None, -1
        return ebook, -2
    elif r.status_code == 200:
        if ebook.url != r.url:
            if models.Ebook.objects.exclude(id=ebook.id).filter(url=r.url).exists():
                return models.Ebook.objects.filter(url=r.url)[0], 0
            ebook.url = r.url
            ebook.set_provider()
            ebook.save()
            return ebook, 1
    logger.error("status code %s for %s", r.status_code, ebook.url)
    return ebook, -3

def make_stapled_ebook(urllist, ebook, user_agent=settings.USER_AGENT, strip_covers=False):
    pdffile = staple_pdf(urllist, user_agent, strip_covers=strip_covers)
    if not pdffile:
        return None, 0
    return make_harvested_ebook(ContentFile(pdffile.getvalue()), ebook, 'pdf')

def make_harvested_ebook(content, ebook, format, filesize=0):
    if not filesize:
        filesize = len(content)
    new_ebf = models.EbookFile.objects.create(
        edition=ebook.edition,
        format=format,
        source=ebook.url,
    )
    try:
        new_ebf.file.save(models.path_for_file(new_ebf, None), content)
        new_ebf.save()
    except MemoryError:  #huge pdf files cause problems here
        logger.error("memory error saving ebook file for %s", ebook.url)
        new_ebf.delete()
        return None, 0
    if ebook.format == "online":
        harvested_ebook = models.Ebook.objects.create(
            edition=ebook.edition,
            format=format,
            provider='Unglue.it',
            url=new_ebf.file.url,
            rights=ebook.rights,
            filesize=filesize if filesize < 2147483647 else 2147483647, # largest safe integer
            version_label=ebook.version_label,
            version_iter=ebook.version_iter,
        )
    else:
        if not ebook.filesize:
            ebook.filesize = filesize if filesize < 2147483647 else 2147483647
            ebook.save()
        harvested_ebook = ebook
        
    new_ebf.ebook = harvested_ebook
    new_ebf.save()
    return new_ebf, 1

def is_bookshop_url(url):
    if '/prodotto/' in url:
        return True
    if ':' in url and url.split(':')[1].startswith('//library.oapen.org/handle/'):
        return True
    return False

def harvest_generic(ebook):
    if is_bookshop_url(ebook.url):
        return set_bookshop(ebook)        
    return make_dl_ebook(ebook.url, ebook)


def harvest_manual(ebook):
    def make_manual_ebf(format):
        fname = f'mebf/{ebook.id}.{format}'
        if default_storage.exists(fname):
            filesize = default_storage.size(fname)
            new_ebf = models.EbookFile.objects.create(
                edition=ebook.edition,
                format=format,
                source=ebook.url,
            )
            new_ebf.file.name = fname
            harvested_ebook = models.Ebook.objects.create(
                edition=ebook.edition,
                format=format,
                provider='Unglue.it',
                url=new_ebf.file.url,
                rights=ebook.rights,
                filesize=filesize,
                version_label=ebook.version_label,
                version_iter=ebook.version_iter,
            )
            new_ebf.ebook = harvested_ebook
            new_ebf.save()
            return new_ebf
        else:
            return None
    pdf_ebf = make_manual_ebf('pdf')
    epub_ebf = make_manual_ebf('epub')

    return pdf_ebf or epub_ebf, (1 if pdf_ebf else 0) + (1 if epub_ebf else 0)


def harvest_oapen(ebook):
    if is_bookshop_url(ebook.url):
        return set_bookshop(ebook)        
    if '/bitstream/' in ebook.url:
        return make_dl_ebook(ebook.url, ebook, user_agent=settings.GOOGLEBOT_UA)
    return None, 0


def harvest_one_generic(ebook, selector, user_agent=settings.USER_AGENT):
    doc = get_soup(ebook.url, user_agent=user_agent, follow_redirects=True)
    if doc:
        try:
            base = doc.find('base')['href']
        except:
            base = ebook.url
        obj = selector(doc)
        if obj:
            dl_url = urljoin(base, obj['href'])
            harvest = make_dl_ebook(dl_url, ebook, user_agent=user_agent)
            if not harvest[0]:
                logger.warning('couldn\'t harvest %s', dl_url)
            return harvest
        else:
            logger.warning('couldn\'t get dl_url for %s', ebook.url)
    else:
        logger.warning('couldn\'t get soup for %s', ebook.url)
    return None, 0


def harvest_multiple_generic(ebook, selector, dl=lambda x:x):
    num = 0
    harvested = None
    doc = get_soup(ebook.url, follow_redirects=True)
    if doc:
        found = []
        try:
            base = doc.find('base')['href']
        except:
            base = ebook.url
        for obj in selector(doc):
            dl_url = dl(urljoin(base, obj.get('href')))
            logger.info(dl_url)
            if dl_url in found:
                continue
            else:
                found.append(dl_url)
            harvested, made = make_dl_ebook(dl_url, ebook)
            num += made
    if num == 0:
        logger.warning('couldn\'t get any dl_url for %s', ebook.url)
    return harvested, num


def harvest_stapled_generic(ebook, selector, chap_selector, strip_covers=0,
                            user_agent=settings.GOOGLEBOT_UA, dl=lambda x:x):
    doc = get_soup(ebook.url, user_agent=user_agent, follow_redirects=True)
    if doc:
        try:
            base = doc.find('base')['href']
        except:
            base = ebook.url
        made = None
        
        # check for complete ebook
        if selector:
            obj = selector(doc)
            if obj:
                dl_url = dl(urljoin(base, obj['href']))
                made = make_dl_ebook(dl_url, ebook)
            if made:
                return made

        # staple the chapters
        pdflinks = [dl(urljoin(base, a['href'])) for a in chap_selector(doc)]
        stapled = None
        if pdflinks:
            stapled = make_stapled_ebook(pdflinks, ebook, user_agent=user_agent,
                                         strip_covers=strip_covers)
            if stapled:
                return stapled

        logger.warning('couldn\'t make ebook file for %s', ebook.url)
    else:
        logger.warning('couldn\'t get soup for %s', ebook.url)
    return None, 0

OPENBOOKPUB =  re.compile(r'openbookpublishers.com/+(reader|product|/?download/book|books)/(10\.11647/OBP\.\d+|\d+)')

def harvest_obp(ebook):    
    match = OPENBOOKPUB.search(ebook.url)
    booknum = None
    if not match:
        return None, 0
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
    elif match and match.group(2).startswith('10.'):
        dl_url = 'https://books.openbookpublishers.com/' + match.group(2).lower() + '.pdf'
        return make_dl_ebook(dl_url, ebook, user_agent=settings.GOOGLEBOT_UA)
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
DOWNLOAD = re.compile(r' *download *', flags=re.I)

def harvest_degruyter(ebook):
    ebook, status = redirect_ebook(ebook)
    if status < 1:
        return None, -1 if status < 0 else 0

    doc = get_soup(ebook.url, settings.GOOGLEBOT_UA)
    if doc:
        try:
            base = doc.find('base')['href']
        except:
            base = ebook.url
        made = 0
        harvested = None

        # check for epub
        obj = doc.select_one('a.downloadEpub')
        if obj:
            dl_url = urljoin(base, obj['href'])
            harvested, made = make_dl_ebook(dl_url, ebook, user_agent=settings.GOOGLEBOT_UA)
        
        # check for pdf
        obj = doc.select_one('a.downloadPdf')
        if obj:
            dl_url = urljoin(base, obj['href'])
            harvested, madepdf = make_dl_ebook(dl_url, ebook, user_agent=settings.GOOGLEBOT_UA)
            made = made + madepdf
        if made:
            return harvested, made

        # none yet, check for complete ebook
        obj = doc.find('a', string=COMPLETE)
        if obj:
            obj = obj.parent.parent.parent.select_one('a.pdf-link')
        else:
            obj = doc.find('a', href=DEGRUYTERFULL)
        if obj:
            dl_url = urljoin(base, obj['href'])
            return make_dl_ebook(dl_url, ebook, user_agent=settings.GOOGLEBOT_UA)

        # staple the chapters
        pdflinks = [urljoin(base, a['href']) for a in doc.find_all('a', href=DEGRUYTERCHAP)]
        stapled = None
        if pdflinks:
            stapled = make_stapled_ebook(pdflinks, ebook, user_agent=settings.GOOGLEBOT_UA)
        if stapled:
            return stapled
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
    def selector(doc):
        return doc.select('div.access-options a[href]')
    return harvest_multiple_generic(ebook, selector)

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
    def selector(doc):
        return doc.select_one('p.linkForPDF a')
    return harvest_one_generic(ebook, selector)


def harvest_digitalis(ebook): 
    def selector(doc):
        return doc.select_one('a.item-download-button')
    return harvest_one_generic(ebook, selector)


def harvest_kit(ebook): 
    def selector(doc):
        return doc.select_one('a.downloadTextLink')
    return harvest_one_generic(ebook, selector)


def harvest_budrich(ebook): 
    def selector(doc):
        return doc.select_one('a.download_pdf')
    return harvest_one_generic(ebook, selector)


NOMOSPDF = re.compile('download_full_pdf')
def harvest_nomos(ebook): 
    doc = get_soup(ebook.url, follow_redirects=True)
    try:
        base = doc.find('base')['href']
    except:
        base = ebook.url

    if doc:
        obj = doc.find('a', href=NOMOSPDF)
        if obj:
            dl_url = urljoin(base, obj['href'])
            return make_dl_ebook(dl_url, ebook)
        else:
            logger.warning('will try stapling a book for %s', ebook.url)

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
    if 'GetFile.aspx' in ebook.url:
        ebook.delete()
        rl.last.pop(ebook.provider, 0)
        return None, 0
    
    num = 0
    harvested = None
    doc = get_soup(ebook.url, follow_redirects=True)
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

SPRINGERDL = re.compile(r'(EPUB|PDF)')

def harvest_springerlink(ebook): 
    def selector(doc):
        return doc.find_all('a', title=SPRINGERDL)
    if ebook.provider == "springer.com":
        doc = get_soup(ebook.url)
        if  doc:
            obj = doc.select_one(".extra-materials a.btn-secondary[href]")
            if obj:
                url = obj['href']
                if models.Ebook.objects.exclude(id=ebook.id).filter(url=url).exists():
                    set_bookshop(ebook)
                    return models.Ebook.objects.filter(url=url)[0], 0
                ebook.url = url
                ebook.save()
    return harvest_multiple_generic(ebook, selector)


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
    doc = get_soup(ebook.url, follow_redirects=True)
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
        stapled = None
        if pdflinks:
            stapled = make_stapled_ebook(pdflinks, ebook, strip_covers=True)
        if stapled:
            return stapled
        else:
            logger.warning('couldn\'t staple %s', pdflinks)
    else:
        logger.warning('couldn\'t get soup for %s', ebook.url)
    return None, 0

def harvest_athabasca(ebook):
    def selector(doc):
        return doc.select_one('li.downloadPDF a[href]')
    return harvest_one_generic(ebook, selector)


def harvest_usu(ebook):
    def selector(doc):
        return doc.select_one('#full-text a[href]')
    return harvest_one_generic(ebook, selector)


def harvest_fahce(ebook):
    def selector(doc):
        return doc.select_one('div.pub_format_single a[href]')
    return harvest_one_generic(ebook, selector)

def get_meta(doc, term):
    obj = doc.find('meta', attrs={"name": term})
    if obj:
        return obj.get('content', None)
    else:
        logger.warning(f'no meta for {term}')


BAD_CERTS = {'libri.unimi.it', 'editorial.ucatolicaluisamigo.edu.co', 'openpress.mtsu.edu'}
def harvest_cmp(ebook):
    def selector(doc):
        citation_pdf_url = get_meta(doc, "citation_pdf_url")
        citation_epub_url = get_meta(doc, "citation_epub_url")
        if citation_pdf_url or citation_epub_url:
            if citation_pdf_url:
                yield {'href': citation_pdf_url}
            if citation_epub_url:
                yield {'href': citation_epub_url}
        else:
            objs = doc.select('.chapters a.cmp_download_link[href]')
            if (len({obj['href'] for obj in objs})) > 1:
                return []
            return doc.select('a.cmp_download_link[href]')

    def dl(url):
        return url.replace('view', 'download') + '?inline=1'

    verify = ebook.provider not in BAD_CERTS
    if '/view/' in ebook.url:
        return make_dl_ebook(dl(ebook.url), ebook, verify=verify)

    return harvest_multiple_generic(ebook, selector, dl=dl)


DSPACEPDF = re.compile(r'/bitstream/.*\.pdf')
def harvest_dspace(ebook):
    def selector(doc):
        return doc.find(href=DSPACEPDF)
    return harvest_one_generic(ebook, selector)

def harvest_dspace2(ebook): 
    doc = get_soup(ebook.url)
    if doc:
        citation_pdf_url = get_meta(doc, "citation_pdf_url")
        if citation_pdf_url:
            dl_url = urljoin(ebook.url, citation_pdf_url)
            dl_url = dl_url.replace('http://', 'https://')
            return make_dl_ebook(dl_url, ebook)
        else:
            logger.warning('couldn\'t get dl_url for %s', ebook.url)
    else:
        logger.warning('couldn\'t get soup for %s', ebook.url)
    return None, 0


# won't harvest page-image books
def harvest_unt(ebook):
    def selector(doc):
        return doc.select_one('#link-pdf-version[href]')
    return harvest_one_generic(ebook, selector)


def harvest_mdpi(ebook):
    def selector(doc):
        return doc.select_one('div.main-download-container a[alt=download]')
    if 'http://books.mdpi.com' in ebook.url:
        ebook.delete()
        return None, 0
    elif 'img.mdpi.org' in ebook.url:
        return harvest_generic(ebook)
    elif ebook.url.find('mdpi.com/books/pdfview/book/') >= 0:
        url = ebook.url.replace('pdfview', 'pdfdownload')
        return make_dl_ebook(url, ebook)
    return harvest_one_generic(ebook, selector)


def harvest_idunn(ebook):
    if '/doi/book/' in ebook.url:
        return harvest_manual(ebook)

    doc = get_soup(ebook.url)
    if doc:
        obj = doc.select_one('#accessinfo[data-product-id]')
        if obj:
            pdf_id = obj.get('data-pdf-id', '')
            prod_id = obj.get('data-product-id', '')
            filename = obj.get('data-issue-pdf-url', ebook.url[:21])
            dl_url = 'https://www.idunn.no/file/pdf/%s/%s.pdf' % (pdf_id, filename)
            ebf, num = make_dl_ebook(dl_url, ebook)
            if ebf:
                return ebf, num
            dl_url = 'https://www.idunn.no/file/pdf/%s/%s.pdf' % (prod_id, filename)
            return make_dl_ebook(dl_url, ebook)
    return None, 0


def harvest_calgary(ebook):
    def selector(doc):
        return doc.find('a', string=re.compile('Full Text'))
    def chap_selector(doc):
        return doc.find_all('a', href=re.compile('/bitstream/'))
    return harvest_stapled_generic(ebook, selector, chap_selector, strip_covers=2)


def harvest_muse(ebook):
    def chap_selector(doc):
        return doc.find_all('a', href=re.compile(r'/chapter/\d+/pdf'))
    return harvest_stapled_generic(ebook, None, chap_selector, strip_covers=1)

def harvest_mitpress(ebook):
    def chap_selector(doc):
        return doc.select('a.section-pdfLink[href]')
    return harvest_stapled_generic(ebook, None, chap_selector, strip_covers=0)


def harvest_ios(ebook):    
    booknum = None
    doc = get_soup(ebook.url)
    if doc:
        obj = doc.find('link', rel='image_src', href=True)
        if obj:
            booknum = obj['href'].replace('http://ebooks.iospress.nl/Cover/', '')
            if booknum:
                dl_url = 'http://ebooks.iospress.nl/Download/Pdf?id=%s' % booknum
                return make_dl_ebook(dl_url, ebook, method='POST')
            else:
                logger.warning('couldn\'t get booknum for %s', ebook.url)
        else:
            logger.warning('couldn\'t get link for %s', ebook.url)
    else:
        logger.warning('couldn\'t get soup for %s', ebook.url)
    return None, 0


def harvest_elgar(ebook):
    if 'display' in ebook.url:
        url = ebook.url.replace('display', 'downloadpdf')[:-3] + 'pdf'
    elif 'monobook-oa' in ebook.url:
        url = ebook.url.replace('monobook-oa', 'downloadpdf')[:-3] + 'pdf'
    elif 'edcollbook-oa' in ebook.url:
        url = ebook.url.replace('edcollbook-oa', 'downloadpdf')[:-3] + 'pdf'
    else:
        return None, 0
    return make_dl_ebook(url, ebook, user_agent=settings.GOOGLEBOT_UA)


def harvest_wsp(ebook):
    idmatch = re.search(r'1142/(\d+)', ebook.url)
    if idmatch:
        url = 'https://www.worldscientific.com/doi/pdf/10.1142/%s?download=true' % idmatch.group(1)
        return make_dl_ebook(url, ebook, user_agent=settings.CHROME_UA)
    return None, 0

def harvest_mprl(ebook): 
    def selector(doc):
        return doc.select('a.ml-20[href]')
    return harvest_multiple_generic(ebook, selector)


def harvest_rti(ebook):
    def selector(doc):
        return doc.find('a', href=re.compile('fulltext.pdf'))
    return harvest_one_generic(ebook, selector)


def harvest_unibas(ebook):
    def selector(doc):
        return doc.select_one('a.ep_document_link[href]')
    return harvest_one_generic(ebook, selector)

PENSOFT = re.compile(r'/book/(\d+)/list/')
def harvest_pensoft(ebook):
    if ebook.id == 263395:
        book_id = '12847'
    elif ebook.url.startswith('https://books.pensoft.net/books/'):
        book_id = ebook.url[32:]
    elif PENSOFT.search(ebook.url):
        book_id = PENSOFT.search(ebook.url).group(1)
    else:
        return None, 0
    r = requests.get('https://books.pensoft.net/api/books/' + book_id)
    if r.status_code == 200:
        try:
            file_id = r.json()['data']['item_files'][0]['id']
            return make_dl_ebook('https://books.pensoft.net/api/item_files/%s' % file_id, ebook)
        except IndexError:
            logger.error('no item_file for %s', ebook.url)
    return None, 0


def harvest_edp(ebook):
    def selector(doc):
        return doc.select_one('a.fulldl[href]')
    if ebook.url.endswith('.pdf'):
        return harvest_generic(ebook)
    return harvest_one_generic(ebook, selector)


def harvest_edpsciences(ebook):
    def selector(doc):
        return doc.select_one('.article-open-access-download-cell a[href]')
    return harvest_one_generic(ebook, selector)


def harvest_waxmann(ebook):
    if ebook.url.startswith('https://www.waxmann.com/buch'):
        return make_dl_ebook(ebook.url.replace('buch', 'index.php?eID=download&buchnr='), ebook) 
    return None, 0


def harvest_ojs(ebook):
    def selector(doc):
        return doc.select('#articleFullText a[href]')
    def dl(url):
        return url.replace('view', 'download') + '?inline=1'
    return harvest_multiple_generic(ebook, selector, dl=dl)


def harvest_topoi(ebook):    
    def selector(doc):
        return doc.select_one('li.pdf a[href]')
    return harvest_one_generic(ebook, selector)


def harvest_meson(ebook):    
    def selector(doc):
        for btn in doc.select('a[href] btn.btn-openaccess'):
            yield btn.parent
    return harvest_multiple_generic(ebook, selector)


def harvest_brill(ebook):
    r = requests.get(ebook.url, headers={'User-Agent': settings.GOOGLEBOT_UA})
    if r.url.startswith('https://brill.com/view/title/'):
        dl_url = 'https://brill.com/downloadpdf/title/%s.pdf' % r.url[29:]
        return make_dl_ebook(dl_url, ebook, user_agent=settings.GOOGLEBOT_UA)
    elif r.url.startswith('https://brill.com/display/title/'):
        dl_url = 'https://brill.com/downloadpdf/title/%s.pdf' % r.url[32:]
        return make_dl_ebook(dl_url, ebook, user_agent=settings.GOOGLEBOT_UA)
    elif r.url.startswith('https://brill.com/edcollbook-oa/title/'):
        dl_url = 'https://brill.com/downloadpdf/title/%s.pdf' % r.url[38:]
        return make_dl_ebook(dl_url, ebook, user_agent=settings.GOOGLEBOT_UA)
    return None, 0
    
def harvest_doi(ebook):
    # usually a 404.
    ebook, status = redirect_ebook(ebook)
    if status == -2:
        return None, -1
    return None, 0

def harvest_doi_coaccess(ebook):
    # make a new ebook for the "main pub" and ignore the "related pub"
    if ebook.url.startswith('https://doi.org/'):
        api_url = 'https://apps.crossref.org/search/coaccess?doi=%s' % quote(
            ebook.url[16:], safe='')
        r = requests.get(api_url)
        if r.status_code == 200:
            data = r.json()
            url = data.get('url', '')
            if not url:
                return None, 0
            if models.Ebook.objects.exclude(id=ebook.id).filter(url=url).exists():
                # already taken care of
                return set_bookshop(ebook)

            # a new ebook
            format = loader.type_for_url(url)
            if format in ('pdf', 'epub', 'html', 'online'):
                new_ebook = models.Ebook()
                new_ebook.format = format
                new_ebook.url = url
                new_ebook.rights = ebook.rights
                new_ebook.edition = ebook.edition
                new_ebook.set_provider()
                if format == "online":
                    new_ebook.active = False
                new_ebook.save()
                set_bookshop(ebook)
                if format in DOWNLOADABLE:
                    return make_dl_ebook(url, ebook)
    return None, 0 

GUID = re.compile(r'FBInit\.GUID = \"([0-9a-z]+)\"')
LIBROSID = re.compile(r'(\d+)$')
LIBROSROOT = 'https://libros.uchile.cl/files/presses/1/monographs/%s/submission/proof/'
LIBROSINDEX = LIBROSROOT + 'index.html'
LIBROSJSON = LIBROSROOT + 'files/assets/html/workspace.js?uni=%s'
LIBRODPDF = LIBROSROOT + 'files/assets/common/downloads/%s?uni=%s'

def harvest_libroschile(ebook):
    booknum = LIBROSID.search(ebook.url).group(1)
    if not booknum:
        return None, 0
    viewurl = LIBROSINDEX % booknum
    doc = get_soup(viewurl)
    if not doc:
        return None, 0
    hit = doc.find(string=GUID)
    if not hit:
        return None, 0
    guid = GUID.search(hit)
    if not guid:
        return None, 0
    jsonurl = LIBROSJSON % (booknum, guid)
    try:
        json =  requests.get(jsonurl).json()
    except:
        return None, 0
    if not json:
        return None, 0
    filename = json.get('downloads',{}).get('url', None)
    if not filename:
        return None, 0
    pdfurl =  LIBRODPDF % (booknum, filename, guid)
    return make_dl_ebook(pdfurl, ebook) 


def harvest_ipsflab(ebook):    
    def selector(doc):
        return doc.find_all('a', href=re.compile(r'/system/files/ispf_lab/quaderni/.*\.(pdf|epub)'))
    return harvest_multiple_generic(ebook, selector)


def harvest_figshare(ebook):    
    def selector(doc):
        return doc.find('a', href=re.compile(r'/ndownloader/'))
    return harvest_one_generic(ebook, selector)


def harvest_fupress(ebook):    
    def selector(doc):
        return doc.select_one('#ctl00_contenuto_pdf a.btn-open[href]')
    if 'isbn' in ebook.url:
        set_bookshop(ebook)
        return None, 0
    return harvest_one_generic(ebook, selector)

def harvest_funlam(ebook):    
    if '/modules/' in ebook.url:
        set_bookshop(ebook)
        return None, 0
    return make_dl_ebook(ebook.url, ebook)


def harvest_dunckerhumblot(ebook):    
    def selector(doc):
        return doc.select_one('div.section__buttons a[href$="download"]')
    return harvest_one_generic(ebook, selector)


def harvest_cornellopen(ebook): 
    def selector(doc):
        return doc.select('div.sp-product__buy-btn-container li a[href]')
    return harvest_multiple_generic(ebook, selector)

def harvest_editorialbonaventuriana(ebook):
    def selector(doc):
        return doc.select_one('div.djc_fulltext p a[href$=".pdf"]')
    return harvest_one_generic(ebook, selector)


def harvest_esv(ebook):
    doc = get_soup(ebook.url.replace('details', 'download'))
    if doc:
        obj = doc.select_one('div.content-box a[href$=".pdf"]')
        if obj:
            return make_dl_ebook(obj['href'], ebook)
        else:
            logger.warning('couldn\'t get link for %s', ebook.url)
    else:
        logger.warning('couldn\'t get soup for %s', ebook.url)
    return None, 0

def harvest_fulcrum(ebook):    
    def selector(doc):
        return doc.select('ul.monograph-catalog-rep-downloads a[href]')
    return harvest_multiple_generic(ebook, selector)

def harvest_ubiquity(ebook):    
    def selector(doc):
        return doc.find_all('a', attrs={'data-category': re.compile('(epub|pdf) download')})
    return harvest_multiple_generic(ebook, selector)

def harvest_orkana(ebook):    
    def selector(doc):
        for obj in doc.find_all('p', string=re.compile(r'\((PDF|E-BOK)\)')):
            div = obj.find_parent('div')
            if div and div.find_next_sibling('div') and div.find_next_sibling('div').find('a'):
                yield div.find_next_sibling('div').find('a')
    return harvest_multiple_generic(ebook, selector)

def harvest_euna(ebook):
    if '/view/' in ebook.url:
        return make_dl_ebook(ebook.url.replace('view', 'download'), ebook)
    set_bookshop(ebook)
    return None, 0

def harvest_orl(ebook):
    if ebook.url.startswith('https://openresearchlibrary.org/viewer/'):
        orl_id = ebook.url[39:]
        return make_dl_ebook(
            f'https://openresearchlibrary.org/ext/api/media/{orl_id}/assets/external_content.pdf',
            ebook)
    return None, 0

def harvest_pressesagro(ebook):
    def selector(doc):
        return doc.select_one('#sidebar ul li span a[href]')
    return harvest_one_generic(ebook, selector)

def harvest_buponline(ebook):
    def selector(doc):
        return doc.find('a', string=DOWNLOAD)
    return harvest_one_generic(ebook, selector)

INTECH = re.compile(r'\.intechopen\.com/books/(\d+)$')
def harvest_intech(ebook):
    booknum = INTECH.search(ebook.url)
    if booknum:
        url = (f'https://mts.intechopen.com/storage/books/{booknum.group(1)}/authors_book/authors_book.pdf')
        return make_dl_ebook(url,  ebook)
    return None, 0

def harvest_usmcu(ebook):
    def selector(doc):
        return doc.find('a', string='PDF download')
    return harvest_one_generic(ebook, selector)

def harvest_upv(ebook):
    def selector(doc):
        return doc.select_one('a.descargar[href]')
    return harvest_one_generic(ebook, selector)

def harvest_una_editions(ebook):
    doc = get_soup(ebook.url)
    if doc:
        obj = doc.find('a', class_='jet-listing-dynamic-link__link', href=True, string='PDF')
        if obj:
            return make_dl_ebook(obj['href'], ebook)
        else:
            logger.warning('couldn\'t get link for %s', ebook.url)
    else:
        logger.warning('couldn\'t get soup for %s', ebook.url)
    return None, 0

def harvest_cambridge(ebook):
    ebook, status = redirect_ebook(ebook)
    doc = get_soup(ebook.url)
    if doc:
        obj = doc.find('a', string=re.compile('Full book PDF'))
        if obj and obj['href']:
            dl_url = urljoin(ebook.url, obj['href'])
            return make_dl_ebook(dl_url, ebook)
        obj = doc.find('meta', attrs={"name": re.compile("citation_pdf_url")})
        if obj and obj['content']:
            dl_url = obj['content']
            return make_dl_ebook(dl_url, ebook)
        pdflinks = []
        for obj in doc.select('a[data-pdf-content-id]'):
            if obj and obj['href']:
                chap = urljoin(ebook.url, obj['href'])
            pdflinks.append(chap)
        stapled = None
        if pdflinks:
            stapled = make_stapled_ebook(pdflinks, ebook)
        if stapled:
            return stapled
        else:
            logger.warning('couldn\'t staple %s', pdflinks)
    else:
        logger.warning('couldn\'t get soup for %s', ebook.url)
    return None, 0

def harvest_exon(ebook):
    doc = get_soup(ebook.url)
    if doc:
        pdflinks = []
        for obj in doc.select('a.galley-link.pdf[href]'):
            if obj and obj['href']:
                chap = obj['href'].replace('/view/', '/download/')
            pdflinks.append(chap)
        stapled = None
        if pdflinks:
            stapled = make_stapled_ebook(pdflinks, ebook)
        if stapled:
            return stapled
        else:
            logger.warning('couldn\'t staple %s', pdflinks)
    else:
        logger.warning('couldn\'t get soup for %s', ebook.url)
    return None, 0

def harvest_una(ebook):
    def selector(doc):
        return doc.select_one('#header-primary-action a[href]')
    return harvest_one_generic(ebook, selector)

def harvest_wbg(ebook):
    ''' most of these are archived under files.wbg-wissenverbindet.de '''
    doc = get_soup(ebook.url)
    if doc:
        sku_obj = doc.select_one('span[itemprop=sku]')
        sku = sku_obj.text.strip() if sku_obj else None
        if sku:
            url = f'https://files.wbg-wissenverbindet.de/Files/Article/ARTK_ZOA_{sku}_0001.pdf'
            return make_dl_ebook(url,  ebook)
    return None, 0

def harvest_kb(ebook):
    def selector(doc):
        return doc.select_one('a[title=fulltext][href]')
    return harvest_one_generic(ebook, selector)

def harvest_istanbul(ebook):
    def cdn_url(soup):
        objs = soup.find_all('a', href=re.compile(r'cdn\.istanbul'))
        for obj in objs:
            yield obj['href']
    def pdf_urls(ebook):
        doc = get_soup(ebook.url, user_agent=settings.GOOGLEBOT_UA, follow_redirects=True)
        if doc:
            for content_url in cdn_url(doc):
                yield content_url
            for obj in doc.select('div.post-content h5 a.from-journal[href]'):
                chap_url = urljoin(ebook.url, obj['href'])
                chap_doc = get_soup(chap_url, user_agent=settings.GOOGLEBOT_UA, follow_redirects=True)
                if chap_doc:
                    for content_url in cdn_url(chap_doc):
                        yield content_url
        
    # staple the chapters
    stapled = make_stapled_ebook(pdf_urls(ebook), ebook, user_agent=settings.GOOGLEBOT_UA)
    if stapled:
        return stapled
    else:
        logger.warning('couldn\'t make ebook file for %s', ebook.url)
    return None, 0

def harvest_gta(ebook):
    # https://verlag.gta.arch.ethz.ch/en/gta:book_978-3-85676-393-0
    pos = ebook.url.find('_')
    if pos < 1:
        return None, 0
    isbn = ebook.url[pos + 1:]
    api_host = 'https://api.verlag.gta.arch.ethz.ch'
    json_url = f'{api_host}/api/v1/graphs/gta/data/gtaapi:PublicRetrieveBook/gta:book_{isbn}/'
    r = requests.get(json_url)
    if r.status_code == 200:
        try:
            file_url = None
            graph = r.json()['@graph']           
            for obj in graph:
                if "gtaapi:file_url" in obj:
                    file_url = obj["gtaapi:file_url"]
                    break
            if file_url:  
                return make_dl_ebook(file_url, ebook)
        except IndexError:
            logger.error('no item_file for %s', ebook.url)
    return None, 0

def harvest_manu(ebook):
    def chap_selector(doc):
        return doc.select('div.content-box-body div.book-toc a.c-Button--link[href*="/display/"]')
    def dl(url):
        return url.replace('/display/', '/downloadpdf/').replace('.xml', '.pdf')
    doc = get_soup(ebook.url, follow_redirects=True, user_agent=settings.CHROME_UA)
    if doc:
        obj = doc.find('a', string=re.compile(r"Open Access"))
        if not obj or 'href' not in obj.attrs:
            return None, 0
        ebook.url = urljoin(ebook.url, obj['href'])
        return harvest_stapled_generic(ebook, lambda x: None, chap_selector, 
                            user_agent=settings.CHROME_UA, dl=dl)
    return None, 0

def harvest_sciendo(ebook):    
    def selector(doc):
        json_obj = doc.find('script', id='__NEXT_DATA__')
        if json_obj:
            try:
                json_data = json.loads(json_obj.string)
                pdf_url = json_data['props']['pageProps']['product']['pdfLink']
                epub_url = json_data['props']['pageProps']['product']['epubLink']
                if pdf_url or epub_url:
                    if pdf_url:
                        yield {'href': pdf_url}
                    if epub_url:
                        yield {'href': epub_url}
            except json.JSONDecodeError as je:
                logger.error(f'Bad json {je.msg}')
            except KeyError as ke:
                logger.error('No links in json for {ebook.url}')
    return harvest_multiple_generic(ebook, selector)
