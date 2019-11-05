import logging
import requests
from bs4 import BeautifulSoup

from django.conf import settings

from gitenberg.metadata.pandata import Pandata

from regluit.core.bookloader import add_from_bookdatas, BasePandataLoader
from .scrape import BaseScraper
from .hathitrust import HathitrustScraper
from .pressbooks import PressbooksScraper
from .routledge import RoutledgeScraper
from .springer import SpringerScraper
from .smashwords import SmashwordsScraper
from .ubiquity import UbiquityScraper

logger = logging.getLogger(__name__)

def get_scraper(url):
    scrapers = [
        PressbooksScraper,
        SpringerScraper,
        UbiquityScraper,
        SmashwordsScraper,
        HathitrustScraper,
        RoutledgeScraper,
        BaseScraper,
    ]
    for scraper in scrapers:
        if scraper.can_scrape(url):
            return scraper(url)
            
def scrape_sitemap(url, maxnum=None):
    try:
        response = requests.get(url, headers={"User-Agent": settings.USER_AGENT})
        doc = BeautifulSoup(response.content, 'lxml')
        for page in doc.find_all('loc')[0:maxnum]:
            scraper = get_scraper(page.text)
            if scraper.metadata.get('genre', None) == 'book':
                yield scraper
    except requests.exceptions.RequestException as e:
        logger.error(e)

def add_by_webpage(url, work=None, user=None):
    edition = None
    scraper = get_scraper(url)
    loader = BasePandataLoader(url)
    pandata = Pandata()
    pandata.metadata = scraper.metadata
    for metadata in pandata.get_edition_list():
        edition = loader.load_from_pandata(metadata, work)
        work = edition.work
    loader.load_ebooks(pandata, edition, user=user)
    return edition if edition else None

        
def add_by_sitemap(url, maxnum=None):
    return add_from_bookdatas(scrape_sitemap(url, maxnum=maxnum))
    
def scrape_language(url):
    scraper = get_scraper(url)
    language = scraper.metadata.get('language')
    return language if language else 'xx'


