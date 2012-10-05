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
    notification.create_notice_type("wishlist_unsuccessful_amazon", _("Campaign shut down"), _("An ungluing campaign that you supported had to be shut down due to an Amazon Payments policy change."))
    notification.create_notice_type("pledge_donation_credit", _("Donation Credit Balance"), _("You have a donation credit balance"))
    notification.create_notice_type("new_wisher", _("New wisher"), _("Someone new has wished for a book that you're the rightsholder for"))
    
signals.post_syncdb.connect(create_notice_types, sender=notification)

# define the notifications and tie them to corresponding signals

from django.contrib.comments.signals import comment_was_posted

def notify_comment(comment, request, **kwargs):
    logger.info('comment %s notifying' % comment.pk)
    other_commenters = User.objects.filter(comment_comments__content_type=comment.content_type, comment_comments__object_pk=comment.object_pk).distinct().exclude(id=comment.user.id)
    other_wishers = comment.content_object.wished_by().exclude(id=comment.user.id).exclude(id__in=other_commenters)
    domain = Site.objects.get_current().domain
    if comment.content_object.last_campaign() and comment.user in comment.content_object.last_campaign().managers.all():
        #official
        notification.queue(other_wishers, "wishlist_official_comment", {'comment':comment, 'domain':domain}, True)
    else:
        notification.queue(other_commenters, "comment_on_commented", {'comment':comment, 'domain':domain}, True)
        notification.queue(other_wishers, "wishlist_comment", {'comment':comment, 'domain':domain}, True)
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

unsuccessful_campaign = Signal(providing_args=["campaign"])

def notify_unsuccessful_campaign(campaign, **kwargs):
    """send notification in response to unsuccessful campaign"""
    logger.info('received unsuccessful_campaign signal for {0}'.format(campaign))
    # supporters and staff -- though it might be annoying for staff to be getting all these notices!
    staff = User.objects.filter(is_staff=True)
    supporters = (User.objects.get(id=k) for k in campaign.supporters())
    
    site = Site.objects.get_current()
    notification.queue(itertools.chain(staff, supporters), "wishlist_unsuccessful", {'campaign':campaign, 'site':site}, True)
    from regluit.core.tasks import emit_notifications
    emit_notifications.delay()
    
# unsuccessful_campaign -> send notices    
unsuccessful_campaign.connect(notify_unsuccessful_campaign)

def handle_transaction_charged(sender,transaction=None, **kwargs):
    if transaction==None:
        return
    notification.queue([transaction.user], "pledge_charged", {
            'site':Site.objects.get_current(),
            'transaction':transaction
        }, True)
    from regluit.core.tasks import emit_notifications
    emit_notifications.delay()

transaction_charged.connect(handle_transaction_charged)

def handle_pledge_modified(sender, transaction=None, up_or_down=None, **kwargs):
    # we need to know if pledges were modified up or down because Amazon handles the
    # transactions in different ways, resulting in different user-visible behavior;
    # we need to set expectations appropriately
    # up_or_down is 'increased', 'decreased', or 'canceled'
    if transaction==None or up_or_down==None:
        return
    if up_or_down == 'canceled':
        transaction.user.profile.reset_pledge_badge()
    notification.queue([transaction.user], "pledge_status_change", {
            'site':Site.objects.get_current(),
            'transaction': transaction,
            'up_or_down': up_or_down
        }, True)
    from regluit.core.tasks import emit_notifications
    emit_notifications.delay()

pledge_modified.connect(handle_pledge_modified)

def handle_you_have_pledged(sender, transaction=None, **kwargs):
    if transaction==None:
        return
        
    #give user a badge
    if not transaction.anonymous:
        transaction.user.profile.reset_pledge_badge()
    
    notification.queue([transaction.user], "pledge_you_have_pledged", {
            'site':Site.objects.get_current(),
            'transaction': transaction
    }, True)
    from regluit.core.tasks import emit_notifications
    emit_notifications.delay()
    
pledge_created.connect(handle_you_have_pledged)

amazon_suspension = Signal(providing_args=["campaign"])

def handle_wishlist_unsuccessful_amazon(campaign, **kwargs):
    """send notification in response to campaign shutdown following Amazon suspension"""
    logger.info('received amazon_suspension signal for {0}'.format(campaign))
    # supporters and staff -- though it might be annoying for staff to be getting all these notices!
    staff = User.objects.filter(is_staff=True)
    supporters = (User.objects.get(id=k) for k in campaign.supporters())
    
    site = Site.objects.get_current()
    notification.queue(itertools.chain(staff, supporters), "wishlist_unsuccessful_amazon", {'campaign':campaign, 'site':site}, True)
    from regluit.core.tasks import emit_notifications
    emit_notifications.delay()
    
amazon_suspension.connect(handle_wishlist_unsuccessful_amazon)

wishlist_added = Signal(providing_args=["supporter", "work"])

def handle_wishlist_added(supporter, work, **kwargs):
    """send notification to confirmed rights holder when someone wishes for their work"""
    claim = work.claim.filter(status="active")
    if claim:
        notification.queue([claim[0].user], "new_wisher", {
            'supporter': supporter,
            'work': work,
            'base_url': settings.BASE_URL,
        }, True)
        
        from regluit.core.tasks import emit_notifications
        emit_notifications.delay()
		
wishlist_added.connect(handle_wishlist_added)
