from time import sleep

from celery.decorators import task

from regluit.core import bookloader
from regluit.core import goodreads, librarything

@task 
def populate_edition(edition):
    """given an edition this task will populate the database with additional
    information about related editions and subjects related to this edition
    """
    bookloader.add_related(edition.isbn_13)
    bookloader.add_openlibrary(edition.work)
    return edition

@task
def load_goodreads_shelf_into_wishlist(user, shelf_name='all', goodreads_user_id=None, max_books=None,
                                       expected_number_of_books=None):
    return goodreads.load_goodreads_shelf_into_wishlist(user,shelf_name,goodreads_user_id,max_books, expected_number_of_books)
    
@task
def load_librarything_into_wishlist(user, lt_username, max_books=None):
    return librarything.load_librarything_into_wishlist(user, lt_username, max_books)
    
@task
def add(x,y):
    return x+y

@task
def fac(n, sleep_interval=None):
    if not(isinstance(n,int) and n >= 0):
        raise Exception("You can't calculate a factorial of %s " % (str(n)))
    if n <= 1:
        return 1
    else:
        res = 1
        for i in xrange(2,n+1):
            res = res*i
            fac.update_state(state="PROGRESS", meta={"current": i, "total": n})
            if sleep_interval is not None:
                sleep(sleep_interval)
        return res
