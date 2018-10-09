from django.conf import settings

from .multiscrape import BaseMultiScraper




class KUMultiScraper(BaseMultiScraper):

    @classmethod
    def divider(cls, doc):
        return doc.select('submission')
    
    @classmethod
    def login(cls):
        s = requests.Session()
        credentials = {'email': settings.KU_EMAIL, 'password': settings.KU_PASSWORD}
        r = s.get('https://app.knowledgeunlatched.org/login')
        r = s.post('https://app.knowledgeunlatched.org/auth/login', json=credentials)
        return s

    can_scrape_hosts = ['app.knowledgeunlatched.org']

    def get_genre(self):
        value = self.check_metas([r'dc\.type', 'og:type'])
        if value and value in ('Text.Book', 'book'):
            self.set('genre', 'book')

    def get_title(self):
        value = self.check_metas([r'dc\.title', 'citation_title', 'og:title', 'title'])
        if not value:
            value =  self.fetch_one_el_content('title')
        self.set('title', value)

    def get_language(self):
        value = self.check_metas([r'dc\.language', 'language', 'inLanguage'])
        self.set('language', value)

    def get_description(self):
        value = self.check_metas([
            r'dc\.description',
            'og:description',
            'description'
        ])
        self.set('description',  value)

    def get_isbns(self):
        '''return a dict of edition keys and ISBNs'''
        isbns = {}
        isbn_cleaner = identifier_cleaner('isbn', quiet=True)
        label_map = {'epub': 'EPUB', 'mobi': 'Mobi',
            'paper': 'Paperback', 'pdf':'PDF', 'hard':'Hardback'}
        for key in label_map.keys():
            isbn_key = 'isbn_{}'.format(key)
            value = self.check_metas(['citation_isbn'], type=label_map[key])
            value = isbn_cleaner(value)
            if value:
                isbns[isbn_key] = value
                self.identifiers[isbn_key] = value
        if not isbns:
            values = self.check_metas(['book:isbn', 'books:isbn'], list_mode='list')
            values = values if values else self.get_itemprop('isbn')
            if values:
                value = isbn_cleaner(values[0])
                isbns = {'':value} if value else {}
        return isbns

    def get_identifiers(self):
        value = self.doc.identifier.text
        if not value:
            value = self.doc.select_one('link[rel=canonical]')
            value = value['href'] if value else None
        value = identifier_cleaner('http', quiet=True)(value)
        if value:
            self.identifiers['http'] = value
        value = self.check_metas([r'DC\.Identifier\.DOI', 'citation_doi'])
        value = identifier_cleaner('doi', quiet=True)(value)
        if value:
            self.identifiers['doi'] = value

        #look for oclc numbers
        links = self.doc.find_all(href=CONTAINS_OCLCNUM)
        for link in links:
            oclcmatch = CONTAINS_OCLCNUM.search(link['href'])
            if oclcmatch:
                value = identifier_cleaner('oclc', quiet=True)(oclcmatch.group(1))
                if value:
                    self.identifiers['oclc'] = value
                    break

        isbns = self.get_isbns()
        ed_list = []
        if len(isbns):
            #need to create edition list
            for key in isbns.keys():
                isbn_type = key.split('_')[-1]
                ed_list.append({
                    'edition_note': isbn_type,
                    'edition_identifiers': {'isbn': isbns[key]}
                })
        else:
            value = self.check_metas(['citation_isbn'], list_mode='list')
            if len(value):
                for isbn in value:
                    isbn = identifier_cleaner('isbn', quiet=True)(isbn)
                    if isbn:
                        ed_list.append({
                            '_edition': isbn,
                            'edition_identifiers': {'isbn':isbn}
                        })
        if len(ed_list):
            self.set('edition_list', ed_list)

    def get_keywords(self):
        value = self.check_metas(['keywords']).strip(',;')
        if value:
            subjects = []
            for subject in re.split(' *[;,] *', value):
                if valid_subject(subject):
                    subjects.append(subject)
            self.set('subjects', subjects)

    def get_publisher(self):
        value = self.check_metas(['citation_publisher', r'DC\.Source'])
        if value:
            self.set('publisher', value)

    def get_pubdate(self):
        value = self.get_itemprop('datePublished', list_mode='one_item')
        if not value:
            value = self.check_metas([
                'citation_publication_date', 'copyrightYear', r'DC\.Date\.issued', 'datePublished',
                'books:release_date', 'book:release_date', 
            ])
        if value:
            value = validate_date(value)
            if value:
                self.set('publication_date', value)

    def get_author_list(self):
        value_list = self.get_itemprop('author')
        if not value_list:
            value_list = self.check_metas([
                r'DC\.Creator\.PersonalName',
                'citation_author',
                'author',
            ], list_mode='list')
            if not value_list:
                return []
        return value_list

    def get_role(self):
        return 'author'

    def get_authors(self):
        role = self.get_role()
        value_list = self.get_author_list()
        creator_list = []
        value_list = authlist_cleaner(value_list)
        if len(value_list) == 0:
            return
        if len(value_list) == 1:
            self.set('creator',  {role: {'agent_name': value_list[0]}})
            return
        for auth in value_list:
             creator_list.append({'agent_name': auth})

        self.set('creator', {'{}s'.format(role): creator_list })

    def get_cover(self):
        image_url = self.check_metas(['og:image', 'image', 'twitter:image'])
        if not image_url:
            block = self.doc.find(class_=CONTAINS_COVER)
            block = block if block else self.doc
            img = block.find_all('img', src=CONTAINS_COVER)
            if img:
                image_url = img[0].get('src', None)
        if image_url:
            if not image_url.startswith('http'):
                image_url = urljoin(self.base, image_url)
            self.set('covers', [{'image_url': image_url}])

    def get_downloads(self):
        for dl_type in ['epub', 'mobi', 'pdf']:
            dl_meta = 'citation_{}_url'.format(dl_type)
            value = self.check_metas([dl_meta])
            if value:
                self.set('download_url_{}'.format(dl_type), value)

    def get_license(self):
        '''only looks for cc licenses'''
        links = self.doc.find_all(href=CONTAINS_CC)
        for link in links:
            self.set('rights_url', link['href'])


