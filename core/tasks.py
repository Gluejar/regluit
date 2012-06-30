from time import sleep
from datetime import timedelta

import logging
logger = logging.getLogger(__name__)

from celery.task import task

from django.contrib.auth.models import User

from regluit.core import bookloader, models
from regluit.core import goodreads, librarything
from regluit.core.models import Campaign
from regluit.utils.localdatetime import now, date_today

from django.core.mail import send_mail

from notification.engine import send_all
from notification import models as notification

@task 
def populate_edition(isbn):
    """given an edition this task will populate the database with additional
    information about related editions and subjects related to this edition
    """
    bookloader.add_related(isbn)
    edition=models.Edition.get_by_isbn(isbn)
    if edition:
        bookloader.add_openlibrary(edition.work)
    return edition

@task
def load_goodreads_shelf_into_wishlist(user_id, shelf_name='all', goodreads_user_id=None, max_books=None,
                                       expected_number_of_books=None):
    user=User.objects.get(id=user_id)
    return goodreads.load_goodreads_shelf_into_wishlist(user,shelf_name,goodreads_user_id,max_books, expected_number_of_books)

@task
def load_librarything_into_wishlist(user_id, lt_username, max_books=None):
    user=User.objects.get(id=user_id)
    return librarything.load_librarything_into_wishlist(user, lt_username, max_books)
    
@task
def fac(n, sleep_interval=None):
    # used to test celery task execution 
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


@task
def send_mail_task(subject, message, from_email, recipient_list,
            fail_silently=False, auth_user=None, auth_password=None,
            connection=None):
    """a task to drop django.core.mail.send_mail into """   
    return send_mail(subject, message, from_email, recipient_list, fail_silently=False, auth_user=auth_user,
                     auth_password=auth_password, connection=connection)


#task to update the status of active campaigns

@task
def update_active_campaign_status():
    """update the status of all active campaigns -- presumed to be run at midnight Eastern time"""
    return [c.update_status(send_notice=True) for c in Campaign.objects.filter(status='Active') ]
 
@task
def emit_notifications():
    logger.info('notifications emitting' )
    return send_all()
    
@task
def report_new_ebooks(created=None):   #created= creation date
    if created:
        period = (created, created+timedelta(days=1))
    else:
        period = (date_today()-timedelta(days=1), date_today())
    works = models.Work.objects.filter(editions__ebooks__created__range = period).distinct()
    for work in works:
        notification.send_now(work.wished_by(), "wishlist_unglued_book_released", {'work':work}, True)

    