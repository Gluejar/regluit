import re

import requests
from RISparser import read as readris

from django.conf import settings

from regluit.core.validation import identifier_cleaner

from .scrape import BaseScraper


class HathitrustScraper(BaseScraper):

    can_scrape_hosts = ['hathitrust.org']
    can_scrape_strings = ['hdl.handle.net/2027/']
    CATALOG = re.compile(r'catalog.hathitrust.org/Record/(\d+)')

    def setup(self):
        catalog_a = self.doc.find('a', href=self.CATALOG)
        if catalog_a:
            catalog_num = self.CATALOG.search(catalog_a['href']).group(1)
            ris_url = 'https://catalog.hathitrust.org/Search/SearchExport?handpicked={}&method=ris'.format(catalog_num)
            response = requests.get(ris_url, headers={"User-Agent": settings.USER_AGENT})
            records = readris(response.text.splitlines()) if response.status_code == 200 else []
            for record in records:
                self.record = record
                return
            self.record = None # probably a hdl not pointing at Hathitrust
        self.record = None

    def get_downloads(self):
        if self.record:
            dl_a = self.doc.select_one('#fullPdfLink')
            value = dl_a['href'] if dl_a else None
            if value:
                self.set(
                    'download_url_{}'.format('pdf'),
                    'https://babel.hathitrust.org{}'.format(value)
                )
        return super(HathitrustScraper, self).get_downloads()

    def get_isbns(self):
        if self.record:
            isbn = self.record.get('issn', [])
            value = identifier_cleaner('isbn', quiet=True)(isbn)
            return {'print': value} if value else {}
        return super(HathitrustScraper, self).get_isbns()

    def get_title(self):
        if self.record:
            self.set('title', self.record.get('title', ''))
        return super(HathitrustScraper, self).get_title()

    def get_keywords(self):
        if self.record:
            self.set('subjects', self.record.get('keywords', []))
        return super(HathitrustScraper, self).get_keywords()

    def get_publisher(self):
        if self.record:
            self.set('publisher', self.record.get('publisher', ''))
        return super(HathitrustScraper, self).get_publisher()

    def get_pubdate(self):
        if self.record:
            self.set('publication_date', self.record.get('year', ''))
        return super(HathitrustScraper, self).get_pubdate()

    def get_description(self):
        if self.record:
            notes = self.record.get('notes', [])
            self.set('description', '\r'.join(notes))
        return super(HathitrustScraper, self).get_description()

    def get_genre(self):
        if self.record:
            self.set('genre', self.record.get('type_of_reference', '').lower())
        return super(HathitrustScraper, self).get_genre()
