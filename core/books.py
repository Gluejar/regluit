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


def add_book(isbn):
    url = "http://openlibrary.org/api/books"
    bibkeys = "ISBN:%s" % isbn
    params = {"bibkeys": bibkeys, "jscmd": "details", "format": "json"}
    results = get_json(url, params)
    if results.has_key(bibkeys):
        return save_edition(results[bibkeys]['details'])
    elif len(isbn) == 10:
        return add_book(convert_10_to_13(isbn))
    else:
        return None


def save_edition(edition_data):
    edition = models.Edition()
    edition.title = edition_data.get('title')
    edition.description = edition_data.get('description')
    edition.publisher = first(edition_data, 'publishers')
    edition.publication_date = edition_data.get('publish_date')
    edition.save()

    for work_data in edition_data.get('works', []):
        save_work(work_data['key'], edition)

    for isbn_10 in edition_data.get('isbn_10', []):
        models.EditionIdentifier.objects.get_or_create(name='isbn_10', value=isbn_10, edition=edition)

    for isbn_13 in edition_data.get('isbn_13', []):
        models.EditionIdentifier.objects.get_or_create(name='isbn_13', value=isbn_13, edition=edition)

    for cover_id in edition_data.get('covers', []):
        models.EditionCover.objects.get_or_create(openlibrary_id=cover_id, edition=edition)

    return edition


def save_work(work_key, edition):
    url = "http://openlibrary.org" + work_key
    work_data = get_json(url)

    work = models.Work()
    work.title = work_data.get('title')
    work.openlibrary_id = work_key
    work.save()
    
    for author_data in work_data.get('authors', []):
        save_author(author_data['author']['key'], work)

    for subject_name in work_data.get('subjects', []):
        subject, created = models.Subject.objects.get_or_create(name=subject_name)
        work.subjects.add(subject)

    work.editions.add(edition)

    return work


def save_author(author_key, work):
    url = "http://openlibrary.org" + author_key
    author_data = get_json(url)

    author = models.Author()
    author.name = author_data['name']
    author.save()

    author.works.add(work)

    return author


def first(dictionary, key):
    l = dictionary.get(key, [])
    if len(l) == 0: return None
    return l[0]


def get_json(url, params={}):
    headers = {'User-Agent': 'unglue.it bot', 'Accept': 'application/json'}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return json.loads(response.content)
    else:
        logging.error("unexpected HTTP response: %s" % response)
        raise LookupFailure("GET failed: url=%s and params=%s" % (url, params))


class LookupFailure(Exception):
    pass
