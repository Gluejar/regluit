import requests
import urllib
import httplib
import json
from pprint import pprint
from itertools import islice, izip, repeat
import logging
from xml.etree import ElementTree



import sys, os

# a kludge to allow for isbn.py to be imported 
# and not just in the context of the regluit Django app

try:
    from regluit.core import isbn as isbn_mod
except:
    import isbn as isbn_mod

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

GOOGLE_BOOKS_KEY = "AIzaSyCewoH_s2LmrxWD5XNwed3izNnA3dUqMlo"

MASHUPBOOK_ISBN_13 = '9781590598580'
MASHUPBOOK_ISBN_10 = '159059858X'
MASHUPBOOK_OLID = 'OL13439114M'
RY_OLID = 'OL4264806A'

SURFACING_WORK_OLID = 'OL675829W'
SURFACING_EDITION_OLID = 'OL8075248M'
SURFACING_ISBN = '9780446311076'

USER_AGENT = "rdhyee-test"

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
    
def thingisbn(isbn):
    """given an ISBN return a list of related edition ISBNs, according to 
    Library Thing. (takes isbn_10 or isbn_13, returns isbn_10, except for 979 isbns, which come back as isbn_13')
    """
    logger.info("looking up %s at ThingISBN" , isbn)
    url = "http://www.librarything.com/api/thingISBN/%s" % isbn
    xml = requests.get(url, headers={"User-Agent": USER_AGENT}).content
    doc = ElementTree.fromstring(xml)
    return [e.text for e in doc.findall('isbn')]

def hathi_bib(id, id_type='isbn', detail_level='brief'):
    url = "http://catalog.hathitrust.org/api/volumes/brief/%s/%s.json"  % (id_type, id)
    r = requests.get(url)
    if r.status_code == httplib.OK:
        return r.content
    else:
        raise Exception("Hathi Bib API response: %s " % (httplib.responses[r.status_code]) )
        
class GoogleBooks(object):
    def __init__(self, key):
        self.key = key
    def isbn (self, isbn, glossed=True):
        url = "https://www.googleapis.com/books/v1/volumes"
        try:
            results = self._get_json(url, {"q": "isbn:%s" % isbn})
        except LookupFailure:
            logger.exception("lookup failure for %s", isbn)
            return None
        if not results.has_key('items') or len(results['items']) == 0:
            logger.warn("no google hits for %s" , isbn)
            return None
        else:
            if glossed:
                return self._get_item(results)
            else:
                return results
    def _get_item(self, results):
        if len(results):

            google_books_id = results['items'][0]['id']
            item = results['items'][0]
            
            d = item['volumeInfo']
            title = d.get('title')
            language = d.get('language')
            identifiers = d.get('industryIdentifiers', [])
            ratings_count = d.get('ratingsCount')

            # flip [{u'identifier': u'159059858X', u'type': u'ISBN_10'}, {u'identifier': u'9781590598580', u'type': u'ISBN_13'}] to
            #    {u'ISBN_13': u'9781590598580', u'ISBN_10': u'159059858X'}
            identifiers = dict([(id["type"],id["identifier"]) for id in d.get('industryIdentifiers', [])])
            
            isbn = identifiers.get('ISBN_13') or identifiers.get('ISBN_10')
            if isbn:
                isbn = isbn_mod.ISBN(isbn).to_string('13')
                
            published_date = d.get('publishedDate')
            publisher = d.get('publisher')
            
            data = {'title':title, 'language':language, 'isbn':isbn, 'google_books_id': google_books_id,
                    'ratings_count':ratings_count, 'published_date':published_date, 'publisher':publisher}
        else:
            data = None
        return data
    def _get_json(self, url, params={}, type='gb'):
        # lifted (with slight mod) from https://github.com/Gluejar/regluit/blob/master/core/bookloader.py
        # TODO: should X-Forwarded-For change based on the request from client?
        headers = {'User-Agent': 'raymond.yee@gmail.com', 
                   'Accept': 'application/json',
                   'X-Forwarded-For': '69.174.114.214'}
        if type == 'gb':
            params['key'] = self.key
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return json.loads(response.content)
        else:
            logger.error("unexpected HTTP response: %s" % response)
            if response.content:
                logger.error("response content: %s" % response.content)
            raise LookupFailure("GET failed: url=%s and params=%s" % (url, params))

class OpenLibrary(object):
    """http://openlibrary.org/developers/api"""
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
    @classmethod
    def json_for_olid(cls, olid, follow_redirect=True):
        ol_types = {'M': 'books', 'W':'works', 'A':'authors'}
        id_type = ol_types.get(str(olid)[-1].upper(), None)
        if id_type is not None:
            url = "http://openlibrary.org/{0}/{1}.json".format(id_type, olid.upper())
            r = requests.get(url)  
            if r.status_code == httplib.OK:
                # check to see whether type is redirect, retrieve that item it we are following redirects
                resp = json.loads(r.content)
                if resp["type"]["key"] == "/type/redirect" and follow_redirect:
                    redir_olid = resp["location"].split("/")[-1]
                    return OpenLibrary.json_for_olid(redir_olid)
                else:
                    return resp
            else:
                raise OpenLibraryException("OpenLibrary API response: %s " % (httplib.responses[r.status_code]) )
        else:
            return None
    @classmethod
    def xisbn(cls,isbn_val=None, work_id=None, page_size=5):
        
        isbns = set()
        
        if isbn_val is None and work_id is None:
            raise Exception("One of isbn or work_id must be specified")
        elif isbn_val is not None and work_id is not None:
            raise Exception("Only only of isbn or work_id can be specified")
            
        if isbn_val is not None:
            # figure out the work_id and then pass back all the ISBNs from the manifestations of the work
            try:
                isbn_val = isbn_mod.ISBN(isbn_val).to_string('13')
                isbns.add(isbn_val)
                yield isbn_val
                
                work_ids = list(cls.works([(isbn_val,'isbn')]))
                if len(work_ids):
                    work_id = work_ids[0][0]
                else: # can't find a work_id
                    raise StopIteration()
            except isbn_mod.ISBNException:
                raise StopIteration()
 
        # by this point we have a work_id
         
        editions = cls.editions(work_olid=work_id)
        
        for page in grouper(editions, page_size):
            query = list(izip(page, repeat('olid')))
            #print query
            k = cls.read(query)      
            for edition in page:
                # k['olid:OL8075248M']['records'].values()[0]['data']['identifiers']['isbn_13'][0]
                identifiers =  k['olid:{0}'.format(edition)]['records'].values()[0]['data']['identifiers']
                isbn = identifiers.get('isbn_13',[None])[0] or identifiers.get('isbn_10',[None])[0]
                if isbn:
                    try:
                        isbn = isbn_mod.ISBN(isbn).to_string('13')
                        if isbn not in isbns:
                            isbns.add(isbn)
                            yield isbn
                    except isbn_mod.ISBNException:
                        print "Problem with isbn %s for edition %s " % (isbn, edition)
                    except Exception as e:
                        raise e
        
 

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
            isbn_val = isbn_mod.ISBN(isbn_val).to_string('13')
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
        # grab all ISBNs correponding to Freebase fb_id and compute the OpenLibrary work ID
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


class LookupFailure(Exception):
    pass
        
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
        ids =[(MASHUPBOOK_ISBN_10, 'isbn'), (SURFACING_EDITION_OLID,'olid'), ('233434','isbn')]
        resp = list(OpenLibrary.works(ids))
        self.assertEqual(resp, [['OL10306321W'], ['OL675829W'], []])
    def test_json_for_olid(self):
        # manifestation
        # http://openlibrary.org/books/OL13439114M.json
        id = "OL13439114M"
        edition = OpenLibrary.json_for_olid(id)
        self.assertEqual(edition["title"], "Pro Web 2.0 Mashups")
        self.assertEqual(edition["identifiers"]["librarything"], ['2771144'])
        self.assertEqual(edition["subjects"], ['Mashups (World Wide Web)'])
        
        # work
        # http://openlibrary.org/works/OL10306321W.json
        id = "OL10306321W"
        work = OpenLibrary.json_for_olid(id)
        self.assertEqual(work["title"], "Pro Web 2.0 Mashups")
        self.assertEqual(work["type"]["key"], "/type/work")
        self.assertEqual(work["authors"][0]["type"]["key"], "/type/author_role")
        self.assertEqual(work["authors"][0]["author"]["key"], "/authors/OL4264806A")

        # author
        # http://openlibrary.org/authors/OL4264806A.json
        id = "OL4264806A"
        author = OpenLibrary.json_for_olid(id)
        self.assertEqual(author["name"], "Raymond Yee")
        
        # redirect ok?
        #  "OL14917149W" -> "OL362684W"
        id = "OL14917149W"
        work = OpenLibrary.json_for_olid(id,follow_redirect=True)
        self.assertEqual(work["title"], "King Richard III")
        self.assertEqual(work["key"], "/works/OL362684W")
    
        work = OpenLibrary.json_for_olid(id,follow_redirect=False)
        self.assertEqual(work["type"]["key"], "/type/redirect")
    def test_xisbn(self):
        work_id = SURFACING_WORK_OLID
        surfacing_fb_id = '/m/05p_vg'
        book_isbn = '9780446311076'
        
        #for isbn in islice(OpenLibrary.xisbn(work_id=work_id),5):
        #    print isbn
        fb = FreebaseBooks()
        gb = GoogleBooks(key=GOOGLE_BOOKS_KEY)
        fb_isbn_set = set(fb.xisbn(book_id=surfacing_fb_id))
        ol_isbn_set = set(OpenLibrary.xisbn(isbn_val=book_isbn))
        lt_isbn_set = set(map(lambda x: isbn_mod.ISBN(x).to_string('13'), thingisbn(SURFACING_ISBN)))
        
        print "Freebase set: ", len(fb_isbn_set), fb_isbn_set
        print "OpenLibrary set: ", len(ol_isbn_set), ol_isbn_set
        print "in both", len(fb_isbn_set & ol_isbn_set), fb_isbn_set & ol_isbn_set
        print "in fb but not ol", len(fb_isbn_set - ol_isbn_set), fb_isbn_set - ol_isbn_set
        print "in ol but not fb", len(ol_isbn_set - fb_isbn_set), ol_isbn_set - fb_isbn_set
        
        # compare thingisbn with ol
        print "thingisbn set:", len(lt_isbn_set), lt_isbn_set
        print "in both ol and lt", len(lt_isbn_set & ol_isbn_set), lt_isbn_set & ol_isbn_set
        print "in lt but not ol", len(lt_isbn_set - ol_isbn_set), lt_isbn_set - ol_isbn_set
        print "in ol but not lt", len(ol_isbn_set - lt_isbn_set), ol_isbn_set - lt_isbn_set        
        
        # run through the intersection set and query Google Books
        for (i, isbn) in enumerate(fb_isbn_set & ol_isbn_set & lt_isbn_set):
            print i, isbn, gb.isbn(isbn)
        

class WorkMapperTest(TestCase):
    def test_freebase_book_to_openlibrary_work(self):
        id = '/en/moby-dick'
        #id = '/en/wuthering_heights'
        work_ids = list(WorkMapper.freebase_book_to_openlibrary_work(id, complete_search=True))
        print work_ids
    def test_work_info_from_openlibrary(self):
        editions = list(OpenLibrary.editions(SURFACING_WORK_OLID))
        print editions, len(editions)

class GoogleBooksTest(TestCase):
    def test_isbn(self):
        isbn_num = MASHUPBOOK_ISBN_13
        gb = GoogleBooks(key=GOOGLE_BOOKS_KEY)
        item = gb.isbn(isbn_num)
        self.assertEqual(item['isbn'], '9781590598580')
        self.assertEqual(item['language'], 'en')
        
class thingISBNTest(TestCase):
    def test_lt_isbn(self):
        isbns = thingisbn(SURFACING_ISBN)
        # convert to isbn-13
        isbns = map(lambda x: isbn_mod.ISBN(x).to_string('13'), isbns)
        print isbns
        
def suite():
    
    #testcases = [WorkMapperTest,FreebaseBooksTest, OpenLibraryTest,GoogleBooksTest]
    testcases = []
    suites = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(testcase) for testcase in testcases])
    suites.addTest(OpenLibraryTest('test_xisbn'))
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
    
    

