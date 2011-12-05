import requests
import urllib
import httplib
import json
from pprint import pprint
from itertools import islice, izip, repeat
import logging



import sys, os

# a kludge to allow for isbn.py to be imported 
# and not just in the context of the regluit Django app

try:
    from regluit.core import isbn
except:
    import isbn

try:
    import unittest
    from unittest import TestCase    
except:
    from django.test import TestCase
    from django.utils import unittest


import re

import freebase

import logging
logger = logging.getLogger(__name__)

MASHUPBOOK_ISBN_13 = '9781590598580'
MASHUPBOOK_ISBN_10 = '159059858X'
MASHUPBOOK_OLID = 'OL13439114M'
RY_OLID = 'OL4264806A'

SURFACING_WORK_OLID = 'OL675829W'
SURFACING_EDITION_OLID = 'OL8075248M'

# http://stackoverflow.com/questions/2348317/how-to-write-a-pager-for-python-iterators/2350904#2350904        
def grouper(iterable, page_size):
    page= []
    for item in iterable:
        page.append( item )
        if len(page) == page_size:
            yield page
            page= []
    yield page

class FreebaseException(Exception):
    pass

class OpenLibraryException(Exception):
    pass

class HathiException(Exception):
    pass

def filter_none(d):
    d2 = {}
    for (k,v) in d.iteritems():
        if v is not None:
            d2[k] = v
    return d2

def to_list(s):
    """if input is not a list return a list with s"""
    if not isinstance(s,list):
        return [s]
    else:
        return s

def hathi_bib(id, id_type='isbn', detail_level='brief'):
    url = "http://catalog.hathitrust.org/api/volumes/brief/%s/%s.json"  % (id_type, id)
    r = requests.get(url)
    if r.status_code == httplib.OK:
        return r.content
    else:
        raise Exception("Hathi Bib API response: %s " % (httplib.responses[r.status_code]) )
        
# http://openlibrary.org/developers/api

class OpenLibrary(object):
    @classmethod
    def books(cls, id, id_type="isbn", format="json", callback=None, jscmd=None):
        # http://openlibrary.org/dev/docs/api/books
        # bibkeys: one of isbn, oclc, lccn, olid
        # format: one of json, javascript
        # jscmd: one of viewapi, data, details (deprecated in favor of data)
        base_url = "http://openlibrary.org/api/books"
        params = filter_none({'bibkeys':'%s:%s' % (id_type,id),
                              'format':format,
                              'callback':callback,
                              'jscmd':jscmd})
        
        r = requests.get(base_url,params=params)
        if r.status_code == httplib.OK:
            return json.loads(r.content)
        else:
            raise OpenLibraryException("OpenLibrary API response: %s " % (httplib.responses[r.status_code]) )
            
    @classmethod
    def covers(cls, id, id_type='isbn', size='S'):
        # http://openlibrary.org/dev/docs/api/covers
        # id_type: one of 'id' (internal cover ID), olid (Open Library ID), isbn, oclc, lccn, goodreads, librarything
        # size:  one of s, m, l
        # http://covers.openlibrary.org/b/$key/$value-$size.jpg

        if id_type.lower() not in ['id','isbn','oclc','lccn','goodreads','librarything']:
            raise OpenLibraryException("%s is an incorrect id_type for covers" % (id_type))
        if size.upper() not in ['S','M','L']:
            raise OpenLibraryException("%s is an incorrect size for covers" % (size))
    
        return "http://covers.openlibrary.org/b/%s/%s-%s.jpg" % (id_type.lower(),id,size.upper())
    
    @classmethod
    def author_photos(cls, olid, size='S'):
        #http://covers.openlibrary.org/a/$key/$value-$size.jpg
        if size.upper() not in ['S','M','L']:
            raise OpenLibraryException("%s is an incorrect size for author" % (size))
        return "http://covers.openlibrary.org/a/olid/%s-%s.jpg" % (olid,size.upper())
        
    @classmethod
    def read(cls, queries):
        # http://openlibrary.org/dev/docs/api/read -- most of its value to be used in browser JS?
        # can do single or multiple requests
        # example of a single request:
        # http://openlibrary.org/api/volumes/brief/isbn/0596156715.json
        
        # multiple
        # http://openlibrary.org/api/volumes/brief/json/id:1;lccn:50006784|olid:OL6179000M;lccn:55011330
        # the multiple format works, I think, for single requests
        #url = "http://openlibrary.org/api/volumes/brief/%s/%s.json" % (id_type, id)
        
        query_string = "|".join([ ";".join([ "%s:%s" % (id_type,id) for (id, id_type) in to_list(query)])
                         for query in to_list(queries)])
        if query_string:
            url = "http://openlibrary.org/api/volumes/brief/json/%s" % (query_string)
            r = requests.get(url)  
            if r.status_code == httplib.OK:
                return json.loads(r.content)
            else:
                raise OpenLibraryException("OpenLibrary API response: %s " % (httplib.responses[r.status_code]) )
        else:
            return None
    
    @classmethod
    def lists(cls):
        # http://openlibrary.org/dev/docs/api/lists
        raise NotImplementedError

    @classmethod
    def query_iter(cls,**kwargs):
        # use limit for page size and offset as the starting point
        kwargs2 = kwargs.copy()
        kwargs2.setdefault('offset', 0)
        
        more_items = True
        while more_items:
            items = cls.query(**kwargs2)
            for item in items:
                yield item
            if len(items):
                kwargs2['offset'] += len(items)
            else:
                more_items = False

    @classmethod
    def query(cls, **kwargs):
        # limit and offset are special
        base_url = "http://openlibrary.org/query.json"
        r = requests.get(base_url, params=kwargs)
        if r.status_code == httplib.OK:
            return json.loads(r.content)
        else:
            raise OpenLibraryException("OpenLibrary API response: %s " % (httplib.responses[r.status_code]) )

    @classmethod
    def editions(cls, work_olid):
        # http://openlibrary.org/query.json?type=/type/edition&works=/works/OL675829W&limit=5000
        for item in cls.query_iter(type='/type/edition',works='/works/%s'%(work_olid), limit=10):
            try:
                yield re.match(r'^/books/(.*)$',item['key']).group(1)
            except Exception, e:
                raise OpenLibraryException("problem in editions: %s " % e)
                
    @classmethod
    def works0(cls, id, id_type='isbn'):
        # http://openlibrary.org/api/volumes/brief/olid/OL8075248M.json
        # can there be more than 1 work for a given edition?
        # will return a list of works
        # there is a bug in OL in which we have workless editions
        response = cls.read((id,id_type))
        # resp['olid:OL8075248M']['records']['/books/OL8075248M']["details"]["details"]["works"][0]["key"]
        # resp.values()[0]['records'].values()[0]["details"]["details"]["works"][0]["key"]
        try:
            works_key = response.values()[0]['records'].values()[0]["details"]["details"]["works"]
            if (len(response.values()) == 1 and len(response.values()[0]['records'].values()) == 1):
                return [re.match(r'^/works/(.*)$',work_key["key"]).group(1) for work_key in works_key]
            else:
                raise OpenLibraryException("Assumption of 1 key in response invalid in OpenLibrary.works0")
        except Exception, e:
            return []
    @classmethod
    def works(cls, ids, page_size=10):
        """generalize to handle more than one set of id at a time -- ids is an iterable"""

        for (i, page) in enumerate(grouper(ids, page_size=page_size)):
            response = cls.read(page)
    
            for (id, id_type) in page:
                key = "{1}:{0}".format(id, id_type)
                val = response.get(key)
                if val is not None:
                    if (len(val['records'].values()) == 1):
                        try:
                            works_key = val['records'].values()[0]["details"]["details"]["works"]
                            yield [re.match(r'^/works/(.*)$',work_key["key"]).group(1) for work_key in works_key]
                        except Exception, e:
                            pass
                    else:
                        raise OpenLibraryException("Assumption of 1 key in response invalid in OpenLibrary.works")
                else:
                    yield []

class FreebaseBooks(object):
    def __init__(self, username=None, password=None, main_or_sandbox='main'):
        if main_or_sandbox == 'main':
            self.freebase = freebase
        else:
            self.freebase = freebase.sandbox
        if username is not None and password is not None:
            self.freebase.login(username,password)
    def books(self):
        MQL = u"""[{
  "type": "/book/book",
  "id":   null,
  "key": [{
    "namespace": "/wikipedia/en",
    "value":     null,
    "type":      "/type/key"
  }]
}]
""".replace("\n"," ")
        query = json.loads(MQL)
        resp = self.freebase.mqlreaditer(query)
        for r in resp:
            yield r

    def book_editions(self):
        MQL = u"""[{
  "type":        "/book/book_edition",
  "id":          null,
  "isbn":        [{}],
  "ISBN":        [{}],
  "LCCN":        [{}],
  "OCLC_number": [{}],
  "openlibrary_id": [{}],
  "book": {
    "id":   null,
    "name": null
  }
}]""".replace("\n"," ")
        query = json.loads(MQL)
        resp = self.freebase.mqlreaditer(query)
        for r in resp:
            yield r

    def editions_for_book(self, book_id):
        MQL = u"""[{
  "type":        "/book/book_edition",
  "id":          null,
  "isbn":        [{}],
  "ISBN":        [{}],
  "LCCN":        [{}],
  "OCLC_number": [{}],
  "openlibrary_id": [{}],
  "book": {
    "id":   null,
    "name": null
  }
}]""".replace("\n"," ")
        query = json.loads(MQL)
        query[0]["book"]["id"] = book_id
        resp = self.freebase.mqlreaditer(query)
        for r in resp:
            yield r
            
    def book_edition_by_id(self,id,id_type):
        MQL = u"""[{
  "type":        "/book/book_edition",
  "id":          null,
  "isbn":        [{}],
  "ISBN":        [{}],
  "LCCN":        [{}],
  "OCLC_number": [{}],
  "openlibrary_id": [{}],
  "book": {
    "id":   null,
    "name": null
  }
}]""".replace("\n"," ")
        query = json.loads(MQL)
        if id_type == 'isbn':
            query[0][id_type][0].setdefault('name', id)
        elif id_type in ['LCCN', 'OCLC_number', 'openlibrary_id']:
            query[0][id_type][0].setdefault('value', id)
            
        if id_type in ['isbn', 'LCCN', 'OCLC_number', 'openlibrary_id']:
            resp = self.freebase.mqlreaditer(query)
            for r in resp:
                yield r           
        else:
            raise FreebaseException('id_type must be one of ISBN, LCCN, OCLC_number or openlibrary_id, not %s' % (id_type))
    def xisbn(self, isbn_val=None, book_id=None):
        """ pass in either isbn_val or book_id and xisbn returns related ISBNs in Freebase.  Handles case in which
            either isbn or book_id is not None but not both
        """
        if isbn_val is None and book_id is None:
            raise Exception("One of isbn or book_id must be specified")
        elif isbn_val is not None and book_id is not None:
            raise Exception("Only only of isbn or book_id can be specified")
        elif isbn_val is not None:
            isbn_val = isbn.ISBN(isbn_val).to_string('13')
            MQL = """[{
  "type": "/book/book_edition",
  "isbn": {
    "name": null
  },
  "book": {
    "editions": [{
      "isbn": {
        "name": null
      }
    }]
  }
}]""".replace("\n"," ")
            query = json.loads(MQL)
            query[0]["book"]["editions"][0]["isbn"]["name"] = isbn_val
            resp = self.freebase.mqlreaditer(query)
            for r in resp:
                yield r["isbn"]["name"]             
        elif book_id is not None:
            for edition in self.editions_for_book(book_id=book_id):
                for i in edition["isbn"]:
                    yield i["name"]
        
            
class WorkMapper(object):
    @classmethod
    def freebase_book_to_openlibrary_work(cls, fb_id, complete_search=False):
        """ Try to map a Freebase ID by taking the ISBNs of associated editions and asking OpenLibrary for the work id"""
        print "fb_id: ", fb_id
        fb = FreebaseBooks()
        work_ids = set()
        # grab all ISBNs correponding to Freebase fb_id and comput the OpenLibrary work ID
        # if complete_search is False, stop at first work id
        for work_id_list in OpenLibrary.works(izip(fb.xisbn(book_id=fb_id), repeat('isbn'))):
            for work_id in work_id_list:
                if work_id not in work_ids:
                    work_ids.add(work_id)
                    yield work_id
                    if not complete_search:
                        raise StopIteration()    
            

def look_up_my_zotero_books_in_hathi():
    from regluit.experimental.zotero_books import MyZotero
    zot = MyZotero()
    for (i,b) in enumerate(zot.get_books(20)):
        try:
            print b, hathi_bib(b['isbn'])
        except Exception, e:
            print e

def ol_practice():
    print OpenLibrary.books(MASHUPBOOK_ISBN_10)
    pprint (OpenLibrary.books(MASHUPBOOK_ISBN_13, jscmd='data'))
    print OpenLibrary.books('0385472579', jscmd='data')
    print (OpenLibrary.covers(MASHUPBOOK_ISBN_10, size='M'))
    print (OpenLibrary.author_photos(RY_OLID,'S'))
    # can we status of a pd book oclc:03544699 The Log of a Cowboy - Andy Adams, 1903
    # http://openlibrary.org/books/OL7173600M/The_log_of_a_cowboy -- not working?
    print OpenLibrary.books('OL7173600M' 'olid', jscmd='data')
    # http://openlibrary.org/books/OL6542070M/The_Montessori_method works
    print OpenLibrary.books('1181252','oclc',jscmd='data')
    print OpenLibrary.read([(MASHUPBOOK_ISBN_10,'isbn'),('1181252','oclc')])
    # let's bring up the editions for Surfacing
    
    for (i,ed) in enumerate(islice(OpenLibrary.editions(SURFACING_WORK_OLID),100)):
        print i, ed
        
    # let's get the Work ID for one of the editions
    pprint(OpenLibrary.works(SURFACING_EDITION_OLID,id_type='olid'))

        
class FreebaseBooksTest(TestCase):
    def test_books_iter(self):
        fb = FreebaseBooks()
        books = list(islice(fb.books(),4))
        self.assertEqual(len(books),4)
        for book in books[0:1]:
            self.assertTrue(book["type"], "/book/book")
    def test_book_editions_iter(self):
        fb = FreebaseBooks()
        editions = list(islice(fb.book_editions(),4))
        self.assertEqual(len(editions),4)
        for edition in editions[0:1]:
            self.assertTrue(edition["type"], "/book/book_edition")
    def test_book_edition_by_id(self):
        fb = FreebaseBooks()
        # http://www.amazon.com/New-Collected-Poems-Czeslaw-Milosz/dp/006019667X
        edition = list(fb.book_edition_by_id('9780060196677','isbn'))
        self.assertEqual(edition[0]['type'],'/book/book_edition')
        self.assertEqual(edition[0]['book']['id'],'/m/0c1t1yk')
        self.assertEqual(edition[0]['book']['name'],'New and collected poems 1931-2001')
        
        edition = list(fb.book_edition_by_id('76074298', 'OCLC_number'))
        self.assertEqual(edition[0]['type'],'/book/book_edition')
        self.assertEqual(edition[0]['book']['id'],'/m/021yncj')
        self.assertEqual(edition[0]['book']['name'],'Brave New Words: The Oxford Dictionary of Science Fiction')
        
        # test openlibary_id Moby Dick
        edition = list(fb.book_edition_by_id('9780486432151', 'isbn'))[0]
        self.assertEqual(edition['openlibrary_id'][0]['value'], 'OL3685847M')
    def test_editions_for_book(self):
        fb = FreebaseBooks()
        book_id = '/en/moby-dick'
        editions = fb.editions_for_book(book_id)
        for i, edition in enumerate(editions):
            pass
    def test_xisbn(self):
        isbn_val = '9780486432151'
        book_id = '/en/moby-dick'
        fb = FreebaseBooks()
        isbns = set(fb.xisbn(isbn_val))
        isbns2 = set(fb.xisbn(book_id=book_id))
        self.assertEqual(isbns, isbns2)
        
                

class OpenLibraryTest(TestCase):
    def test_books(self):
        book = OpenLibrary.books(MASHUPBOOK_ISBN_10)
        self.assertEqual(book.values()[0]['info_url'], 'http://openlibrary.org/books/OL13439114M/Pro_Web_2.0_Mashups')
        book_data = OpenLibrary.books('0385472579', jscmd='data')
        self.assertEqual(book_data.values()[0]['title'], 'Zen Speaks')
        self.assertEqual(book_data.values()[0]['identifiers']['openlibrary'][0], 'OL7440033M')
    def test_books_olid(self):
        # can we status of a pd book oclc:03544699 The Log of a Cowboy - Andy Adams, 1903
        # http://openlibrary.org/books/OL7173600M/The_log_of_a_cowboy
        book = OpenLibrary.books('OL7173600M', 'olid', jscmd='data')
        self.assertEqual(book.values()[0]['title'], 'The log of a cowboy')
    def test_books_oclc(self):
        # http://openlibrary.org/books/OL6542070M/The_Montessori_method works
        book = OpenLibrary.books('1181252','oclc',jscmd='data')
        self.assertEqual(book.values()[0]['title'], 'The Montessori method')
    def test_read(self):
        results = OpenLibrary.read([(MASHUPBOOK_ISBN_10,'isbn'),('1181252','oclc')])
        self.assertEqual(results['oclc:1181252']['records'].values()[0]['data']['ebooks'][0]['formats']['epub']['url'],
                         'http://www.archive.org/download/cu31924032538500/cu31924032538500.epub')        
    def test_covers(self):
        self.assertEqual(OpenLibrary.covers(MASHUPBOOK_ISBN_10, size='M'),
                         'http://covers.openlibrary.org/b/isbn/159059858X-M.jpg')
    def test_author_photos(self):
        self.assertEqual(OpenLibrary.author_photos(RY_OLID,'S'), 'http://covers.openlibrary.org/a/olid/OL4264806A-S.jpg')
    def test_editions(self):
        # let's bring up the editions for Surfacing
        for (i,ed) in enumerate(islice(OpenLibrary.editions(SURFACING_WORK_OLID),100)):
            self.assertTrue(re.match(r'^OL(\d+)M$',ed))
    def test_works0(self):
        self.assertEqual(OpenLibrary.works0(SURFACING_EDITION_OLID,id_type='olid')[0], 'OL675829W')
    def test_works(self):
        ids = [(MASHUPBOOK_ISBN_10, 'isbn'), (SURFACING_EDITION_OLID,'olid'), ('233434','isbn')]
        resp = list(OpenLibrary.works(ids))
        self.assertEqual(resp, [['OL10306321W'], ['OL675829W'], []])

class WorkMapperTest(TestCase):
    def test_freebase_book_to_openlibrary_work(self):
        id = '/en/moby-dick'
        id = '/en/wuthering_heights'
        work_ids = list(WorkMapper.freebase_book_to_openlibrary_work(id, complete_search=True))
        print work_ids
    def test_work_info_from_openlibrary(self):
        editions = list(OpenLibrary.editions(SURFACING_WORK_OLID))
        print editions, len(editions)
        
def suite():
    
    #testcases = [WorkMapperTest]
    testcases = []
    suites = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(testcase) for testcase in testcases])
    suites.addTest(WorkMapperTest('test_work_info_from_openlibrary')) 
    #suites.addTest(SettingsTest('test_dev_me_alignment'))  # give option to test this alignment
    return suites    
    
if __name__ == '__main__':
    #look_up_my_zotero_books_in_hathi()
    #ol_practice()
    #print len(list(islice(parse_project_gutenberg_catalog(),100000)))
    #unittest.main()
    suites = suite()
    #suites = unittest.defaultTestLoader.loadTestsFromModule(__import__('__main__'))
    unittest.TextTestRunner().run(suites)    
    
    

