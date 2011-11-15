import requests
import urllib
import httplib
from regluit.experimental.zotero_books import Zotero2, MyZotero
import json
from pprint import pprint
from itertools import islice

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
RY_OLID = 'OL4264806A'

SURFACING_WORK_OLID = 'OL675829W'
SURFACING_EDITION_OLID = 'OL8075248M'

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
    def works(cls, id, id_type='isbn'):
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
                raise OpenLibraryException("Assumption of 1 key in response invalid in OpenLibrary.works")
        except Exception, e:
            raise OpenLibraryException("problem in works: %s " % e)

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
  "book": {
    "id":   null,
    "name": null
  }
}]""".replace("\n"," ")
        query = json.loads(MQL)
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
  "book": {
    "id":   null,
    "name": null
  }
}]""".replace("\n"," ")
        query = json.loads(MQL)
        if id_type == 'isbn':
            query[0][id_type][0].setdefault('name', id)
        elif id_type in ['LCCN', 'OCLC_number']:
            query[0][id_type][0].setdefault('value', id)
            
        if id_type in ['isbn', 'LCCN', 'OCLC_number']:
            resp = self.freebase.mqlreaditer(query)
            for r in resp:
                yield r           
        else:
            raise FreebaseException('id_type must be one of ISBN, LCCN, or OCLC_number, not %s' % (id_type))
            

def look_up_my_zotero_books_in_hathi():
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
        
                

if __name__ == '__main__':
    #look_up_my_zotero_books_in_hathi()
    #ol_practice()
    #print len(list(islice(parse_project_gutenberg_catalog(),100000)))
    unittest.main()
    
    

