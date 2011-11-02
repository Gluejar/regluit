import mechanize
import csv
import HTMLParser
import logging
import re

logger = logging.getLogger(__name__)


class LibraryThing(object):
    """
    This class retrieves and parses the CSV representation of a LibraryThing user's library.
    """
    url = "https://www.librarything.com"
    csv_file_url = "http://www.librarything.com/export-csv"
    
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        self.csv_handle = None
    def retrieve_csv(self):
        br = mechanize.Browser()
        br.open(LibraryThing.url)
        # select form#2
        br.select_form(nr=1)
        br["formusername"] = self.username
        br["formpassword"] = self.password
        br.submit()
        self.csv_handle = br.open(LibraryThing.csv_file_url)
        return self.csv_handle
    def parse_csv(self):
        h = HTMLParser.HTMLParser()
        reader = csv.DictReader(self.csv_handle)
        # There are more fields to be parsed out.  Note that there is a second author column to handle
        for (i,row) in enumerate(reader):
            # ISBNs are written like '[123456789x]' in the CSV, suggesting possibility of a list
            m = re.match(r'^\[(.*)\]$', row["'ISBNs'"])
            if m:
                isbn = m.group(1).split()
            else:
                isbn = []
            yield {'title':h.unescape(row["'TITLE'"]), 'author':h.unescape(row["'AUTHOR (first, last)'"]),
                   'isbn':isbn, 'comment':row["'COMMENT'"],
                   'tags':row["'TAGS'"], 'collections':row["'COLLECTIONS'"],
                   'reviews':h.unescape(row["'REVIEWS'"])}

def load_librarything_into_wishlist(user, lt_username, lt_password, max_books=None):
    """
    Load a specified Goodreads shelf (by default:  all the books from the Goodreads account associated with user)
    """
   
    from regluit.core import bookloader
    from itertools import islice
    
    lt = LibraryThing(lt_username,lt_password)
    lt.retrieve_csv()
    for (i,book) in enumerate(islice(lt.parse_csv(),max_books)):
        isbn = book["isbn"][0]  # grab the first one
        logger.info("%d %s %s", i, book["title"], isbn)
        try:
            edition = bookloader.add_by_isbn(isbn)
            # let's not trigger too much traffic to Google books for now
            # regluit.core.tasks.add_related.delay(isbn)
            user.wishlist.works.add(edition.work)
            logger.info("Work with isbn %s added to wishlist.", isbn)
        except Exception, e:
            logger.info ("error adding ISBN %s: %s", isbn, e)             