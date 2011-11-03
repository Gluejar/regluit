from celery.decorators import task
from regluit.core import bookloader
from regluit.core import goodreads, librarything

@task
def add_related(isbn):
    return bookloader.add_related(isbn)

@task
def add_by_isbn(isbn):
    return bookloader.add_by_isbn(isbn)

@task
def load_goodreads_shelf_into_wishlist(user, shelf_name='all', goodreads_user_id=None, max_books=None):
    return goodreads.load_goodreads_shelf_into_wishlist(user,shelf_name,goodreads_user_id,max_books)
    
@task
def load_librarything_into_wishlist(user, lt_username, lt_password, max_books=None):
    return librarything.load_librarything_into_wishlist(user, lt_username, lt_password, max_books)
    
