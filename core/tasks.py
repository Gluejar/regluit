#
# external library imports
#
import logging
import random

from datetime import timedelta
from time import sleep
from celery.task import task

#
# django imports
#
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.management import call_command
from django.utils.timezone import now
from notification.engine import send_all
from notification import models as notification

from mailchimp3 import MailChimp


#
# regluit imports
#
from regluit.core import (
    bookloader,
    covers,
    models,
    librarything
)
from regluit.core.models import Acq, Campaign, EbookFile, Gift, UserProfile, Work
from regluit.core.signals import deadline_impending
from regluit.core.parameters import RESERVE, REWARDS, THANKS
from regluit.utils.localdatetime import date_today

logger = logging.getLogger(__name__)
mc_client = MailChimp(mc_api=settings.MAILCHIMP_API_KEY)

@task
def populate_edition(isbn):
    """given an edition this task will populate the database with additional
    information about related editions and subjects related to this edition
    """
    bookloader.add_related(isbn)
    edition = models.Edition.get_by_isbn(isbn)
    if edition:
        bookloader.add_openlibrary(edition.work)
    return edition

@task
def load_librarything_into_wishlist(user_id, lt_username, max_books=None):
    user = User.objects.get(id=user_id)
    return librarything.load_librarything_into_wishlist(user, lt_username, max_books)

@task
def fac(n, sleep_interval=None):
    # used to test celery task execution
    if not(isinstance(n, int) and n >= 0):
        raise Exception("You can't calculate a factorial of %s " % (str(n)))
    if n <= 1:
        return 1
    else:
        res = 1
        for i in range(2, n+1):
            res = res * i
            fac.update_state(state="PROGRESS", meta={"current": i, "total": n})
            if sleep_interval is not None:
                sleep(sleep_interval)
        return res


@task
def send_mail_task(subject, message, from_email, recipient_list,
                   fail_silently=False, auth_user=None, auth_password=None,
                   connection=None, override_from_email=True):
    """a task to drop django.core.mail.send_mail into """
    # NOTE:  since we are currently using Amazon SES, which allows email to be sent only from
    # validated email addresses, we force from_email to be one of the validated
    # address unless override_from_email is FALSE
    try:
        if override_from_email:
            try:
                from_email = settings.DEFAULT_FROM_EMAIL
            except:
                pass
        r = send_mail(subject, message, from_email, recipient_list, fail_silently=False,
                      auth_user=auth_user, auth_password=auth_password, connection=connection)
        logger.info('sent mail about %s to %s', subject, recipient_list)
    except:
        r = logger.info('failed to send message:', message)
    return r

#task to update the status of active campaigns
@task
def update_active_campaign_status():
    """update the status of all active campaigns -- presumed to be run at midnight Eastern time"""
    return [
        c.update_status(send_notice=True, ignore_deadline_for_success=True,
                        process_transactions=True) for c in Campaign.objects.filter(status='Active')
    ]

@task
def emit_notifications():
    logger.info('notifications emitting')
    send_all()

@task
def report_new_ebooks(created=None):   #created= creation date
    if created:
        period = (created, created+timedelta(days=1))
    else:
        period = (date_today()-timedelta(days=1), date_today())
    works = models.Work.objects.filter(editions__ebooks__created__range=period).distinct()
    for work in works:
        # only notify if a new ebooks are active, don't notify person if the book was just wished
        # ebooks() only returns active ebooks
        for ebook in work.ebooks().filter(created__range=period):
            notification.send_now(
                work.wished_by(excluding=period),
                "wishlist_unglued_book_released",
                {'work':work},
                True
            )
            break

@task
def notify_ending_soon():
    c_active = Campaign.objects.filter(status='Active', type=REWARDS)
    for c in c_active:
        if c.deadline - now() < timedelta(7) and c.deadline - now() >= timedelta(6):
            # if the campaign is still active and there's only a week left until it closes,
            # send reminder notification
            deadline_impending.send(sender=None, campaign=c)

@task
def watermark_acq(acq_id):
    try:
        acq = Acq.objects.get(acq_id)
    except Acq.DoesNotExist as e:
        logger.error("error getting acq %s", acq_id)
        return False
    acq.get_watermarked()

@task
def process_ebfs(campaign_id):
    try:
        campaign = Campaign.objects.get(campaign_id)
    except Campaign.DoesNotExist as e:
        logger.error("error getting acq %s", campaign_id)
        return False
    if campaign.type == THANKS:
        if campaign.use_add_ask:
            campaign.add_ask_to_ebfs()
        else:
            campaign.revert_asks()


@task
def refresh_acqs():
    in_10_min = now() + timedelta(minutes=10)
    acqs = Acq.objects.filter(refreshed=False, refreshes__lt=in_10_min)
    logger.info('refreshing %s acqs', acqs.count())
    for acq in acqs:
        for hold in acq.holds:
            # create a 1 day reserve on the acq
            reserve_acq = Acq.objects.create(
                user=hold.user,
                work=hold.work,
                license=RESERVE,
                lib_acq=acq,
            )
            # the post_save handler takes care of pushing expires  vis acq.expires_in

            # notify the user with the hold
            if 'example.org' not in reserve_acq.user.email:
                notification.send_now([reserve_acq.user], "library_reserve", {'acq':reserve_acq})
            # delete the hold
            hold.delete()
            break
        else:
            acq.refreshed = True

@task
def ml_subscribe_task(profile_id, **kwargs):
    try:
        profile = UserProfile.objects.get(profile_id)
    except UserProfile.DoesNotExist as e:
        logger.error("error getting profile %s", profile_id)
        return False

    try:
        if not profile.on_ml:
            data = {"email_address": profile.user.email, "status_if_new": "pending"}
            mc_client.lists.members.create_or_update(
                list_id=settings.MAILCHIMP_NEWS_ID,
                subscriber_hash=profile.user.email,
                data=data,
            )
            return True
    except Exception as e:
        logger.error("error subscribing to mailchimp list %s", e)
        return False

@task
def notify_unclaimed_gifts():
    unclaimed = Gift.objects.filter(used=None)
    for gift in unclaimed:
        # send notice every 7 days, but stop at 10x
        unclaimed_duration = (now() - gift.acq.created).days
        if unclaimed_duration > 70:
            return
        if unclaimed_duration > 0 and unclaimed_duration % 7 == 0: # first notice in 7 days
            notification.send_now([gift.acq.user], "purchase_gift_waiting", {'gift':gift}, True)
            notification.send_now([gift.giver], "purchase_notgot_gift", {'gift':gift}, True)

@task
def periodic_cleanup():
    call_command('clearsessions')
    call_command('cleanupregistration')

@task
def feature_new_work():
    works = Work.objects.filter(is_free=True, featured__isnull=True).order_by('-num_wishes')
    work = works[random.randrange(0, 50)]
    work.featured = now()
    work.save()

@task
def make_cover_thumbnail(url, geom_string, **options):
    success = covers.make_cover_thumbnail(url, geom_string, **options)
    if not success and url != '':
        for ed in models.Edition.objects.filter(cover_image=url):
            logger.error('bad cover image %s for edition: %s', url, ed.id)
            #ed.cover_image = ''
            #ed.save()
    