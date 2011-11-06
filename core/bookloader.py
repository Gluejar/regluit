import json
import logging

import requests
from xml.etree import ElementTree

from django.db.models import Q
from django.conf import settings
from django.db import IntegrityError

from regluit.core import models

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
    logger.info("adding book by isbn %s", isbn)
    # save a lookup to google if we already have this isbn
    has_isbn = Q(isbn_10=isbn) | Q(isbn_13=isbn)
    for edition in models.Edition.objects.filter(has_isbn):
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
    e, created = models.Edition.objects.get_or_create(googlebooks_id=googlebooks_id)
    if not created:
        return e

    logger.info("loading metadata from google for %s", googlebooks_id)
    url = "https://www.googleapis.com/books/v1/volumes/%s" % googlebooks_id
    item  = _get_json(url)
    d = item['volumeInfo']

    e.title = d.get('title')
    e.description = d.get('description')
    e.publisher = d.get('publisher')
    e.publication_date = d.get('publishedDate')
    e.language = d.get('language')

    for i in d.get('industryIdentifiers', []):
        if i['type'] == 'ISBN_10':
            e.isbn_10 = i['identifier']
        elif i['type'] == 'ISBN_13':
            e.isbn_13 = i['identifier']

    for a in d.get('authors', []):
        a, created = models.Author.objects.get_or_create(name=a)
        a.editions.add(e)

    for s in d.get('categories', []):
        s, created = models.Subject.objects.get_or_create(name=s)
        s.editions.add(e)

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

    # if we know what work to add the edition to do it
    if work:
        work.editions.add(e)

    # otherwise we need to create a stub work
    else:
        w = models.Work.objects.create(title=e.title)
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
        related_edition = add_by_isbn(other_isbn, work)
        if related_edition and related_edition.work != edition.work:
            merge_works(edition.work, related_edition.work)
        if related_edition:
            new_editions.append(related_edition)

    return new_editions


def thingisbn(isbn):
    """given an ISBN return a list of related edition ISBNs, according to 
    Library Thing.
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
        wishlist.works.remove(w2)
        wishlist.works.add(w1)
    w2.delete()


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
