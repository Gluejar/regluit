import json
import logging
from xml.etree import ElementTree

import requests
from django.conf import settings

from regluit.core import models

logger = logging.getLogger(__name__)


def add_by_isbn(isbn):
    url = "https://www.googleapis.com/books/v1/volumes"
    results = _get_json(url, {"q": "isbn:%s" % isbn})

    if not results.has_key('items') or len(results['items']) == 0:
        logger.warn("no google hits for %s" % isbn)
        return None

    return add_by_googlebooks_id(results['items'][0]['id'])


def add_by_googlebooks_id(googlebooks_id):
    url = "https://www.googleapis.com/books/v1/volumes/%s" % googlebooks_id
    d = _get_json(url)['volumeInfo']

    e, created = models.Edition.objects.get_or_create(googlebooks_id=googlebooks_id)
    if not created:
        return e

    e.title = d.get('title')
    e.description = d.get('description')
    e.publisher = d.get('publisher')
    e.publication_date = d.get('publishedDate')

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

    # add a stub Work for the edition 
    if e.work == None:
        w = models.Work.objects.create(title=e.title)
        w.editions.add(e)

    return e


def thingisbn(isbn):
    url = "http://www.librarything.com/api/thingISBN/%s" % isbn
    xml = requests.get(url, headers={"User-Agent": settings.USER_AGENT}).content
    doc = ElementTree.fromstring(xml)
    return [e.text for e in doc.findall('isbn')]

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
