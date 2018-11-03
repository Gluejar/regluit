import requests
from django.conf import settings

from regluit.core.validation import (
    authlist_cleaner,
    identifier_cleaner,
    valid_subject,
    validate_date,
)
from regluit.core.bookloader import add_from_bookdatas

from .multiscrape import BaseMultiScraper, multiscrape
from .utils import ids_from_urls

class KUMultiScraper(BaseMultiScraper):
    parser_name = 'xml'
    can_scrape_hosts = ['app.knowledgeunlatched.org']

    @classmethod
    def divider(cls, doc):
        return doc.find_all('Submission')

    @classmethod
    def get_response(cls, url):
        return cls.login().get(url)

    @classmethod
    def login(cls):
        s = requests.Session()
        credentials = {'email': settings.KU_EMAIL, 'password': settings.KU_PASSWORD}
        r = s.get('https://app.knowledgeunlatched.org/login')
        r = s.post('https://app.knowledgeunlatched.org/auth/login', json=credentials)
        return s

    def get_license(self):
        val = self.fetch_one_el_content('LicenseURL')
        if val:
            self.set('rights_url', val)

    def get_title(self):
        val = self.fetch_one_el_content('Title')
        if val:
            self.set('title', val)

    def get_description(self):
        val = self.fetch_one_el_content('Description')
        coll = self.doc.select_one('Funder ProgramName')
        coll = u"<br>This book is made open access as part of the Knowledge Unlatched {}".format(coll.text) if coll else ''
        if val:
            self.set('description', val + coll)

    def get_genre(self):
        val = self.fetch_one_el_content('Type')
        if val:
            self.set('genre', val)

    def get_language(self):
        val = self.fetch_one_el_content('Language')
        if val:
            self.set('language', val)

    def get_keywords(self):
        subjects = [self.fetch_one_el_content('PrimarySubject')]
        for subject in self.doc.find_all('ManualSubject'):
            subjects.append(subject.text)
        bisac = self.fetch_one_el_content('BISAC')
        if bisac:
            subjects.append(u'!bisac {}'.format(bisac))
        subjects.append('KUnlatched')
        self.set('subjects', subjects)

    def get_publisher(self):
        val = self.fetch_one_el_content('PublisherName')
        if val:
            self.set('publisher', val)

    def get_cover(self):
        image_url = self.fetch_one_el_content('Cover')
        if image_url:
            self.set('covers', [{'image_url': image_url}])

    def get_pubdate(self):
        value = self.fetch_one_el_content('PublicationDate')
        if value:
            value = validate_date(value)
            if value:
                self.set('publication_date', value)

    def get_authors(self):
        def fullname(auth):
            firstname = auth.FirstName.text
            lastname = auth.FirstName.text
            return u'{} {}'.format(firstname, lastname)
        authors = self.doc.find_all('Author')
        creator_list = []
        role = 'author'
        for author in authors:
            creator_list.append({'agent_name': fullname(author)})
            role = author.Role.text
        self.set('creator', {'{}s'.format(role): creator_list })

    def get_downloads(self):
        fts = ['pdf', 'epub', 'mobi']
        dls = self.doc.find_all('Document')
        for dl in dls:
            dlft = dl.Type.text
            url = dl.Path.text
            for ft in fts:
                if ft in dlft:
                    dlft = ft
                    break
            if url:
                self.set('download_url_{}'.format(dlft), url)

    def get_isbns(self):
        isbn_cleaner = identifier_cleaner('isbn', quiet=True)
        isbns = {}
        isbn = isbn_cleaner(self.fetch_one_el_content('IsbnHardback'))
        if isbn:
            isbns['isbn_hard'] = isbn
        isbn = isbn_cleaner(self.fetch_one_el_content('IsbnPaperback'))
        if isbn:
            isbns['isbn_paper'] = isbn
        isbn = isbn_cleaner(self.fetch_one_el_content('IsbnEpdf'))
        if isbn:
            isbns['isbn_pdf'] = isbn
        isbn = isbn_cleaner(self.fetch_one_el_content('IsbnEpub'))
        if isbn:
            isbns['isbn_epub'] = isbn
        return isbns

    def get_identifiers(self):
        doi_cleaner = identifier_cleaner('doi', quiet=True)
        super(KUMultiScraper, self).get_identifiers()
        url = self.fetch_one_el_content('Doi')
        if url:
            doi = doi_cleaner(url)
            if doi:
                self.identifiers['doi'] = doi
        url = self.fetch_one_el_content('OAPENURL')
        if url:
            oapn = ids_from_urls(url).get('oapn', None)
            if oapn:
                self.identifiers['oapn'] = oapn

ku_rounds = [8, 33, 1, 2, 4, 3, 5, 31, 6, 42, 26, 27]

def load_ku(ku_round=None):
    rounds = [ku_round] if ku_round else ku_rounds
    editions = []
    for around in rounds:
        ku_url = 'https://app.knowledgeunlatched.org/api/rounds/{}/submissions.xml'.format(around)
        scrapers = multiscrape(ku_url, scraper_class=KUMultiScraper)
        editions.extend(add_from_bookdatas(scrapers))
    return editions

