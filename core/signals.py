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

from regluit.payment.signals import transaction_charged, pledge_modified, pledge_created

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

def handle_same_email_account(sender, user, **kwargs):
    logger.info('checking %s' % user.username)
    old_users=User.objects.exclude(id=user.id).filter(email=user.email)
    for old_user in old_users:
        # decide why there's a previous user with this email
        if not old_user.is_active:
            # never activated
            old_user.delete()
        elif old_user.date_joined < user.date_joined:
            # attach to old account 
            old_user.username=user.username
            old_user.password=user.password
            user.delete()
            old_user.save()
            user=old_user
        else: 
            # shouldn't happen; don't want to delete the user in case the user is being used for something
            old_user.email= '%s.unglue.it'% old_user.email
            
registration.signals.user_activated.connect(handle_same_email_account)

# create notification types (using django-notification) -- tie to syncdb

def create_notice_types(app, created_models, verbosity, **kwargs):
    notification.create_notice_type("comment_on_commented", _("Comment on Commented Work"), _("A comment has been received on a book that you've commented on."))
    notification.create_notice_type("wishlist_comment", _("Wishlist Comment"), _("A comment has been received on one of your wishlist books."), default = 1)
    notification.create_notice_type("wishlist_official_comment", _("Wishlist Comment"), _("An official comment has been received on one of your wishlist books."))
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
    notification.create_notice_type("wishlist_unglued_book_released", _("Unglued Book!"), _("A book you wanted is now available to be downloaded."))
    notification.create_notice_type("pledge_you_have_pledged", _("Thanks For Your Pledge!"), _("Your ungluing pledge has been entered."))
    notification.create_notice_type("pledge_status_change", _("Your Pledge Has Been Modified"), _("Your ungluing pledge has been modified."))
    notification.create_notice_type("pledge_charged", _("Your Pledge has been Executed"), _("You have contributed to a successful ungluing campaign."))
    notification.create_notice_type("rights_holder_created", _("Agreement Accepted"), _("You have become a verified Unglue.it rights holder."))
    notification.create_notice_type("rights_holder_claim_approved", _("Claim Accepted"), _("A claim you've entered has been accepted."))
    
signals.post_syncdb.connect(create_notice_types, sender=notification)

# define the notifications and tie them to corresponding signals

from django.contrib.comments.signals import comment_was_posted


def notify_comment(comment, request, **kwargs):
    logger.info('comment %s notifying' % comment.pk)
    other_commenters = User.objects.filter(comment_comments__content_type=comment.content_type, comment_comments__object_pk=comment.object_pk).distinct().exclude(id=comment.user.id)
    other_wishers = comment.content_object.wished_by().exclude(id=comment.user.id).exclude(id__in=other_commenters)
    if comment.content_object.last_campaign() and comment.user in comment.content_object.last_campaign().managers.all():
        #official
        notification.queue(other_wishers, "wishlist_official_comment", {'comment':comment}, True)
    else:
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


def handle_transaction_charged(sender,transaction=None, **kwargs):
    if transaction==None:
        return
    notification.queue([transaction.user], "pledge_charged", {
            'site':Site.objects.get_current(),
            'transaction':transaction,
            'payment_processor':settings.PAYMENT_PROCESSOR
        }, True)
    from regluit.core.tasks import emit_notifications
    emit_notifications.delay()

transaction_charged.connect(handle_transaction_charged)

def handle_pledge_modified(sender, transaction=None, status=None, **kwargs):
    if transaction==None or status==None:
        return
    notification.queue([transaction.user], "pledge_status_change", {
            'site':Site.objects.get_current(),
            'transaction': transaction,
            'payment_processor':settings.PAYMENT_PROCESSOR,
            'status': status
        }, True)
    from regluit.core.tasks import emit_notifications
    emit_notifications.delay()

pledge_modified.connect(handle_pledge_modified)

def handle_you_have_pledged(sender, transaction=None, **kwargs):
    if transaction==None:
        return
    notification.queue([transaction.user], "pledge_you_have_pledged", {
            'site':Site.objects.get_current(),
            'transaction': transaction,
            'campaign': transaction.campaign,
            'work': transaction.campaign.work,
            'payment_processor':settings.PAYMENT_PROCESSOR,
    }, True)
    from regluit.core.tasks import emit_notifications
    emit_notifications.delay()
    
pledge_created.connect(handle_you_have_pledged)

# The notification templates need some context; I'm making a note of that here
# This can be removed as the relevant functions are written
# PLEDGE_CHANGE_STATUS:
#	'site': (site)
#	'campaign'
#	'amount': (amount supporter's card will be charged)
#	'premium': (premium requested by the supporter)
# RIGHTS_HOLDER_CLAIM_APPROVED:
#	'site': (site)
#	'claim': (claim)
# RIGHTS_HOLDER_CREATED: (no context needed)
# note -- it might be that wishlist_near_target and wishlist_near_deadline would
# both be triggered at about the same time -- do we want to prevent supporters
# from getting both within a small time frame? if so which supersedes?
# WISHLIST_NEAR_DEADLINE:
#	'site': (site)
#	'campaign': (the campaign)
#	'pledged': (true if the supporter has pledged, false otherwise)
#	'amount': (amount the supporter has pledged; only needed if pledged is true)
# WISHLIST_NEAR_TARGET:
#	'site': (site)
#	'campaign': (the campaign)
#	'pledged': (true if the supporter has pledged, false otherwise)
#	'amount': (amount the supporter has pledged; only needed if pledged is true)
# WISHLIST_PREMIUM_LIMITED_SUPPLY:
# (note we should not send this to people who have already claimed this premium)
# should we only send this to people who haven't pledged at all, or whose pledge 
# is smaller than the amount of this premium? (don't want to encourage people to
# lower their pledge)
# the text assumes there is only 1 left -- if we're going to send at some other 
# threshhold this will need to be revised
#	'campaign': (campaign)
#	'premium': (the premium in question)
#	'site': (site)
# WISHLIST_PRICE_DROP:
#	'campaign'
#	'pledged': (true if recipient has pledged to campaign, otherwise false)
#	'amount': (amount recipient has pledged, only needed if pledged=True)
#	'site'
# WISHLIST_SUCCESSFUL:
#	'pledged'
#	'campaign'
#	'site'
# WISHLIST_UNSUCCESSFUL:
#	'campaign'
#	'site'
# WISHLIST_UPDATED:
# I'd like to provide the actual text of the update in the message but I don't think
# we can reasonably do that, since campaign.description may contain HTML and we are
# sending notifications in plaintext.  If we can send the update information in the
# email, though, let's do that.
#	'campaign'
#	'site'
# WISHLIST_WORK_CLAIMED
# does this trigger when someone claims a work, or when the claim is approved?
# I've written the text assuming it is the latter (sending notifications on the
# former seems too sausage-making, and might make people angry if they get
# notifications about claims they believe are false).  If it's the former, the
# text should be revisited.
#	'claim'
#	'site'
#	'rightsholder' (the name of the rightsholder)