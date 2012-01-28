from regluit.core import librarything, bookloader
import itertools

def ry_lt_books():
    lt = librarything.LibraryThing('rdhyee')
    books = lt.parse_user_catalog(view_style=5)
    return books

def editions_for_lt(books):
    editions = [bookloader.add_by_isbn(b["isbn"]) for b in books]
    return editions

def ry_lt_unloaded():
    books = list(ry_lt_books())
    editions = editions_for_lt(books)
    unloaded_books = [b for (b, ed) in itertools.izip(books, editions) if ed is None]
    return unloaded_books