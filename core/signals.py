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

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db.models import signals
from django.db.models.signals import post_save
from django.db.utils import DatabaseError
from django.dispatch import Signal
from django.utils.translation import ugettext_noop as _
from django.template.loader import render_to_string
from django.utils.timezone import now

from notification import models as notification
from registration.signals import user_activated

"""
regluit imports
"""
from regluit.payment.signals import transaction_charged, transaction_failed, pledge_modified, pledge_created
from regluit.core.parameters import REWARDS, BUY2UNGLUE, THANKS, LIBRARY, RESERVE, THANKED
from regluit.libraryauth.models import Library, LibraryUser
from regluit.utils.localdatetime import date_today

logger = logging.getLogger(__name__)


# create Wishlist and UserProfile to associate with User
def create_user_objects(sender, created, instance, **kwargs):
    # use get_model to avoid circular import problem with models
    # don't create Wishlist or UserProfile if we are loading fixtures https://stackoverflow.com/a/3500009/7782
    if not kwargs.get('raw', False):
        try:
            Wishlist = apps.get_model('core', 'Wishlist')
            UserProfile = apps.get_model('core', 'UserProfile')
            if created:
                Wishlist.objects.create(user=instance)
                profile = UserProfile.objects.create(user=instance)
                if instance.social_auth.exists():
                    instance.profile.ml_subscribe()
        except DatabaseError:
            # this can happen when creating superuser during syncdb since the
            # core_wishlist table doesn't exist yet
            return

post_save.connect(create_user_objects, sender=User)


# create API key for new User
post_save.connect(create_api_key, sender=User)


# create notification types (using django-notification) -- tie to syncdb

def create_notice_types( **kwargs):
    notification.create_notice_type("comment_on_commented", _("Comment on Commented Work"), _("A comment has been received on a book that you've commented on."))
    notification.create_notice_type("wishlist_comment", _("Book List Comment"), _("A comment has been received on one of your books."), default = 1)
    notification.create_notice_type("wishlist_official_comment", _("Book List Comment"), _("The author or publisher, or and Unglue.it staffer, has commented on one of your faves."))
    notification.create_notice_type("wishlist_work_claimed", _("Rights Holder is Active"), _("A rights holder has shown up for a book that you've faved."), default = 1)
    notification.create_notice_type("wishlist_active", _("New Campaign"), _("A book you've favorited has a newly launched campaign."))
    notification.create_notice_type("wishlist_near_target", _("Campaign Near Target"), _("A book you want is near its ungluing target."))
    notification.create_notice_type("wishlist_near_deadline", _("Campaign Near Deadline"), _("A book you want is almost out of time."))
    notification.create_notice_type("wishlist_premium_limited_supply", _("Only a Few Premiums Left"), _("A limited edition premium is running out on a book you've faved."))
    notification.create_notice_type("wishlist_successful", _("Successful Campaign"), _("An ungluing campaign that you have supported or faved has succeeded."))
    notification.create_notice_type("wishlist_unsuccessful", _("Unsuccessful Campaign"), _("An ungluing campaign that you supported didn't succeed this time."))
    notification.create_notice_type("wishlist_updated", _("Campaign Updated"), _("An ungluing campaign you support has been updated."), default = 1)
    notification.create_notice_type("wishlist_message", _("Campaign Communication"), _("You have a private message from unglue.it staff or the rights holder about a book you've faved."))
    notification.create_notice_type("wishlist_price_drop", _("Campaign Price Drop"), _("An ungluing campaign you've faved has a reduced target."), default = 1)
    notification.create_notice_type("wishlist_unglued_book_released", _("Unglued Book!"), _("A book you've faved is now available to be downloaded."))
    notification.create_notice_type("pledge_you_have_pledged", _("Thanks For Your Pledge!"), _("Your ungluing pledge has been entered."))
    notification.create_notice_type("pledge_status_change", _("Your Pledge Has Been Modified"), _("Your ungluing pledge has been modified."))
    notification.create_notice_type("pledge_charged", _("Your Pledge has been Executed"), _("You have contributed to a successful ungluing campaign."))
    notification.create_notice_type("pledge_failed", _("Unable to charge your credit card"), _("A charge to your credit card did not go through."))
    notification.create_notice_type("rights_holder_created", _("Agreement Accepted"), _("You have applied to become an Unglue.it rights holder."))
    notification.create_notice_type("rights_holder_accepted", _("Agreement Accepted"), _("You have become a verified Unglue.it rights holder."))
    notification.create_notice_type("rights_holder_claim", _("Claim Entered"), _("A claim has been entered."))
    notification.create_notice_type("wishlist_unsuccessful_amazon", _("Campaign shut down"), _("An ungluing campaign that you supported had to be shut down due to an Amazon Payments policy change."))
    notification.create_notice_type("pledge_gift_credit", _("Credit Balance"), _("You have a credit balance"))
    notification.create_notice_type("new_wisher", _("New wisher"), _("Someone new has faved a book that you're the rightsholder for"))
    notification.create_notice_type("account_expiring", _("Credit Card Expiring Soon"), _("Your credit card is about to expire."))
    notification.create_notice_type("account_expired", _("Credit Card Has Expired"), _("Your credit card has expired."))
    notification.create_notice_type("account_active", _("Credit Card Number Updated"), _("Payment method updated."), default = 1)
    notification.create_notice_type("purchase_complete", _("Your Purchase is Complete"), _("Your Unglue.it Purchase is Complete."))
    notification.create_notice_type("library_borrow", _("Library eBook Borrowed."), _("You've borrowed an ebook through a Library participating in Unglue.it"))
    notification.create_notice_type("library_reserve", _("Library eBook Reserved."), _("An ebook you've reserved is available."))
    notification.create_notice_type("library_join", _("New Library User."), _("A library participating in Unglue.it has added a user"))
    notification.create_notice_type("purchase_gift", _("You have a gift."), _("An ungluer has given you an ebook."))
    notification.create_notice_type("purchase_got_gift", _("Your gift was received."), _("The ebook you sent as a gift has been redeemed."))
    notification.create_notice_type("purchase_gift_waiting", _("Your gift is waiting."), _("Please claim your ebook."))
    notification.create_notice_type("purchase_notgot_gift", _("Your gift wasn't received."), _("The ebook you sent as a gift has not yet been redeemed."))
    notification.create_notice_type("donation", _("Your donation was processed."), _("Thank you, your generous donation has been processed."))
    
signals.post_migrate.connect(create_notice_types, sender=notification)

# define the notifications and tie them to corresponding signals

from django_comments.signals import comment_was_posted

def notify_comment(comment, request, **kwargs):
    logger.info('comment %s notifying' % comment.pk)
    other_commenters = User.objects.filter(comment_comments__content_type=comment.content_type, comment_comments__object_pk=comment.object_pk).distinct().exclude(id=comment.user_id)
    all_wishers = comment.content_object.wished_by().exclude(id=comment.user_id)
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
    transaction._current_total = None
    context = {'transaction':transaction,'current_site':Site.objects.get_current()}
    if not transaction.campaign:
        if transaction.user:
            notification.send([transaction.user], "donation", context, True)
        elif transaction.receipt:
            from regluit.core.tasks import send_mail_task
            message = render_to_string("notification/donation/full.txt", context )
            send_mail_task.delay('unglue.it donation confirmation', message, 'notices@gluejar.com', [transaction.receipt])
    elif transaction.campaign.type is REWARDS:
        notification.send([transaction.user], "pledge_charged", context, True)
    elif transaction.campaign.type is BUY2UNGLUE:
        # provision the book
        Acq = apps.get_model('core', 'Acq')
        if transaction.offer.license == LIBRARY:
            library = Library.objects.get(id=transaction.extra['library_id'])
            new_acq = Acq.objects.create(user=library.user,work=transaction.campaign.work,license= LIBRARY)
            if transaction.user_id != library.user_id:  # don't put it on reserve if purchased by the library
                reserve_acq =  Acq.objects.create(user=transaction.user,work=transaction.campaign.work,license= RESERVE, lib_acq = new_acq)
                reserve_acq.expire_in(datetime.timedelta(hours=2))
            copies = int(transaction.extra.get('copies',1))
            while copies > 1:
                Acq.objects.create(user=library.user,work=transaction.campaign.work,license= LIBRARY)
                copies -= 1
        else:
            if transaction.extra.get('give_to', False):
                # it's a gift!
                Gift = apps.get_model('core', 'Gift')
                giftee = Gift.giftee(transaction.extra['give_to'], str(transaction.id))
                new_acq = Acq.objects.create(user=giftee, work=transaction.campaign.work, license= transaction.offer.license)
                gift = Gift.objects.create(acq=new_acq, message=transaction.extra.get('give_message',''), giver=transaction.user , to = transaction.extra['give_to'])
                context['gift'] = gift
                notification.send([giftee], "purchase_gift", context, True)
            else:
                new_acq = Acq.objects.create(user=transaction.user,work=transaction.campaign.work,license= transaction.offer.license)
        transaction.campaign.update_left()
        notification.send([transaction.user], "purchase_complete", context, True)
        from regluit.core.tasks import watermark_acq
        watermark_acq.delay(new_acq)
        if transaction.campaign.cc_date < date_today() :
            transaction.campaign.update_status(send_notice=True)
    elif transaction.campaign.type is THANKS:
        if transaction.user:
            Acq = apps.get_model('core', 'Acq')
            new_acq = Acq.objects.create(user=transaction.user, work=transaction.campaign.work, license=THANKED)
            notification.send([transaction.user], "purchase_complete", context, True)
        elif transaction.receipt:
            from regluit.core.tasks import send_mail_task
            message = render_to_string("notification/purchase_complete/full.txt", context )
            send_mail_task.delay('unglue.it transaction confirmation', message, 'notices@gluejar.com', [transaction.receipt])
    from regluit.core.tasks import emit_notifications
    emit_notifications.delay()

transaction_charged.connect(handle_transaction_charged)

# dealing with failed transactions

def handle_transaction_failed(sender,transaction=None, **kwargs):
    if transaction is None or transaction.campaign == None or transaction.campaign.type == THANKS:
        # no need to nag a failed THANKS or DONATION transaction
        return
    
    # window for recharging
    recharge_deadline =  transaction.deadline_or_now + datetime.timedelta(settings.RECHARGE_WINDOW)
    
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
    
    notification.send( [supporter], "wishlist_message", {'work':work, 'msg':msg}, True, sender)
    from regluit.core.tasks import emit_notifications
    emit_notifications.delay()
    
supporter_message.connect(notify_supporter_message)

def notify_join_library(sender, created, instance, **kwargs):
    if created:
        notification.send((instance.user, instance.library.user), "library_join", {
            'library': instance.library,
            'user': instance.user,
            })

post_save.connect(notify_join_library, sender=LibraryUser)

from registration.signals import user_activated

def ml_subscribe(user, request, **kwargs):
    user.profile.ml_subscribe()
    
user_activated.connect(ml_subscribe)