import logging

from celery.task import task

from .models import Target

logger = logging.getLogger(__name__)

def push_books_to_target(books, target):
    """given a list of books this task will push the books, metadata and covers to the target
    """
    for book in books:
        target.push_file(book)
        target.push_cover(book)
    target.push_onix(books)