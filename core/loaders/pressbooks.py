import re
from regluit.core.validation import identifier_cleaner
from . import BaseScraper

class PressbooksScraper(BaseScraper):
    can_scrape_hosts = [
        'bookkernel.com', 'milnepublishing.geneseo.edu', 'press.rebus.community', 'pb.unizin.org', 
        'opentext.wsu.edu', 'oer.missouriwestern.edu', 'eskript.ethz.ch', 'opentext.lib.vt.edu',
        'opentextbc.ca',
    ]
    can_scrape_strings = ['pressbooks']

    def get_downloads(self):
        for dl_type in ['epub', 'mobi', 'pdf']:
            download_el = self.doc.select_one('.{}'.format(dl_type))
            value = None
            if download_el and download_el.find_parent():
                value = download_el.find_parent().get('href')
            else:
                a = self.doc.find('a', href=re.compile(r'{}$'.format(dl_type)))
                value = a.get('href') if a else None
            if value:
                self.set('download_url_{}'.format(dl_type), value)

    def get_publisher(self):
        value = self.get_dt_dd('Publisher')
        if not value:
            value = self.doc.select_one('.cie-name')
            value = value.text if value else None
        if value:
            self.set('publisher', value)
        else:
            value = self.check_metas(['citation_publisher', 'publisher', r'DC\.Source'])
            if value:
                self.set('publisher', value)
                
    def get_title(self):
        value = self.doc.select_one('.entry-title a[title]')
        value = value['title'] if value else None
        if value:
            self.set('title', value)
        else:
            super(PressbooksScraper, self).get_title()

    def get_isbns(self):
        '''add isbn identifiers and return a dict of edition keys and ISBNs'''
        isbns = {}
        for (key, label) in [('electronic', 'Ebook ISBN'), ('paper', 'Print ISBN')]:
            isbn = identifier_cleaner('isbn', quiet=True)(self.get_dt_dd(label))
            if isbn:
                self.identifiers['isbn_{}'.format(key)] = isbn
                isbns[key] = isbn
        return isbns
