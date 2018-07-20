import re
from urlparse import urlparse

from regluit.utils.lang import get_language_code
from . import BaseScraper


HAS_EDS = re.compile(r'\(eds?\.\)')
UBIQUITY_HOSTS = ["ubiquitypress.com", "kriterium.se", "oa.finlit.fi", "humanities-map.net",
    "oa.psupress.org", "larcommons.net", "uwestminsterpress.co.uk", "stockholmuniversitypress.se",
    "luminosoa.org", "iitikship.iiti.ac.in", "aperio.press", "press.lse.ac.uk", "press.sjms.nu", 
    "trystingtree.library.oregonstate.edu", "publishing.vt.edu", "universitypress.whiterose.ac.uk",
    "www.winchesteruniversitypress.org",
]

class UbiquityScraper(BaseScraper):
    can_scrape_hosts = UBIQUITY_HOSTS
    def get_role(self):
        descs = self.doc.select('section.book-description')
        for desc in descs:
            if desc.find(string=HAS_EDS):
                return 'editor'
        return super(UbiquityScraper, self).get_role()

    def get_language(self):
        langlabel = self.doc.find(string='Language')
        lang = langlabel.parent.parent.find_next_sibling() if langlabel else ''
        lang = lang.get_text() if lang else ''
        lang = get_language_code(lang) if lang else ''
        if lang:
            self.set('language', lang)
        else:
            super(UbiquityScraper, self).get_language()
