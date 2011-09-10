"""
The module handles fetching books from OpenLibrary and adding them 
to the local database.
"""

import json
import logging

import requests
from django.conf import settings

from regluit.core import models
from regluit.core.isbn import convert_10_to_13

logger = logging.getLogger(__name__)

def add_book(isbn):
    url = "http://openlibrary.org/api/books"
    bibkeys = "ISBN:%s" % isbn
    params = {"bibkeys": bibkeys, "jscmd": "details", "format": "json"}
    results = _get_json(url, params)

    edition = None
    if results.has_key(bibkeys):
        logger.info("saving book info for %s", isbn)
        edition = _save_edition(results[bibkeys]['details'])
    elif len(isbn) == 10:
        isbn_13 = convert_10_to_13(isbn)
        logger.info("lookup failed for %s trying isbn13 %s", isbn, isbn_13)
        edition = add_book(isbn_13)
    else:
        logger.info("lookup failed for %s", isbn)

    return edition


def _save_edition(edition_data):
    edition_key = edition_data['key']
    edition, created = models.Edition.objects.get_or_create(openlibrary_id=edition_key)
    edition.title = edition_data.get('title')
    edition.description = edition_data.get('description')
    edition.publisher = _first(edition_data, 'publishers')
    edition.publication_date = edition_data.get('publish_date')

    # assumption: OL has only one isbn_10 or isbn_13 for an edition
    edition.isbn_10 = _first(edition_data, 'isbn_10')
    edition.isbn_13 = _first(edition_data, 'isbn_13')

    edition.save()

    for work_data in edition_data.get('works', []):
        _save_work(work_data['key'], edition)

    for cover_id in edition_data.get('covers', []):
        models.EditionCover.objects.get_or_create(openlibrary_id=cover_id, edition=edition)

    return edition


def _save_work(work_key, edition):
    url = "http://openlibrary.org" + work_key
    work_data = _get_json(url)

    work, created = models.Work.objects.get_or_create(openlibrary_id=work_key)
    work.title = work_data.get('title')
    work.save()
    
    for author_data in work_data.get('authors', []):
        _save_author(author_data['author']['key'], work)

    for subject_name in work_data.get('subjects', []):
        subject, created = models.Subject.objects.get_or_create(name=subject_name)
        work.subjects.add(subject)

    work.editions.add(edition)

    return work


def _save_author(author_key, work):
    url = "http://openlibrary.org" + author_key
    author_data = _get_json(url)

    author, created = models.Author.objects.get_or_create(openlibrary_id=author_key)
    author.name = author_data['name']
    author.save()

    author.works.add(work)

    return author


def _first(dictionary, key):
    l = dictionary.get(key, [])
    if len(l) == 0: return None
    return l[0]


def _get_json(url, params={}):
    headers = {'User-Agent': settings.USER_AGENT, 'Accept': 'application/json'}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return json.loads(response.content)
    else:
        logger.error("unexpected HTTP response: %s" % response)
        raise LookupFailure("GET failed: url=%s and params=%s" % (url, params))


class LookupFailure(Exception):
    pass
