"""
A simplistic module for looking up books via varioius web service APIs.
"""

import json
import requests

def openlibrary_book(isbn):
    response = requests.get("http://openlibrary.org/api/books?",
                            params={"bibkeys": "ISBN:%s" % isbn,
                                    "format": "json",
                                    "jscmd": "data"})
    if response.status_code != 200:
        raise LookupFailure("failed to look up %s at OpenLibrary" % isbn)
    hits = json.loads(response.content).values()
    if len(hits) == 1:
        return hits[0]
    return None

def googlebooks_book(isbn):
    response = requests.get('https://www.googleapis.com/books/v1/volumes', 
                            params={'q': "isbn:%s" % isbn})
    if response.status_code != 200:
        raise LookupFailure("failed to look up %s at GoogleBooks" % isbn)
    books = json.loads(response.content)
    if books['totalItems'] == 1:
        return books['items'][0]
    return None
    

class LookupFailure(Exception):
    pass

if __name__ == "__main__":
    # list of books from Amanda
    isbns = [
        "0811216993", "0811216713", "1564780880", "0156709902",
        "0803260970", "0231145365", "0745647863", "0393302318",
        "1590171101", "015602909X", "0156576813", "0156982900",
        "0156189798", "0553380834", "0375706682", "055380491X",
        "0553378589", "0684831074", "0761148574", "1563053381",
        "0520256093", "0679442707", "0375754741",
    ]

    for isbn in isbns:
        b = googlebooks_book(isbn)
        google_id = b['id'] if b != None else ""
        title = b['volumeInfo']['title']
        b = openlibrary_book(isbn)
        openlibrary_id = b['key'] if b != None else ""
        print "\t".join([isbn, title, google_id, openlibrary_id])
