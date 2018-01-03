import re
from urlparse import urljoin
from regluit.core.loaders.scrape import BaseScraper

SWCAT = re.compile(r'^https://www\.smashwords\.com/books/category.*')
class SmashwordsScraper(BaseScraper):
    can_scrape_strings =['smashwords.com']
    
    def get_keywords(self):
        kws = self.doc.find_all('a', href=SWCAT)
        value = list(set(kw.string.strip() for kw in kws))
        if value:
            self.set('subjects', value)

    def get_description(self):
        desc = self.doc.select_one('#longDescription')
        if desc:
            value = desc.get_text() if hasattr(desc, 'get_text') else desc.string
            if value.strip():
                self.set('description', value.strip())
    
    def get_downloads(self):
        dldiv =  self.doc.select_one('#download')
        if dldiv:
            for dl_type in ['epub', 'mobi', 'pdf']:
                dl_link = dldiv.find('a', href=re.compile(r'.*\.{}'.format(dl_type)))
                if dl_link:
                    url = urljoin(self.base,dl_link['href'])
                    self.set('download_url_{}'.format(dl_type), url)
    def get_publisher(self):
        self.set('publisher', 'Smashwords')

