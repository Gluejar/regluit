import binascii
import hashlib
import logging
import math
import random
import re
import urllib
import urllib2
from datetime import timedelta, datetime
from decimal import Decimal
from tempfile import SpooledTemporaryFile

import requests
from ckeditor.fields import RichTextField
from notification import models as notification
from postmonkey import PostMonkey, MailChimpException

#django imports
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.contenttypes.fields import GenericRelation
from django.core.urlresolvers import reverse
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import F, Q
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

#regluit imports

import regluit
import regluit.core.isbn
import regluit.core.cc as cc

from regluit.booxtream import BooXtream
from regluit.libraryauth.auth import AVATARS
from regluit.libraryauth.models import Library
from regluit.payment.parameters import (
    TRANSACTION_STATUS_ACTIVE,
    TRANSACTION_STATUS_COMPLETE,
    TRANSACTION_STATUS_CANCELED,
    TRANSACTION_STATUS_ERROR,
    TRANSACTION_STATUS_FAILED,
    TRANSACTION_STATUS_INCOMPLETE
)
from regluit.utils import crypto
from regluit.utils.localdatetime import now, date_today

from regluit.core.parameters import (
    REWARDS,
    BUY2UNGLUE,
    THANKS,
    INDIVIDUAL,
    LIBRARY,
    BORROWED,
    TESTING,
    RESERVE,
    THANKED,
    OFFER_CHOICES,
    ACQ_CHOICES,
)
from regluit.core.epub import personalize, ungluify, ask_epub
from regluit.core.pdf import ask_pdf, pdf_append
from regluit.core import mobi
from regluit.core.signals import (
    successful_campaign,
    unsuccessful_campaign,
    wishlist_added
)

watermarker = BooXtream()

from .bibmodels import (
    Author,
    Ebook,
    EbookFile,
    Edition,
    EditionNote,
    good_providers,
    Identifier,
    path_for_file,
    Publisher,
    PublisherName,
    Relation,
    Relator,
    safe_get_work,
    Subject,
    WasWork,
    Work,
    WorkRelation,
)

pm = PostMonkey(settings.MAILCHIMP_API_KEY)

logger = logging.getLogger(__name__)

class UnglueitError(RuntimeError):
    pass

class Key(models.Model):
    """an encrypted key store"""
    name = models.CharField(max_length=255, unique=True)
    encrypted_value = models.TextField(null=True, blank=True)

    def _get_value(self):
        return crypto.decrypt_string(binascii.a2b_hex(self.encrypted_value), settings.SECRET_KEY)

    def _set_value(self, value):
        self.encrypted_value = binascii.b2a_hex(crypto.encrypt_string(value, settings.SECRET_KEY))

    value = property(_get_value, _set_value)

    def __unicode__(self):
        return "Key with name {0}".format(self.name)

class CeleryTask(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    task_id = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="tasks", null=True)
    description = models.CharField(max_length=2048, null=True)  # a description of what the task is
    function_name = models.CharField(max_length=1024) # used to reconstitute the AsyncTask with which to get status
    function_args = models.IntegerField(null=True)  # not full generalized here -- takes only a single arg for now.
    active = models.NullBooleanField(default=True)

    def __unicode__(self):
        return "Task %s arg:%s ID# %s %s: State %s " % (self.function_name, self.function_args, self.task_id, self.description, self.state)

    @property
    def AsyncResult(self):
        f = getattr(regluit.core.tasks, self.function_name)
        return f.AsyncResult(self.task_id)
    @property
    def state(self):
        f = getattr(regluit.core.tasks, self.function_name)
        return f.AsyncResult(self.task_id).state
    @property
    def result(self):
        f = getattr(regluit.core.tasks, self.function_name)
        return f.AsyncResult(self.task_id).result
    @property
    def info(self):
        f = getattr(regluit.core.tasks, self.function_name)
        return f.AsyncResult(self.task_id).info

class Claim(models.Model):
    STATUSES = ((u'active', u'Claim has been accepted.'),
                (u'pending', u'Claim is pending acceptance.'),
                (u'release', u'Claim has not been accepted.'),
               )
    created = models.DateTimeField(auto_now_add=True)
    rights_holder = models.ForeignKey("RightsHolder", related_name="claim", null=False)
    work = models.ForeignKey("Work", related_name="claim", null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="claim", null=False)
    status = models.CharField(max_length=7, choices=STATUSES, default='active')

    @property
    def can_open_new(self):
        # whether a campaign can be opened for this claim

        #must be an active claim
        if self.status != 'active':
            return False
        #can't already be a campaign
        for campaign in self.campaigns:
            if campaign.status in ['ACTIVE', 'INITIALIZED']:
                return 0 # cannot open a new campaign
            if campaign.status in ['SUCCESSFUL']:
                return 2  # can open a THANKS campaign
        return 1 # can open any type of campaign

    def  __unicode__(self):
        return self.work.title

    @property
    def campaign(self):
        return self.work.last_campaign()

    @property
    def campaigns(self):
        return self.work.campaigns.all()

def notify_claim(sender, created, instance, **kwargs):
    if 'example.org' in instance.user.email or hasattr(instance, 'dont_notify'):
        return
    try:
        (rights, new_rights) = User.objects.get_or_create(email='rights@gluejar.com', defaults={'username':'RightsatUnglueit'})
    except:
        rights = None
    if instance.user == instance.rights_holder.owner:
        ul = (instance.user, rights)
    else:
        ul = (instance.user, instance.rights_holder.owner, rights)
    notification.send(ul, "rights_holder_claim", {'claim': instance,})
post_save.connect(notify_claim, sender=Claim)

class RightsHolder(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    email = models.CharField(max_length=100, blank=True)
    rights_holder_name = models.CharField(max_length=100, blank=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="rights_holder", null=False)
    can_sell = models.BooleanField(default=False)
    def __unicode__(self):
        return self.rights_holder_name

class Premium(models.Model):
    PREMIUM_TYPES = ((u'00', u'Default'), (u'CU', u'Custom'), (u'XX', u'Inactive'))
    TIERS = {"supporter":25, "patron":50, "bibliophile":100} #should load this from fixture
    created = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=2, choices=PREMIUM_TYPES)
    campaign = models.ForeignKey("Campaign", related_name="premiums", null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=0, blank=False)
    description = models.TextField(null=True, blank=False)
    limit = models.IntegerField(default=0)

    @property
    def premium_count(self):
        t_model = apps.get_model('payment', 'Transaction')
        return t_model.objects.filter(premium=self).count()
    @property
    def premium_remaining(self):
        t_model = apps.get_model('payment', 'Transaction')
        return self.limit - t_model.objects.filter(premium=self).count()
    def  __unicode__(self):
        return  (self.campaign.work.title if self.campaign else '')  + ' $' + str(self.amount)

class PledgeExtra:
    def __init__(self, premium=None, anonymous=False, ack_name='', ack_dedication='', offer=None):
        self.anonymous = anonymous
        self.premium = premium
        self.offer = offer
        self.extra = {}
        if ack_name:
            self.extra['ack_name'] = ack_name
        if ack_dedication:
            self.extra['ack_dedication'] = ack_dedication

class CampaignAction(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    # anticipated types: activated, withdrawn, suspended, restarted, succeeded, failed, unglued
    type = models.CharField(max_length=15)
    comment = models.TextField(null=True, blank=True)
    campaign = models.ForeignKey("Campaign", related_name="actions", null=False)

class Offer(models.Model):
    work = models.ForeignKey("Work", related_name="offers", null=False)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=False)
    license = models.PositiveSmallIntegerField(null=False, default=INDIVIDUAL,
                                               choices=OFFER_CHOICES)
    active = models.BooleanField(default=False)

    @property
    def days_per_copy(self):
        return Decimal(float(self.price) / self.work.last_campaign().dollar_per_day)

    @property
    def get_thanks_display(self):
        if self.license == LIBRARY:
            return 'Suggested contribution for libraries'
        else:
            return 'Suggested contribution for individuals'

class Acq(models.Model):
    """
    Short for Acquisition, this is a made-up word to describe the thing you acquire when you buy or borrow an ebook
    """

    created = models.DateTimeField(auto_now_add=True, db_index=True,)
    expires = models.DateTimeField(null=True)
    refreshes = models.DateTimeField(auto_now_add=True)
    refreshed = models.BooleanField(default=True)
    work = models.ForeignKey("Work", related_name='acqs', null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acqs')
    license = models.PositiveSmallIntegerField(null=False, default=INDIVIDUAL,
                                               choices=ACQ_CHOICES)
    watermarked = models.ForeignKey("booxtream.Boox", null=True)
    nonce = models.CharField(max_length=32, null=True)

    # when the acq is a loan, this points at the library's acq it's derived from
    lib_acq = models.ForeignKey("self", related_name="loans", null=True)

    class mock_ebook(object):
        def __init__(self, acq):
            self.url = acq.get_mobi_url()
            self.format = 'mobi'
            self.filesize = 0
        def save(self):
            # TODO how to handle filesize?
            return True

    def ebook(self):
        return self.mock_ebook(self)

    def __unicode__(self):
        if self.lib_acq:
            return "%s, %s: %s for %s" % (self.work.title, self.get_license_display(), self.lib_acq.user, self.user)
        else:
            return "%s, %s for %s" % (self.work.title, self.get_license_display(), self.user,)

    @property
    def expired(self):
        if self.expires is None:
            return False
        else:
            return self.expires < datetime.now()

    def get_mobi_url(self):
        if self.expired:
            return ''
        return self.get_watermarked().download_link_mobi

    def get_epub_url(self):
        if self.expired:
            return ''
        return self.get_watermarked().download_link_epub

    def get_watermarked(self):
        if self.watermarked is None or self.watermarked.expired:
            if self.on_reserve:
                self.borrow(self.user)
            do_watermark = self.work.last_campaign().do_watermark
            params = {
                'customeremailaddress': self.user.email if do_watermark else '',
                'customername': self.user.username if do_watermark else 'an ungluer',
                'languagecode':'1033',
                'expirydays': 1,
                'downloadlimit': 7,
                'exlibris':0,
                'chapterfooter':  0,
                'disclaimer':0,
                'referenceid': '%s:%s:%s' % (self.work.id, self.user.id, self.id) if do_watermark else 'N/A',
                'kf8mobi': True,
                'epub': True,
                }
            personalized = personalize(self.work.epubfiles()[0].file, self)
            personalized.seek(0)
            self.watermarked = watermarker.platform(epubfile=personalized, **params)
            self.save()
        return self.watermarked

    def _hash(self):
        return hashlib.md5('%s:%s:%s:%s'%(settings.SOCIAL_AUTH_TWITTER_SECRET, self.user.id, self.work.id, self.created)).hexdigest()

    def expire_in(self, delta):
        self.expires = (now() + delta) if delta else now()
        self.save()
        if self.lib_acq:
            self.lib_acq.refreshes = now() + delta
            self.lib_acq.refreshed = False
            self.lib_acq.save()

    @property
    def on_reserve(self):
        return self.license == RESERVE

    def borrow(self, user=None):
        if self.on_reserve:
            self.license = BORROWED
            self.expire_in(timedelta(days=14))
            self.user.wishlist.add_work(self.work, "borrow")
            notification.send([self.user], "library_borrow", {'acq':self})
            return self
        elif self.borrowable and user:
            user.wishlist.add_work(self.work, "borrow")
            borrowed = Acq.objects.create(user=user, work=self.work, license=BORROWED, lib_acq=self)
            from regluit.core.tasks import watermark_acq
            notification.send([user], "library_borrow", {'acq':borrowed})
            watermark_acq.delay(borrowed)
            return borrowed

    @property
    def borrowable(self):
        if self.license == RESERVE and not self.expired:
            return True
        if self.license == LIBRARY:
            return self.refreshes < datetime.now()
        else:
            return False

    @property
    def holds(self):
        return Hold.objects.filter(library__user=self.user, work=self.work).order_by('created')


def config_acq(sender, instance, created, **kwargs):
    if created:
        instance.nonce = instance._hash()
        instance.save()
        if instance.license == RESERVE:
            instance.expire_in(timedelta(hours=24))
        if instance.license == BORROWED:
            instance.expire_in(timedelta(days=14))

post_save.connect(config_acq, sender=Acq)

class Hold(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    work = models.ForeignKey("Work", related_name='holds', null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='holds', null=False)
    library = models.ForeignKey(Library, related_name='holds', null=False)

    def __unicode__(self):
        return '%s for %s at %s' % (self.work, self.user.username, self.library)
    def ahead(self):
        return Hold.objects.filter(work=self.work, library=self.library, created__lt=self.created).count()

class Campaign(models.Model):
    LICENSE_CHOICES = cc.FREECHOICES
    created = models.DateTimeField(auto_now_add=True,)
    name = models.CharField(max_length=500, null=True, blank=False)
    description = RichTextField(null=True, blank=False)
    details = RichTextField(null=True, blank=True)
    target = models.DecimalField(max_digits=14, decimal_places=2, null=True, default=0.00)
    license = models.CharField(max_length=255, choices=LICENSE_CHOICES, default='CC BY-NC-ND')
    left = models.DecimalField(max_digits=14, decimal_places=2, null=True, db_index=True,)
    deadline = models.DateTimeField(db_index=True, null=True)
    dollar_per_day = models.FloatField(null=True)
    cc_date_initial = models.DateTimeField(null=True)
    activated = models.DateTimeField(null=True, db_index=True,)
    paypal_receiver = models.CharField(max_length=100, blank=True)
    amazon_receiver = models.CharField(max_length=100, blank=True)
    work = models.ForeignKey("Work", related_name="campaigns", null=False)
    managers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="campaigns", null=False)
    # status: INITIALIZED, ACTIVE, SUSPENDED, WITHDRAWN, SUCCESSFUL, UNSUCCESSFUL
    status = models.CharField(max_length=15, null=True, blank=False, default="INITIALIZED", db_index=True,)
    type = models.PositiveSmallIntegerField(null=False, default=REWARDS,
                                            choices=((REWARDS, 'Pledge-to-unglue campaign'),
                                                     (BUY2UNGLUE, 'Buy-to-unglue campaign'),
                                                     (THANKS, 'Thanks-for-ungluing campaign'),
                                                    ))
    edition = models.ForeignKey("Edition", related_name="campaigns", null=True)
    email = models.CharField(max_length=100, blank=True)
    publisher = models.ForeignKey("Publisher", related_name="campaigns", null=True)
    do_watermark = models.BooleanField(default=True)
    use_add_ask = models.BooleanField(default=True)

    def __init__(self, *args, **kwargs):
        self.problems = []
        super(Campaign, self).__init__(*args, **kwargs)

    def __unicode__(self):
        try:
            return u"Campaign for %s" % self.work.title
        except:
            return u"Campaign %s (no associated work)" % self.name

    def clone(self):
        """use a previous UNSUCCESSFUL campaign's data as the basis for a new campaign
         assume that B2U campaigns don't need cloning
        """

        if self.clonable():
            old_managers = self.managers.all()

            # copy custom premiums
            new_premiums = self.premiums.filter(type='CU')

            # setting pk to None will insert new copy http://stackoverflow.com/a/4736172/7782
            self.pk = None
            self.status = 'INITIALIZED'

            # set deadline far in future
            # presumably RH will set deadline to proper value before campaign launched
            self.deadline = date_today() + timedelta(days=int(settings.UNGLUEIT_LONGEST_DEADLINE))

            # allow created, activated dates to be autoset by db
            self.created = None
            self.name = 'copy of %s' % self.name
            self.activated = None
            self.update_left()
            self.save()
            self.managers = old_managers

            # clone associated premiums
            for premium in new_premiums:
                premium.pk = None
                premium.created = None
                premium.campaign = self
                premium.save()
            return self
        else:
            return None

    def clonable(self):
        """campaign clonable if it's UNSUCCESSFUL and is the last campaign associated with a Work"""

        if self.status == 'UNSUCCESSFUL' and self.work.last_campaign().id == self.id:
            return True
        else:
            return False

    @property
    def launchable(self):
        may_launch = True
        try:
            if self.status != 'INITIALIZED':
                if self.status == 'ACTIVE':
                    self.problems.append(_('The campaign is already launched'))
                else:
                    self.problems.append(_('A campaign must initialized properly before it can be launched'))
                may_launch = False
            if not self.description:
                self.problems.append(_('A campaign must have a description'))
                may_launch = False
            if self.type == REWARDS:
                if self.deadline:
                    if self.deadline.date()- date_today() > timedelta(days=int(settings.UNGLUEIT_LONGEST_DEADLINE)):
                        self.problems.append(_('The chosen closing date is more than %s days from now' % settings.UNGLUEIT_LONGEST_DEADLINE))
                        may_launch = False
                else:
                    self.problems.append(_('A pledge campaign must have a closing date'))
                    may_launch = False
                if self.target:
                    if self.target < Decimal(settings.UNGLUEIT_MINIMUM_TARGET):
                        self.problems.append(_('A pledge campaign may not be launched with a target less than $%s' % settings.UNGLUEIT_MINIMUM_TARGET))
                        may_launch = False
                else:
                    self.problems.append(_('A campaign must have a target'))
                    may_launch = False
            if self.type == BUY2UNGLUE:
                if self.work.offers.filter(price__gt=0, active=True).count() == 0:
                    self.problems.append(_('You can\'t launch a buy-to-unglue campaign before setting a price for your ebooks'))
                    may_launch = False
                if EbookFile.objects.filter(edition__work=self.work).count() == 0:
                    self.problems.append(_('You can\'t launch a buy-to-unglue campaign if you don\'t have any ebook files uploaded'))
                    may_launch = False
                if (self.cc_date_initial is None) or (self.cc_date_initial > datetime.combine(settings.MAX_CC_DATE, datetime.min.time())) or (self.cc_date_initial < now()):
                    self.problems.append(_('You must set an initial Ungluing Date that is in the future and not after %s' % settings.MAX_CC_DATE))
                    may_launch = False
                if self.target:
                    if self.target < Decimal(settings.UNGLUEIT_MINIMUM_TARGET):
                        self.problems.append(_('A buy-to-unglue campaign may not be launched with a target less than $%s' % settings.UNGLUEIT_MINIMUM_TARGET))
                        may_launch = False
                else:
                    self.problems.append(_('A buy-to-unglue campaign must have a target'))
                    may_launch = False
            if self.type == THANKS:
                # the case in which there is no EbookFile and no Ebook associated with work (We have ebooks without ebook files.)
                if EbookFile.objects.filter(edition__work=self.work).count() == 0 and self.work.ebooks().count() == 0:
                    self.problems.append(_('You can\'t launch a thanks-for-ungluing campaign if you don\'t have any ebook files uploaded'))
                    may_launch = False
        except Exception as e:
            self.problems.append('Exception checking launchability ' + str(e))
            may_launch = False
        return may_launch


    def update_status(self, ignore_deadline_for_success=False, send_notice=False, process_transactions=False):
        """Updates the campaign's status. returns true if updated.
        for REWARDS:
        Computes UNSUCCESSFUL only after the deadline has passed
        Computes SUCCESSFUL only after the deadline has passed if ignore_deadline_for_success is TRUE -- otherwise looks just at amount of pledges accumulated
        by default, send_notice is False so that we have to explicitly send specify delivery of successful_campaign notice
        for BUY2UNGLUE:
        Sets SUCCESSFUL when cc_date is in the past.
        if process_transactions is True, also execute or cancel associated transactions

        """
        if not self.status == 'ACTIVE':
            return False
        elif self.type == REWARDS:
            if (ignore_deadline_for_success or self.deadline < now()) and self.current_total >= self.target:
                self.status = 'SUCCESSFUL'
                self.save()
                action = CampaignAction(campaign=self, type='succeeded', comment=self.current_total)
                action.save()

                if process_transactions:
                    p = PaymentManager()
                    results = p.execute_campaign(self)

                if send_notice:
                    successful_campaign.send(sender=None, campaign=self)

                # should be more sophisticated in whether to return True -- look at all the transactions?
                return True
            elif self.deadline < now() and self.current_total < self.target:
                self.status = 'UNSUCCESSFUL'
                self.save()
                action = CampaignAction(campaign=self, type='failed', comment=self.current_total)
                action.save()

                if process_transactions:
                    p = PaymentManager()
                    results = p.cancel_campaign(self)

                if send_notice:
                    regluit.core.signals.unsuccessful_campaign.send(sender=None, campaign=self)
                # should be more sophisticated in whether to return True -- look at all the transactions?
                return True
        elif  self.type == BUY2UNGLUE:
            if self.cc_date < date_today():
                self.status = 'SUCCESSFUL'
                self.save()
                action = CampaignAction(campaign=self, type='succeeded', comment=self.current_total)
                action.save()
                self.watermark_success()
                if send_notice:
                    successful_campaign.send(sender=None, campaign=self)

                # should be more sophisticated in whether to return True -- look at all the transactions?
                return True

        return False

    _current_total = None
    @property
    def current_total(self):
        if self._current_total is None:
            p = PaymentManager()
            self._current_total = p.query_campaign(self, summary=True, campaign_total=True)
        return self._current_total

    def set_dollar_per_day(self):
        if self.status != 'INITIALIZED' and self.dollar_per_day:
            return self.dollar_per_day
        if self.cc_date_initial is None:
            return None

        start_datetime = self.activated if self.activated else datetime.today()

        time_to_cc = self.cc_date_initial - start_datetime

        self.dollar_per_day = float(self.target)/float(time_to_cc.days)
        if self.status != 'DEMO':
            self.save()
        return self.dollar_per_day

    def set_cc_date_initial(self, a_date=settings.MAX_CC_DATE):
        self.cc_date_initial = datetime.combine(a_date, datetime.min.time())

    @property
    def cc_date(self):
        if self.type in {REWARDS, THANKS}:
            return None
        if self.dollar_per_day is None:
            return self.cc_date_initial.date()
        cc_advance_days = float(self.current_total) / self.dollar_per_day
        return (self.cc_date_initial-timedelta(days=cc_advance_days)).date()


    def update_left(self):
        self._current_total = None
        if self.type == THANKS:
            self.left = Decimal(0.00)
        elif self.type == BUY2UNGLUE:
            self.left = Decimal(self.dollar_per_day*float((self.cc_date_initial - datetime.today()).days))-self.current_total
        else:
            self.left = self.target - self.current_total
        if self.status != 'DEMO':
            self.save()

    def transactions(self, **kwargs):
        p = PaymentManager()

        # handle default parameter values
        kw = {'summary':False, 'campaign_total':True}
        kw.update(kwargs)

        return p.query_campaign(self, **kw)


    def activate(self):
        status = self.status
        if status != 'INITIALIZED':
            raise UnglueitError(_('Campaign needs to be initialized in order to be activated'))
        try:
            active_claim = self.work.claim.filter(status="active")[0]
        except IndexError, e:
            raise UnglueitError(_('Campaign needs to have an active claim in order to be activated'))
        if not self.launchable:
            raise UnglueitError('Configuration issues need to be addressed before campaign is activated: %s' % unicode(self.problems[0]))
        self.status = 'ACTIVE'
        self.left = self.target
        self.activated = datetime.today()
        if self.type == THANKS:
            # make ebooks from ebookfiles
            if self.use_add_ask:
                self.add_ask_to_ebfs()
            else:
                self.revert_asks()
            self.work.remove_old_ebooks()
        self.save()
        action = CampaignAction(campaign=self, type='activated', comment=self.get_type_display())
        ungluers = self.work.wished_by()
        notification.queue(ungluers, "wishlist_active", {'campaign':self}, True)
        return self


    def suspend(self, reason):
        status = self.status
        if status != 'ACTIVE':
            raise UnglueitError(_('Campaign needs to be active in order to be suspended'))
        action = CampaignAction(campaign=self, type='suspended', comment=reason)
        action.save()
        self.status = 'SUSPENDED'
        self.save()
        return self

    def withdraw(self, reason):
        status = self.status
        if status != 'ACTIVE':
            raise UnglueitError(_('Campaign needs to be active in order to be withdrawn'))
        action = CampaignAction(campaign=self, type='withdrawn', comment=reason)
        action.save()
        self.status = 'WITHDRAWN'
        self.save()
        return self

    def resume(self, reason):
        """Change campaign status from SUSPENDED to ACTIVE.  We may want to track reason for resuming and track history"""
        status = self.status
        if status != 'SUSPENDED':
            raise UnglueitError(_('Campaign needs to be suspended in order to be resumed'))
        if not reason:
            reason = ''
        action = CampaignAction(campaign=self, type='restarted', comment=reason)
        action.save()
        self.status = 'ACTIVE'
        self.save()
        return self

    def supporters(self):
        # expensive query used in loop; stash it
        if hasattr(self, '_translist_'):
            return self._translist_
        """nb: returns (distinct) supporter IDs, not supporter objects"""
        self._translist_ = self.transactions().filter(status=TRANSACTION_STATUS_ACTIVE).values_list('user', flat=True).distinct()
        return self._translist_

    @property
    def supporters_count(self):
        # avoid transmitting the whole list if you don't need to; let the db do the count.
        active = self.transactions().filter(status=TRANSACTION_STATUS_ACTIVE).values_list('user', flat=True).distinct().count()
        complete = self.transactions().filter(status=TRANSACTION_STATUS_COMPLETE).values_list('user', flat=True).distinct().count()
        return active+complete

    @property
    def anon_count(self):
        # avoid transmitting the whole list if you don't need to; let the db do the count.
        complete = self.transactions().filter(status=TRANSACTION_STATUS_COMPLETE, user=None).count()
        return complete

    def transaction_to_recharge(self, user):
        """given a user, return the transaction to be recharged if there is one -- None otherwise"""

        # only if a campaign is SUCCESSFUL, we allow for recharged

        if self.status == 'SUCCESSFUL':
            if self.transaction_set.filter(Q(user=user) & (Q(status=TRANSACTION_STATUS_COMPLETE) | Q(status=TRANSACTION_STATUS_ACTIVE))).count():
                # presence of an active or complete transaction means no transaction to recharge
                return None
            else:
                transactions = self.transaction_set.filter(Q(user=user) & (Q(status=TRANSACTION_STATUS_ERROR) | Q(status=TRANSACTION_STATUS_FAILED)))
                # assumption --that the first failed/errored transaction has the amount we need to recharge
                if transactions.count():
                    return transactions[0]
                else:
                    return None
        else:
            return None

    def ungluers(self):
        # expensive query used in loop; stash it
        if hasattr(self, '_ungluers_'):
            return self._ungluers_
        p = PaymentManager()
        ungluers = {"all":[], "supporters":[], "patrons":[], "bibliophiles":[]}
        if self.status == "ACTIVE":
            translist = p.query_campaign(self, summary=False, pledged=True, authorized=True)
        elif self.status == "SUCCESSFUL":
            translist = p.query_campaign(self, summary=False, pledged=True, completed=True)
        else:
            translist = []
        for transaction in translist:
            ungluers['all'].append(transaction.user)
            if not transaction.anonymous:
                if transaction.amount >= Premium.TIERS["bibliophile"]:
                    ungluers['bibliophiles'].append(transaction.user)
                elif transaction.amount >= Premium.TIERS["patron"]:
                    ungluers['patrons'].append(transaction.user)
                elif transaction.amount >= Premium.TIERS["supporter"]:
                    ungluers['supporters'].append(transaction.user)

        self._ungluers_ = ungluers
        return ungluers

    def ungluer_transactions(self):
        """
        returns a list of authorized transactions for campaigns in progress,
        or completed transactions for successful campaigns
        used to build the acks page -- because ack_name, _link, _dedication adhere to transactions,
        it's easier to return transactions than ungluers
        """
        p = PaymentManager()
        ungluers = {"all":[], "supporters":[], "anon_supporters": 0, "patrons":[], "anon_patrons": 0, "bibliophiles":[]}
        if self.status == "ACTIVE":
            translist = p.query_campaign(self, summary=False, pledged=True, authorized=True)
        elif self.status == "SUCCESSFUL":
            translist = p.query_campaign(self, summary=False, pledged=True, completed=True)
        else:
            translist = []
        for transaction in translist:
            ungluers['all'].append(transaction)
            if transaction.amount >= Premium.TIERS["bibliophile"]:
                ungluers['bibliophiles'].append(transaction)
            elif transaction.amount >= Premium.TIERS["patron"]:
                if transaction.anonymous:
                    ungluers['anon_patrons'] += 1
                else:
                    ungluers['patrons'].append(transaction)
            elif transaction.amount >= Premium.TIERS["supporter"]:
                if transaction.anonymous:
                    ungluers['anon_supporters'] += 1
                else:
                    ungluers['supporters'].append(transaction)

        return ungluers

    def effective_premiums(self):
        """returns the available premiums for the Campaign including any default premiums"""
        if self.type is BUY2UNGLUE:
            return Premium.objects.none()
        q = Q(campaign=self) | Q(campaign__isnull=True)
        return Premium.objects.filter(q).exclude(type='XX').order_by('amount')

    def custom_premiums(self):
        """returns only the active custom premiums for the Campaign"""
        if self.type is BUY2UNGLUE:
            return Premium.objects.none()
        return Premium.objects.filter(campaign=self).filter(type='CU').order_by('amount')

    @property
    def library_offer(self):
        return self._offer(LIBRARY)

    @property
    def individual_offer(self):
        return self._offer(INDIVIDUAL)

    def _offer(self, license):
        if self.type is REWARDS:
            return None
        try:
            return Offer.objects.get(work=self.work, active=True, license=license)
        except Offer.DoesNotExist:
            return None

    @property
    def ask_money(self):
    # true if there's an offer asking for money
        if self.type is REWARDS:
            return True
        try:
            Offer.objects.get(work=self.work, active=True, price__gt=0.00)
            return True
        except Offer.DoesNotExist:
            return False
        except Offer.MultipleObjectsReturned:
            return True

    @property
    def days_per_copy(self):
        if self.individual_offer:
            return Decimal(float(self.individual_offer.price) / self.dollar_per_day)
        else:
            return Decimal(0)

    @property
    def rh(self):
        """returns the rights holder for an active or initialized campaign"""
        try:
            q = Q(status='ACTIVE') | Q(status='INITIALIZED')
            rh = self.work.claim.filter(q)[0].rights_holder
            return rh
        except:
            return None
    @property
    def rightsholder(self):
        """returns the name of the rights holder for an active or initialized campaign"""
        try:
            return self.rh.rights_holder_name
        except:
            return ''

    @property
    def license_url(self):
        return cc.CCLicense.url(self.license)

    @property
    def license_badge(self):
        return cc.CCLicense.badge(self.license)

    @property
    def success_date(self):
        if self.status == 'SUCCESSFUL':
            try:
                return self.actions.filter(type='succeeded')[0].timestamp
            except:
                return ''
        return ''

    def percent_of_goal(self):
        if self.type == THANKS:
            return 100
        percent = 0
        if self.status == 'SUCCESSFUL' or self.status == 'ACTIVE':
            if self.type == BUY2UNGLUE:
                percent = int(100 - 100*self.left/self.target)
            else:
                percent = int(self.current_total/self.target*100)
        return percent

    @property
    def countdown(self):
        from math import ceil
        if not self.deadline:
            return ''
        time_remaining = self.deadline - now()
        countdown = ""

        if time_remaining.days:
            countdown = "%s days" % str(time_remaining.days + 1)
        elif time_remaining.seconds > 3600:
            countdown = "%s hours" % str(time_remaining.seconds/3600 + 1)
        elif time_remaining.seconds > 60:
            countdown = "%s minutes" % str(time_remaining.seconds/60 + 1)
        else:
            countdown = "Seconds"

        return countdown

    @property
    def deadline_or_now(self):
        return self.deadline if self.deadline else now()

    @classmethod
    def latest_ending(cls):
        return timedelta(days=int(settings.UNGLUEIT_LONGEST_DEADLINE)) + now()

    def make_mobis(self):
        # make archive files for ebooks, make mobi files for epubs
        versions = set()
        for ebook in self.work.ebooks().filter(provider__in=good_providers, format='mobi'):
            versions.add(ebook.version_label)
        for ebook in self.work.ebooks_all().exclude(provider='Unglue.it').filter(provider__in=good_providers, format='epub'):
            if not ebook.version_label in versions:
                # now make the mobi file
                ebf = ebook.get_archive_ebf()
                ebf.make_mobi()

    def add_ask_to_ebfs(self, position=0):
        if not self.use_add_ask or self.type != THANKS:
            return
        format_versions = []
        to_dos = []
        for ebf in self.work.ebookfiles().filter(asking=False, ebook__provider='Unglue.it').order_by('-created'):
            format_version = '{}_{}'.format(ebf.ebook.format, ebf.ebook.version_label)
            if ebf.format in ('pdf', 'epub') and not format_version in format_versions:
                ebf.file.open()
                to_dos.append({'content': ebf.file.read(), 'ebook': ebf.ebook})
                format_versions.append(format_version)
        for ebook in self.work.ebooks_all().exclude(provider='Unglue.it').filter(provider__in=good_providers):
            format_version = '{}_{}'.format(ebook.format, ebook.version_label)
            if ebook.format in ('pdf', 'epub') and not format_version in format_versions:
                to_dos.append({'content': ebook.get_archive().read(), 'ebook': ebook})
                format_versions.append(format_version)
        new_ebfs = []
        for to_do in to_dos:
            edition = to_do['ebook'].edition
            version = {'label':to_do['ebook'].version_label, 'iter':to_do['ebook'].version_iter}
            if to_do['ebook'].format == 'pdf':
                try:
                    added = ask_pdf({'campaign':self, 'work':self.work, 'site':Site.objects.get_current()})
                    new_file = SpooledTemporaryFile()
                    old_file = SpooledTemporaryFile()
                    old_file.write(to_do['content'])
                    if position == 0:
                        pdf_append(added, old_file, new_file)
                    else:
                        pdf_append(old_file, added, new_file)
                    new_file.seek(0)
                    new_pdf_ebf = EbookFile.objects.create(edition=edition, format='pdf', asking=True)
                    new_pdf_ebf.version = version
                    new_pdf_ebf.file.save(path_for_file('ebf', None), ContentFile(new_file.read()))
                    new_pdf_ebf.save()
                    new_ebfs.append(new_pdf_ebf)
                except Exception as e:
                    logger.error("error appending pdf ask  %s" % (e))
            elif to_do['ebook'].format == 'epub':
                try:
                    old_file = SpooledTemporaryFile()
                    old_file.write(to_do['content'])
                    new_file = ask_epub(old_file, {'campaign':self, 'work':self.work, 'site':Site.objects.get_current()})
                    new_file.seek(0)
                    new_epub_ebf = EbookFile.objects.create(edition=edition, format='epub', asking=True)
                    new_epub_ebf.file.save(path_for_file(new_epub_ebf, None), ContentFile(new_file.read()))
                    new_epub_ebf.save()
                    new_epub_ebf.version = version
                    new_ebfs.append(new_epub_ebf)
                    
                    # now make the mobi file
                    new_mobi_ebf = EbookFile.objects.create(edition=edition, format='mobi', asking=True)
                    new_mobi_ebf.file.save(path_for_file('ebf', None), ContentFile(mobi.convert_to_mobi(new_epub_ebf.file.url)))
                    new_mobi_ebf.save()
                    new_mobi_ebf.version = version
                    new_ebfs.append(new_mobi_ebf)
                except Exception as e:
                    logger.error("error making epub ask or mobi  %s" % (e))
        for ebf in new_ebfs:
            ebook = Ebook.objects.create(
                edition=ebf.edition,
                format=ebf.format,
                rights=self.license,
                provider="Unglue.it",
                url=ebf.file.url,
                version_label=ebf.version['label'],
                version_iter=ebf.version['iter'],
            )
            ebf.ebook = ebook
            ebf.save()
        new_ebf_pks = [ebf.pk for ebf in new_ebfs]

        for old_ebf in self.work.ebookfiles().filter(asking=True).exclude(pk__in=new_ebf_pks):
            obsolete = Ebook.objects.filter(url=old_ebf.file.url)
            old_ebf.ebook.deactivate()
            old_ebf.file.delete()
            old_ebf.delete()
        
        for non_asking in self.work.ebookfiles().filter(asking=False, ebook__active=True):
            non_asking.ebook.deactivate()

    def revert_asks(self):
        # there should be a deactivated non-asking ebook for every asking ebook
        if self.type != THANKS:  # just to make sure that ebf's can be unglued by mistake
            return
        format_versions = []
        for ebf in EbookFile.objects.filter(edition__work=self.work).exclude(file='').exclude(ebook=None).order_by('-created'):
            format_version = '{}_{}'.format(ebf.format, ebf.ebook.version_label)
            if ebf.asking: 
                ebf.ebook.deactivate()
            elif format_version in format_versions:
                # this ebook file has the wrong "asking"
                ebf.ebook.deactivate()
            else:
                ebf.ebook.activate()
                format_versions.append(format_version)

    def make_unglued_ebf(self, format, watermarked):
        r = urllib2.urlopen(watermarked.download_link(format))
        ebf = EbookFile.objects.create(edition=self.work.preferred_edition, format=format)
        ebf.file.save(path_for_file(ebf, None), ContentFile(r.read()))
        ebf.file.close()
        ebf.save()
        ebook = Ebook.objects.create(
            edition=self.work.preferred_edition,
            format=format,
            rights=self.license,
            provider="Unglue.it",
            url=settings.BASE_URL_SECURE + reverse('download_campaign', args=[self.work.id, format]),
            version='unglued',
        )
        old_ebooks = Ebook.objects.exclude(pk=ebook.pk).filter(
            edition=self.work.preferred_edition,
            format=format,
            rights=self.license,
            provider="Unglue.it",
        )
        for old_ebook in old_ebooks:
            old_ebook.deactivate()
        return ebook.pk


    def watermark_success(self):
        if self.status == 'SUCCESSFUL' and self.type == BUY2UNGLUE:
            params = {
                'customeremailaddress': self.license,
                'customername': 'The Public',
                'languagecode':'1033',
                'expirydays': 1,
                'downloadlimit': 7,
                'exlibris':0,
                'chapterfooter':0,
                'disclaimer':0,
                'referenceid': '%s:%s:%s' % (self.work.id, self.id, self.license),
                'kf8mobi': True,
                'epub': True,
            }
            ungluified = ungluify(self.work.epubfiles()[0].file, self)
            ungluified.filename.seek(0)
            watermarked = watermarker.platform(epubfile=ungluified.filename, **params)
            self.make_unglued_ebf('epub', watermarked)
            self.make_unglued_ebf('mobi', watermarked)
            return True
        return False

    def is_pledge(self):
        return  self.type == REWARDS

    @property
    def user_to_pay(self):
        return self.rh.owner

    ### for compatibility with MARC output
    def marc_records(self):
        return self.work.marc_records()


class Wishlist(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='wishlist')
    works = models.ManyToManyField('Work', related_name='wishlists', through='Wishes')

    def __unicode__(self):
        return "%s's Books" % self.user.username

    def add_work(self, work, source, notify=False):
        try:
            w = Wishes.objects.get(wishlist=self, work=work)
        except:
            Wishes.objects.create(source=source, wishlist=self, work=work)
            work.update_num_wishes()
            # only send notification in case of new wishes
            # and only when they result from user action, not (e.g.) our tests
            if notify:
                wishlist_added.send(sender=self, work=work, supporter=self.user)

    def remove_work(self, work):
        w = Wishes.objects.filter(wishlist=self, work=work)
        if w:
            w.delete()
            work.update_num_wishes()

    def work_source(self, work):
        w = Wishes.objects.filter(wishlist=self, work=work)
        if w:
            return w[0].source
        else:
            return ''

class Wishes(models.Model):
    created = models.DateTimeField(auto_now_add=True, db_index=True,)
    source = models.CharField(max_length=15, blank=True, db_index=True,)
    wishlist = models.ForeignKey('Wishlist')
    work = models.ForeignKey('Work', related_name='wishes')
    class Meta:
        db_table = 'core_wishlist_works'

class Badge(models.Model):
    name = models.CharField(max_length=72, blank=True)
    description = models.TextField(default='', null=True)

    @property
    def path(self):
        return '/static/images/%s.png' % self.name
    def __unicode__(self):
        return self.name

def pledger():
    if not pledger.instance:
        pledger.instance = Badge.objects.get(name='pledger')
    return pledger.instance
pledger.instance = None

def pledger2():
    if not pledger2.instance:
        pledger2.instance = Badge.objects.get(name='pledger2')
    return pledger2.instance
pledger2.instance = None

ANONYMOUS_AVATAR = '/static/images/header/avatar.png'
(NO_AVATAR, GRAVATAR, TWITTER, FACEBOOK, UNGLUEITAR) = AVATARS

class Libpref(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='libpref')
    marc_link_target = models.CharField(
        max_length=6,
        default='UNGLUE',
        choices=settings.MARC_PREF_OPTIONS,
        verbose_name="MARC record link targets",
    )

class UserProfile(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile')
    tagline = models.CharField(max_length=140, blank=True)
    pic_url = models.URLField(blank=True)
    home_url = models.URLField(blank=True)
    twitter_id = models.CharField(max_length=15, blank=True)
    facebook_id = models.BigIntegerField(null=True, blank=True)
    librarything_id = models.CharField(max_length=31, blank=True)
    badges = models.ManyToManyField('Badge', related_name='holders', blank=True)
    kindle_email = models.EmailField(max_length=254, blank=True)

    goodreads_user_id = models.CharField(max_length=32, null=True, blank=True)
    goodreads_user_name = models.CharField(max_length=200, null=True, blank=True)
    goodreads_auth_token = models.TextField(null=True, blank=True)
    goodreads_auth_secret = models.TextField(null=True, blank=True)
    goodreads_user_link = models.CharField(max_length=200, null=True, blank=True)

    avatar_source = models.PositiveSmallIntegerField(
        null=True,
        default=UNGLUEITAR,
        choices=(
            (NO_AVATAR, 'No Avatar, Please'),
            (GRAVATAR, 'Gravatar'),
            (TWITTER, 'Twitter'),
            (FACEBOOK, 'Facebook'),
            (UNGLUEITAR, 'Unglueitar'),
        )
    )

    def __unicode__(self):
        return self.user.username

    def reset_pledge_badge(self):
        #count user pledges
        n_pledges = self.pledge_count
        if self.badges.exists():
            self.badges.remove(pledger())
            self.badges.remove(pledger2())
        if n_pledges == 1:
            self.badges.add(pledger())
        elif n_pledges > 1:
            self.badges.add(pledger2())

    @property
    def pledge_count(self):
        return self.user.transaction_set.exclude(status='NONE').exclude(status='Canceled', reason=None).exclude(anonymous=True).count()

    @property
    def account(self):
        # there should be only one active account per user
        accounts = self.user.account_set.filter(date_deactivated__isnull=True)
        if accounts.count() == 0:
            return None
        else:
            return accounts[0]

    @property
    def old_account(self):
        accounts = self.user.account_set.filter(date_deactivated__isnull=False).order_by('-date_deactivated')
        if accounts.count() == 0:
            return None
        else:
            return accounts[0]

    @property
    def pledges(self):
        return self.user.transaction_set.filter(status=TRANSACTION_STATUS_ACTIVE, campaign__type=1)

    @property
    def last_transaction(self):
        from regluit.payment.models import Transaction
        try:
            return Transaction.objects.filter(user=self.user).order_by('-date_modified')[0]
        except IndexError:
            return None

    @property
    def ack_name(self):
        # use preferences from last transaction, if any
        last = self.last_transaction
        if last and last.extra:
            return last.extra.get('ack_name', self.user.username)
        else:
            return self.user.username

    @property
    def anon_pref(self):
        # use preferences from last transaction, if any
        last = self.last_transaction
        if last:
            return last.anonymous
        else:
            return None

    @property
    def on_ml(self):
        if "@example.org" in self.user.email:
            # use @example.org email addresses for testing!
            return False
        try:
            return settings.MAILCHIMP_NEWS_ID in pm.listsForEmail(email_address=self.user.email)
        except MailChimpException, e:
            if e.code != 215: # don't log case where user is not on a list
                logger.error("error getting mailchimp status  %s" % (e))
        except Exception, e:
            logger.error("error getting mailchimp status  %s" % (e))
        return False

    def ml_subscribe(self, **kwargs):
        if "@example.org" in self.user.email:
            # use @example.org email addresses for testing!
            return True
        from regluit.core.tasks import ml_subscribe_task
        ml_subscribe_task.delay(self, **kwargs)

    def ml_unsubscribe(self):
        if "@example.org" in self.user.email:
            # use @example.org email addresses for testing!
            return True
        try:
            return pm.listUnsubscribe(id=settings.MAILCHIMP_NEWS_ID, email_address=self.user.email)
        except Exception, e:
            logger.error("error unsubscribing from mailchimp list  %s" % (e))
        return False

    def gravatar(self):
        # construct the url
        gravatar_url = "https://www.gravatar.com/avatar/" + hashlib.md5(self.user.email.lower()).hexdigest() + "?"
        gravatar_url += urllib.urlencode({'d':'wavatar', 's':'50'})
        return gravatar_url

    def unglueitar(self):
        # construct the url
        gravatar_url = "https://www.gravatar.com/avatar/" + hashlib.md5(urllib.quote_plus(self.user.username.encode('utf-8')) + '@unglue.it').hexdigest() + "?"
        gravatar_url += urllib.urlencode({'d':'wavatar', 's':'50'})
        return gravatar_url


    @property
    def avatar_url(self):
        if self.avatar_source is None or self.avatar_source is TWITTER:
            if self.pic_url:
                return self.pic_url
            else:
                return ANONYMOUS_AVATAR
        elif self.avatar_source == UNGLUEITAR:
            return self.unglueitar()
        elif self.avatar_source == GRAVATAR:
            return self.gravatar()
        elif self.avatar_source == FACEBOOK and self.facebook_id != None:
            return 'https://graph.facebook.com/v2.3/' + str(self.facebook_id) + '/picture?redirect=true'
        else:
            return ANONYMOUS_AVATAR

    @property
    def social_auths(self):
        socials = self.user.social_auth.all()
        auths = {}
        for social in socials:
            auths[social.provider] = True
        return auths

    @property
    def libraries(self):
        libs = []
        for group in self.user.groups.all():
            try:
                libs.append(group.library)
            except Library.DoesNotExist:
                pass
        return libs


class Press(models.Model):
    url = models.URLField()
    title = models.CharField(max_length=140)
    source = models.CharField(max_length=140)
    date = models.DateField(db_index=True,)
    language = models.CharField(max_length=20, blank=True)
    highlight = models.BooleanField(default=False)
    note = models.CharField(max_length=140, blank=True)

class Gift(models.Model):
    # the acq will contain the recipient, and the work
    acq = models.ForeignKey('Acq', related_name='gifts')
    to = models.CharField(max_length=75, blank=True) # store the email address originally sent to, not necessarily the email of the recipient
    giver = models.ForeignKey(User, related_name='gifts')
    message = models.TextField(max_length=512, default='')
    used = models.DateTimeField(null=True)

    @staticmethod
    def giftee(email, t_id):
        # return a user (create a user if necessary)
        (giftee, new_user) = User.objects.get_or_create(email=email, defaults={'username':'giftee%s' % t_id})
        giftee.new_user = new_user
        return giftee

    def use(self):
        self.used = now()
        self.save()
        notification.send([self.giver], "purchase_got_gift", {'gift': self}, True)


# this was causing a circular import problem and we do not seem to be using
# anything from regluit.core.signals after this line
# from regluit.core import signals
from regluit.payment.manager import PaymentManager
