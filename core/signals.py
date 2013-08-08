"""
external library imports
"""
import datetime
import itertools
import logging

from tastypie.models import create_api_key

"""
django imports
"""
import django.dispatch
import registration.signals

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db.models import get_model, signals
from django.db.models.signals import post_save
from django.db.utils import DatabaseError
from django.dispatch import Signal
from django.utils.translation import ugettext_noop as _

from notification import models as notification
from social_auth.signals import pre_update
from social_auth.backends.facebook import FacebookBackend

"""
regluit imports
"""
from regluit.payment.signals import transaction_charged, transaction_failed, pledge_modified, pledge_created
from regluit.utils.localdatetime import now

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
    # don't create Wishlist or UserProfile if we are loading fixtures http://stackoverflow.com/a/3500009/7782
    if not kwargs.get('raw', False):
        try:
            Wishlist = get_model('core', 'Wishlist')
            UserProfile = get_model('core', 'UserProfile')
            if created:
                Wishlist.objects.create(user=instance)
                profile = UserProfile.objects.create(user=instance)
                profile.ml_subscribe()
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
    notification.create_notice_type("wishlist_official_comment", _("Wishlist Comment"), _("The author or publisher, or and Unglue.it staffer, has commented on one of your wishlist books."))
    notification.create_notice_type("wishlist_work_claimed", _("Rights Holder is Active"), _("A rights holder has shown up for a book that you want unglued."), default = 1)
    notification.create_notice_type("wishlist_active", _("New Campaign"), _("A book you've wishlisted has a newly launched campaign."))
    notification.create_notice_type("wishlist_near_target", _("Campaign Near Target"), _("A book you want is near its ungluing target."))
    notification.create_notice_type("wishlist_near_deadline", _("Campaign Near Deadline"), _("A book you want is almost out of time."))
    notification.create_notice_type("wishlist_premium_limited_supply", _("Only a Few Premiums Left"), _("A limited edition premium is running out on a book you like."))
    notification.create_notice_type("wishlist_successful", _("Successful Campaign"), _("An ungluing campaign that you have supported or followed has succeeded."))
    notification.create_notice_type("wishlist_unsuccessful", _("Unsuccessful Campaign"), _("An ungluing campaign that you supported didn't succeed this time."))
    notification.create_notice_type("wishlist_updated", _("Campaign Updated"), _("An ungluing campaign you support has been updated."), default = 1)
    notification.create_notice_type("wishlist_message", _("Campaign Communication"), _("You have a private message from unglue.it staff or the rights holder about a book on your wishlist."))
    notification.create_notice_type("wishlist_price_drop", _("Campaign Price Drop"), _("An ungluing campaign you're interested in has a reduced target."), default = 1)
    notification.create_notice_type("wishlist_unglued_book_released", _("Unglued Book!"), _("A book you wanted is now available to be downloaded."))
    notification.create_notice_type("pledge_you_have_pledged", _("Thanks For Your Pledge!"), _("Your ungluing pledge has been entered."))
    notification.create_notice_type("pledge_status_change", _("Your Pledge Has Been Modified"), _("Your ungluing pledge has been modified."))
    notification.create_notice_type("pledge_charged", _("Your Pledge has been Executed"), _("You have contributed to a successful ungluing campaign."))
    notification.create_notice_type("pledge_failed", _("Unable to charge your credit card"), _("A charge to your credit card did not go through."))
    notification.create_notice_type("rights_holder_created", _("Agreement Accepted"), _("You have become a verified Unglue.it rights holder."))
    notification.create_notice_type("rights_holder_claim_approved", _("Claim Accepted"), _("A claim you've entered has been accepted."))
    notification.create_notice_type("wishlist_unsuccessful_amazon", _("Campaign shut down"), _("An ungluing campaign that you supported had to be shut down due to an Amazon Payments policy change."))
    notification.create_notice_type("pledge_donation_credit", _("Donation Credit Balance"), _("You have a donation credit balance"))
    notification.create_notice_type("new_wisher", _("New wisher"), _("Someone new has wished for a book that you're the rightsholder for"))
    notification.create_notice_type("account_expiring", _("Credit Card Expiring Soon"), _("Your credit card is about to expire."))
    notification.create_notice_type("account_expired", _("Credit Card Has Expired"), _("Your credit card has expired."))
    notification.create_notice_type("account_active", _("Credit Card Number Updated"), _("Payment method updated."), default = 1)
    
signals.post_syncdb.connect(create_notice_types, sender=notification)

# define the notifications and tie them to corresponding signals

from django.contrib.comments.signals import comment_was_posted

def notify_comment(comment, request, **kwargs):
    logger.info('comment %s notifying' % comment.pk)
    other_commenters = User.objects.filter(comment_comments__content_type=comment.content_type, comment_comments__object_pk=comment.object_pk).distinct().exclude(id=comment.user.id)
    all_wishers = comment.content_object.wished_by().exclude(id=comment.user.id)
    other_wishers = all_wishers.exclude(id__in=other_commenters)
    domain = Site.objects.get_current().domain
    if comment.content_object.last_campaign() and comment.user in comment.content_object.last_campaign().managers.all():
        #official
        notification.queue(all_wishers, "wishlist_official_comment", {'comment':comment, 'domain':domain}, True)
    else:
        notification.send(other_commenters, "comment_on_commented", {'comment':comment}, True, sender=comment.user)
        notification.send(other_wishers, "wishlist_comment", {'comment':comment}, True, sender=comment.user)
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
    
    notification.send(itertools.chain(staff, supporters), "wishlist_successful", {'campaign':campaign}, True)
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
    
    notification.send(itertools.chain(staff, supporters), "wishlist_unsuccessful", {'campaign':campaign}, True)
    from regluit.core.tasks import emit_notifications
    emit_notifications.delay()
    
# unsuccessful_campaign -> send notices    
unsuccessful_campaign.connect(notify_unsuccessful_campaign)

def handle_transaction_charged(sender,transaction=None, **kwargs):
    if transaction==None:
        return
    notification.send([transaction.user], "pledge_charged", {'transaction':transaction}, True)
    from regluit.core.tasks import emit_notifications
    emit_notifications.delay()

transaction_charged.connect(handle_transaction_charged)

# dealing with failed transactions

def handle_transaction_failed(sender,transaction=None, **kwargs):
    if transaction is None:
        return
    
    # window for recharging
    recharge_deadline = transaction.campaign.deadline + datetime.timedelta(settings.RECHARGE_WINDOW)
    
    notification.send([transaction.user], "pledge_failed", {
            'transaction':transaction,
            'recharge_deadline': recharge_deadline
        }, True)
    from regluit.core.tasks import emit_notifications
    emit_notifications.delay()

transaction_failed.connect(handle_transaction_failed)


def handle_pledge_modified(sender, transaction=None, up_or_down=None, **kwargs):
    # we need to know if pledges were modified up or down because Amazon handles the
    # transactions in different ways, resulting in different user-visible behavior;
    # we need to set expectations appropriately
    # up_or_down is 'increased', 'decreased', or 'canceled'
    if transaction==None or up_or_down==None:
        return
    if up_or_down == 'canceled':
        transaction.user.profile.reset_pledge_badge()
    notification.send([transaction.user], "pledge_status_change", {
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
    
    notification.send([transaction.user], "pledge_you_have_pledged", {
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
    
    notification.send(itertools.chain(staff, supporters), "wishlist_unsuccessful_amazon", {'campaign':campaign}, True)
    from regluit.core.tasks import emit_notifications
    emit_notifications.delay()
    
amazon_suspension.connect(handle_wishlist_unsuccessful_amazon)

wishlist_added = Signal(providing_args=["supporter", "work"])

def handle_wishlist_added(supporter, work, **kwargs):
    """send notification to confirmed rights holder when someone wishes for their work"""
    claim = work.claim.filter(status="active")
    if claim:
        notification.send([claim[0].user], "new_wisher", {
            'supporter': supporter,
            'work': work,
            'base_url': settings.BASE_URL_SECURE,
        }, True)
        
        from regluit.core.tasks import emit_notifications
        emit_notifications.delay()
		
wishlist_added.connect(handle_wishlist_added)

deadline_impending = Signal(providing_args=["campaign"])

def handle_wishlist_near_deadline(campaign, **kwargs):
    """
    send two groups - one the nonpledgers, one the pledgers
    set the pledged flag differently in the context
    """
    pledgers = campaign.ungluers()['all']
    nonpledgers = campaign.work.wished_by().exclude(id__in=[p.id for p in pledgers])
    
    notification.send(pledgers, "wishlist_near_deadline", {
            'campaign': campaign,
            'domain': settings.BASE_URL_SECURE,
            'pledged': True,
    }, True)
    
    notification.send(nonpledgers, "wishlist_near_deadline", {
            'campaign': campaign,
            'domain': settings.BASE_URL_SECURE,
            'pledged': False,
    }, True)

    from regluit.core.tasks import emit_notifications
    emit_notifications.delay()
    
deadline_impending.connect(handle_wishlist_near_deadline)

supporter_message = Signal(providing_args=["supporter", "work", "msg"])

def notify_supporter_message(sender, work, supporter, msg, **kwargs):
    """send notification in of supporter message"""
    logger.info('received supporter_message signal for {0}'.format(supporter))
    
    site = Site.objects.get_current()
    notification.send( [supporter], "wishlist_message", {'work':work, 'msg':msg}, True, sender)
    from regluit.core.tasks import emit_notifications
    emit_notifications.delay()
    
supporter_message.connect(notify_supporter_message)
