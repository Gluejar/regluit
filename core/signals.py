from django.db.models import get_model
from django.db.utils import DatabaseError
from django.db.models import signals
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import Signal
from django.contrib.sites.models import Site
from django.conf import settings
from django.utils.translation import ugettext_noop as _

from notification import models as notification

from social_auth.signals import pre_update
from social_auth.backends.facebook import FacebookBackend
from tastypie.models import create_api_key

import registration.signals
import django.dispatch

import itertools
import logging
logger = logging.getLogger(__name__)

# get email from Facebook registration
def facebook_extra_values(sender, user, response, details, **kwargs):
    if response.get('email') is not None:
        user.email = response.get('email')
    return True

pre_update.connect(facebook_extra_values, sender=FacebookBackend)


# create Wishlist and UserProfile to associate with User
def create_user_objects(sender, created, instance, **kwargs):
    # use get_model to avoid circular import problem with models
    try:
        Wishlist = get_model('core', 'Wishlist')
        UserProfile = get_model('core', 'UserProfile')
        if created:
            Wishlist.objects.create(user=instance)
            UserProfile.objects.create(user=instance)
    except DatabaseError:
        # this can happen when creating superuser during syncdb since the
        # core_wishlist table doesn't exist yet
        return

post_save.connect(create_user_objects, sender=User)


# create API key for new User
post_save.connect(create_api_key, sender=User)

def merge_emails(sender, user, **kwargs):
    logger.info('checking %s' % user.username)
    try:
        old_user=User.objects.exclude(id=user.id).get(email=user.email)
        old_user.username=user.username
        old_user.password=user.password
        user.delete()
        old_user.save()
    except User.DoesNotExist:
        return

registration.signals.user_activated.connect(merge_emails)

# create notification types (using django-notification) -- tie to syncdb

def create_notice_types(app, created_models, verbosity, **kwargs):
    notification.create_notice_type("comment_on_commented", _("Comment on Commented Work"), _("A comment has been received on a book that you've commented on."))
    notification.create_notice_type("wishlist_comment", _("Wishlist Comment"), _("A comment has been received on one of your wishlist books."), default = 1)
    notification.create_notice_type("wishlist_work_claimed", _("Rights Holder is Active"), _("A rights holder has shown up for a book that you want unglued."), default = 1)
    notification.create_notice_type("wishlist_active", _("New Campaign"), _("A book you've wishlisted has a newly launched campaign."))
    notification.create_notice_type("wishlist_near_target", _("Campaign Near Target"), _("A book you want is near its ungluing target."))
    notification.create_notice_type("wishlist_near_deadline", _("Campaign Near Deadline"), _("A book you want is almost out of time."))
    notification.create_notice_type("wishlist_premium_limited_supply", _("Only a Few Premiums Left"), _("A limited edition premium is running out on a book you like."))
    notification.create_notice_type("wishlist_successful", _("Successful Campaign"), _("An ungluing campaign that you have supported or followed has succeeded."))
    notification.create_notice_type("wishlist_unsuccessful", _("Unsuccessful Campaign"), _("An ungluing campaign that you supported didn't succeed this time."))
    notification.create_notice_type("wishlist_updated", _("Campaign Updated"), _("An ungluing campaign you support has been updated."), default = 1)
    notification.create_notice_type("wishlist_message", _("Campaign Communication"), _("There's a message about an ungluing campaign you're interested in."))
    notification.create_notice_type("wishlist_price_drop", _("Campaign Price Drop"), _("An ungluing campaign you're interested in has a reduced target."), default = 1)
    notification.create_notice_type("wishlist_unglued_book_released", _("Unglued Book!"), _("A book you wanted is now available to be downloaded.'"))
    notification.create_notice_type("pledge_you_have_pledged", _("Thanks For Your Pledge!"), _("Your ungluing pledge has been entered."))
    notification.create_notice_type("pledge_status_change", _("Your Pledge Has Been Modified"), _("Your ungluing plegde has been modified."))
    notification.create_notice_type("pledge_charged", _("Your Pledge has been Executed"), _("You have contributed to a successful ungluing campaign."))
    notification.create_notice_type("rights_holder_created", _("Agreement Accepted"), _("You become a verified Unglue.it rights holder."))
    notification.create_notice_type("rights_holder_claim_approved", _("Claim Accepted"), _("A claim you've entered has been accepted."))
    
signals.post_syncdb.connect(create_notice_types, sender=notification)

# define the notifications and tie them to corresponding signals

from django.contrib.comments.signals import comment_was_posted


def notify_comment(comment, request, **kwargs):
    logger.info('comment %s notifying' % comment.pk)
    other_commenters = User.objects.filter(comment_comments__content_type=comment.content_type, comment_comments__object_pk=comment.object_pk).distinct().exclude(id=comment.user.id)
    other_wishers = comment.content_object.wished_by().exclude(id=comment.user.id).exclude(id__in=other_commenters)
    notification.queue(other_commenters, "comment_on_commented", {'comment':comment}, True)
    notification.queue(other_wishers, "wishlist_comment", {'comment':comment}, True)
    from regluit.core.tasks import emit_notifications
    emit_notifications.delay()

comment_was_posted.connect(notify_comment)

# Successful campaign signal
# https://code.djangoproject.com/browser/django/tags/releases/1.3.1/django/db/models/signals.py

successful_campaign = Signal(providing_args=["campaign"])

def notify_successful_campaign(campaign, **kwargs):
    """send notification in response to successful campaign"""
    logger.info('received successful_campaign signal for {0}'.format(campaign))
    # supporters and staff -- though it might be annoying for staff to be getting all these notices!
    staff = User.objects.filter(is_staff=True)
    supporters = (User.objects.get(id=k) for k in campaign.supporters())
    
    site = Site.objects.get_current()
    notification.queue(itertools.chain(staff, supporters), "wishlist_successful", {'campaign':campaign, 'site':site}, True)
    from regluit.core.tasks import emit_notifications
    emit_notifications.delay()
    
# successful_campaign -> send notices    
successful_campaign.connect(notify_successful_campaign)