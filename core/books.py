from django.conf import settings

import json
import logging

import requests

def get_edition(isbn):

    # lookup the isbn at googlebooks
    results = googlebooks_search("isbn:%s" % isbn)
    if results['totalItems'] == 0:
        return None
    elif results['totalItems'] > 1:
        return LookupFailure("multiple results for isbn %s" % isbn)

    # get the edition detail from google
    google_id = results['items'][0]['id']
    i = googlebooks_volume(google_id)

    # normalize some of the googlebooks data
    edition = {
        'title': i['volumeInfo']['title'],
        'authors': i['volumeInfo']['authors'],
        'description': i['volumeInfo']['description'],
        'categories': i['volumeInfo']['categories'],
        'language': i['volumeInfo']['language'],
        'publisher': i['volumeInfo']['publisher'],
        'publication_date': i['volumeInfo']['publishedDate'],
        'page_count': i['volumeInfo']['pageCount'],
        'google_books_id': i['id'],
        'cover_image_url': i['volumeInfo']['imageLinks']['thumbnail'],
        'isbn_10': [],
        'isbn_13': []
    }

    for identifier in i['volumeInfo'].get('industryIdentifiers', []):
        if identifier['type'] == 'ISBN_10':
            edition['isbn_10'].append(identifier['identifier'])
        elif identifier['type'] == 'ISBN_13':
            edition['isbn_13'].append(identifier['identifier'])

    return edition


def get_work(isbn):
    return {'title': 'Neuromancer'}


def googlebooks_search(q):
    params = {"q": q, "key": settings.GOOGLE_BOOKS_API_KEY}
    url = 'https://www.googleapis.com/books/v1/volumes'
    return _get_json(url, params)


def googlebooks_volume(google_books_id):
    params = {"key": settings.GOOGLE_BOOKS_API_KEY}
    url = "https://www.googleapis.com/books/v1/volumes/%s" % google_books_id
    return _get_json(url, params)


def _get_json(url, params):
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return json.loads(response.content)
    else:
        logging.error("unexpected HTTP response: %s" % response)
        raise LookupFailure("GET failed: url=%s and params=%s" % (url, params))

class LookupFailure(Exception):
    pass


if __name__ == "__main__":
    # list of books from Amanda
    isbns = [
        # amanda's first list
        "0811216993", "0811216713", "1564780880", "0156709902",
        "0803260970", "0231145365", "0745647863", "0393302318",
        "1590171101", "015602909X", "0156576813", "0156982900",
        "0156189798", "0553380834", "0375706682", "055380491X",
        "0553378589", "0684831074", "0761148574", "1563053381",
        "0520256093", "0679442707", "0375754741",

        # amanda's second list
        "0547773986", "0719595800", "1582432104", "0156372088",
        "0139391401", "0300022867", "0300084587", "0691063184",
        "0691004765", "0940242753", "0671240773", "0060852240",
        "0307270807", "0520047834", "0471609978", "0030839939",
        "0465027822", "0465028381", "0716760355", "1597261076",
        "1559638583", "0393014886", "0452011752", "0151400563",
        "0812536363", "0441007465", "0441569595", "0441012035",
        "0393311198", "0525200150", "0375704078", "0773723749",
        "0760759146", "0441478123", "0553383043", "006076029X",
        "0802714544", "0743442539", "0743431677",
    ]

    for isbn in isbns:
        print get_edition(isbn)


