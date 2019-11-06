from __future__ import print_function
import re
import requests
from bs4 import BeautifulSoup
from django.conf import settings

from regluit.core.bookloader import add_from_bookdatas

from .scrape import BaseScraper

isbnmatch = re.compile(r'\d{13}')
readbook = re.compile('Read Book')

class RoutledgeScraper(BaseScraper):
    can_scrape_hosts = ['www.routledge.com']
    
    def get_keywords(self):
        subjects = []
        for sub in self.doc.select('dl.dl-codes dt'):
            subjects.append('!bisacsh ' + sub.string)
        self.set('subjects', subjects)

    def get_author_list(self):
        value_list = []
        for auth in self.doc.select('h4.media-author a'):
            value_list.append(auth.string)
        return value_list

    def get_role(self):
        return 'editor' if self.doc.find(string="Edited by ") else 'author'
    
    def get_isbns(self):
        '''return a dict of edition keys and ISBNs'''
        def get_isbn(url):
            match = isbnmatch.search(url)
            if match:
                return match.group(0)
            
        def get_eisbn(eurl):
            response = requests.get(eurl, allow_redirects=False)
            if response.status_code in (301, 302):
                eurl = response.headers['Location']
            return get_isbn(eurl)

        isbns = super(RoutledgeScraper, self).get_isbns()
        readbookstr = self.doc.find(string=readbook)
        if readbookstr:
            eurl = readbookstr.find_parent()['href']
            eisbn = get_eisbn(eurl)
            if eisbn:
                isbns['ebook'] = eisbn
        return isbns

    def get_description(self):
        value = self.get_itemprop('description', list_mode='one_item')
        if not value:
            value = self.check_metas([
                r'dc\.description',
                'og:description',
                'description'
            ])
        self.set('description',  value)

    def get_publisher(self):
        self.set('publisher', "Routledge")

    def get_title(self):
        value = self.check_metas([r'dc\.title', 'citation_title', 'og:title', 'title'])
        if not value:
            value =  self.fetch_one_el_content('title')
        to_delete = ["(Open Access)", "(Hardback)", "- Routledge"]
        for text in to_delete:
            value = value.replace(text, "")
        self.set('title', value)


def load_routledge():
    search_url = "https://www.routledge.com/collections/11526"

    def get_collections(url):
        try:
            response = requests.get(url, headers={"User-Agent": settings.USER_AGENT})
            if response.status_code == 200:
                doc = BeautifulSoup(response.content, 'lxml')
                for link in doc.find_all('a', href=re.compile('collections/11526/')):
                    yield (link.text, "https://www.routledge.com/" + link['href'])
        except requests.exceptions.ConnectionError:
            print('couldn\'t connect to %s' % search_url)

    def get_coll_books(url):
        try:
            response = requests.get(url, headers={"User-Agent": settings.USER_AGENT})
            if response.status_code == 200:
                doc = BeautifulSoup(response.content, 'lxml')
                for link in doc.select('.media-title a'):
                    yield link['href']
        except requests.exceptions.ConnectionError:
            print('couldn\'t connect to %s' % url)
    
    books = {}
    for (subject, coll_url) in get_collections(search_url):
        print(subject)
        for book_url in get_coll_books(coll_url):
            if not book_url in books:
                print(book_url)
                new_book = RoutledgeScraper(book_url)
                new_book.metadata['subjects'].append(subject)
                books[book_url] = new_book
            else:
                books[book_url].metadata['subjects'].append(subject)
    print("Harvesting %s books" % len(books.values()))
    add_from_bookdatas(books.values())
    return books
    