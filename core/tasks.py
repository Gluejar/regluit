from celery.decorators import task

from regluit.core import bookloader

@task
def add_related(isbn):
    return bookloader.add_related(isbn)

@task
def add_by_isbn(isbn):
    return bookloader.add_by_isbn(isbn)
