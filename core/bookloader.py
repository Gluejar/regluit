import json
import logging
import datetime

import requests
from xml.etree import ElementTree

from django.db.models import Q
from django.conf import settings
from django.db import IntegrityError

from regluit.core import models
import regluit.core.isbn

logger = logging.getLogger(__name__)


def add_by_oclc(oclc):
    logger.info("adding book by oclc %s", oclc)
    for edition in models.Edition.objects.filter(oclc=oclc):
        return edition

    url = "https://www.googleapis.com/books/v1/volumes"
    results = _get_json(url, {"q": '"OCLC%s"' % oclc})

    if not results.has_key('items') or len(results['items']) == 0:
        logger.warn("no google hits for %s" % oclc)
        return None

    try:
        e = add_by_googlebooks_id(results['items'][0]['id'])
        e.oclc = oclc
        e.save()
        return e
    except LookupFailure, e:
        logger.exception("failed to add edition for %s", oclc)
    except IntegrityError, e:
        logger.exception("google books data for %s didn't fit our db", oclc)
    return None


def add_by_isbn(isbn, work=None):
    """add a book to the UnglueIt database based on ISBN. The work parameter
    is optional, and if not supplied the edition will be associated with
    a stub work.
    """
    if not isbn:
        return None
    if len(isbn)==10:
        isbn=regluit.core.isbn.convert_10_to_13(isbn)
    
    logger.info("adding book by isbn %s", isbn)
    # save a lookup to google if we already have this isbn
    has_isbn =  Q(isbn_13=isbn)
    for edition in models.Edition.objects.filter(has_isbn):
        edition.new = False
        return edition

    url = "https://www.googleapis.com/books/v1/volumes"
    results = _get_json(url, {"q": "isbn:%s" % isbn})

    if not results.has_key('items') or len(results['items']) == 0:
        logger.warn("no google hits for %s" % isbn)
        return None

    try:
        return add_by_googlebooks_id(results['items'][0]['id'], work)
    except LookupFailure, e:
        logger.exception("failed to add edition for %s", isbn)
    except IntegrityError, e:
        logger.exception("google books data for %s didn't fit our db", isbn)
    return None


def add_by_googlebooks_id(googlebooks_id, work=None):
    """add a book to the UnglueIt database based on the GoogleBooks ID. The
    work parameter is optional, and if not supplied the edition will be 
    associated with a stub work.
    """

    # don't ping google again if we already know about the edition
    try:
        e = models.Edition.objects.get(googlebooks_id=googlebooks_id)
        return e
    except models.Edition.DoesNotExist:
        pass

    logger.info("loading metadata from google for %s", googlebooks_id)
    url = "https://www.googleapis.com/books/v1/volumes/%s" % googlebooks_id
    item  = _get_json(url)
    d = item['volumeInfo']

    # don't add the edition to a work with a different language
    # https://www.pivotaltracker.com/story/show/17234433
    language = d.get('language')
    if work and work.language != language:
        logger.warn("ignoring %s since it is %s instead of %s" %
                (googlebooks_id, language, work.language))
        return
 
    e = models.Edition(googlebooks_id=googlebooks_id)
    e.title = d.get('title')
    e.description = d.get('description')
    e.publisher = d.get('publisher')
    e.publication_date = d.get('publishedDate', '')
   
    for i in d.get('industryIdentifiers', []):
        if i['type'] == 'ISBN_13':
            e.isbn_13 = i['identifier']
        elif i['type'] == 'ISBN_13':
            e.isbn_13 = i['identifier']

    e.save()
    e.new=True

    for a in d.get('authors', []):
        a, created = models.Author.objects.get_or_create(name=a)
        a.editions.add(e)

    access_info = item.get('accessInfo')
    if access_info:
        e.public_domain = item.get('public_domain', None)
        epub = access_info.get('epub')
        if epub and epub.get('downloadLink'):
            ebook = models.Ebook(edition=e, format='epub',
                                 url=epub.get('downloadLink'),
                                 provider='google')
            ebook.save()
            
        pdf = access_info.get('pdf')
        if pdf and pdf.get('downloadLink'):
            ebook = models.Ebook(edition=e, format='pdf',
                                 url=pdf.get('downloadLink', None),
                                 provider='google')
            ebook.save()            

    # if we know what work the edition should be attached to, attach it
    if work:
        work.editions.add(e)

    # otherwise we need to create a stub work
    else:
        w = models.Work.objects.create(title=e.title, language=language)
        w.editions.add(e)

    return e


def add_related(isbn):
    """add all books related to a particular ISBN to the UnglueIt database.
    The initial seed ISBN will be added if it's not already there.
    """
    # make sure the seed edition is there
    logger.info("adding related editions for %s", isbn)
    edition = add_by_isbn(isbn)

    # this is the work everything will hang off
    work = edition.work

    new_editions = []
    for other_isbn in thingisbn(isbn):
        # 979's come back as 13
        if len(other_isbn)==10:
            other_isbn=regluit.core.isbn.convert_10_to_13(other_isbn)
        related_edition = add_by_isbn(other_isbn, work)
        if related_edition and related_edition.work != edition.work:
            merge_works(edition.work, related_edition.work)
        if related_edition:
            new_editions.append(related_edition)

    return new_editions


def thingisbn(isbn):
    """given an ISBN return a list of related edition ISBNs, according to 
    Library Thing. (takes isbn_10 or isbn_13, returns isbn_10, except for 979 isbns, which come back as isbn_13')
    """
    logger.info("looking up %s at ThingISBN" % isbn)
    url = "http://www.librarything.com/api/thingISBN/%s" % isbn
    xml = requests.get(url, headers={"User-Agent": settings.USER_AGENT}).content
    doc = ElementTree.fromstring(xml)
    return [e.text for e in doc.findall('isbn')]


def merge_works(w1, w2):
    """will merge the second work (w2) into the first (w1)
    """
    logger.info("merging work %s into %s", w1, w2)
    for edition in w2.editions.all():
        edition.work = w1
        edition.save()
    for campaign in w2.campaigns.all():
        campaign.work = w1
        campaign.save()
    for wishlist in models.Wishlist.objects.filter(works__in=[w2]):
        w2source=wishlist.work_source(w2)
        wishlist.remove_work(w2)
        wishlist.add_work(w1, w2source)
    # TODO: should we decommission w2 instead of deleting it, so that we can
    # redirect from the old work URL to the new one?
    w2.delete()


def add_openlibrary(work):
    work.openlibrary_lookup = datetime.datetime.now()
    work.save()

    # find the first ISBN match in OpenLibrary
    logger.info("looking up openlibrary data for work %s", work.id)
    found = False
    e = None # openlibrary edition json
    w = None # openlibrary work json

    # get the 1st openlibrary match by isbn that has an associated work
    url = "http://openlibrary.org/api/books"
    params = {"format": "json", "jscmd": "details"}
    for edition in work.editions.all():
        isbn_key = "ISBN:%s" % edition.isbn_13
        params['bibkeys'] = isbn_key
        e = _get_json(url, params)
        if e.has_key(isbn_key) and e[isbn_key]['details'].has_key('works'):
            work_key = e[isbn_key]['details']['works'].pop(0)['key']
            logger.info("got openlibrary work %s for isbn %s", work_key, isbn_key)
            w = _get_json("http://openlibrary.org" + work_key)
            if w.has_key('subjects'):
                found = True
                break

    if not found:
        logger.warn("unable to find work %s at openlibrary", work.id)
        return 

    # add the subjects to the Work
    for s in w.get('subjects',  []):
        logger.info("adding subject %s to work %s", s, work.id)
        subject, created = models.Subject.objects.get_or_create(name=s)
        work.subjects.add(subject)

    work.openlibrary_id = w['key']
    work.save()
    # TODO: add authors here once they are moved from Edition to Work
    # TODO: add LCCN, LibraryThing, GoodReads to appropriate models


def _get_json(url, params={}):
    # TODO: should X-Forwarded-For change based on the request from client?
    headers = {'User-Agent': settings.USER_AGENT, 
               'Accept': 'application/json',
               'X-Forwarded-For': '69.174.114.214'}
    params['key'] = settings.GOOGLE_BOOKS_API_KEY
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return json.loads(response.content)
    else:
        logger.error("unexpected HTTP response: %s" % response)
        raise LookupFailure("GET failed: url=%s and params=%s" % (url, params))


class LookupFailure(Exception):
    pass
