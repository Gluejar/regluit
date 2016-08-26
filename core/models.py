'''
external library imports
'''
import binascii
import logging
import hashlib
import uuid
import re
import random
import urllib
import urllib2
from urlparse import urlparse
import unicodedata
import math
import requests

from ckeditor.fields import RichTextField
from datetime import timedelta, datetime
from decimal import Decimal
from notification import models as notification
from postmonkey import PostMonkey, MailChimpException
from sorl.thumbnail import get_thumbnail
from tempfile import SpooledTemporaryFile

'''
django imports
'''
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.contenttypes.fields import GenericRelation
from django.core.urlresolvers import reverse
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import F, Q
from django.db.models.signals import post_save, pre_delete
from django.utils.translation import ugettext_lazy as _
'''
regluit imports
'''
import regluit
from regluit.libraryauth.auth import AVATARS
import regluit.core.isbn
import regluit.core.cc as cc
from regluit.core.epub import personalize, ungluify, test_epub, ask_epub
from regluit.core.pdf import ask_pdf, pdf_append
from regluit.core import mobi
from regluit.marc.models import MARCRecord as NewMARC
from regluit.core.signals import (
    successful_campaign,
    unsuccessful_campaign,
    wishlist_added
)

from regluit.utils import crypto
from regluit.utils.localdatetime import now, date_today

from regluit.payment.parameters import (
    TRANSACTION_STATUS_ACTIVE,
    TRANSACTION_STATUS_COMPLETE,
    TRANSACTION_STATUS_CANCELED,
    TRANSACTION_STATUS_ERROR,
    TRANSACTION_STATUS_FAILED,
    TRANSACTION_STATUS_INCOMPLETE
)

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
)
from regluit.questionnaire.models import Landing  

from regluit.booxtream import BooXtream 
watermarker = BooXtream()

from regluit.libraryauth.models import Library

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
    user =  models.ForeignKey(settings.AUTH_USER_MODEL, related_name="tasks", null=True) 
    description = models.CharField(max_length=2048, null=True)  # a description of what the task is 
    function_name = models.CharField(max_length=1024) # used to reconstitute the AsyncTask with which to get status
    function_args = models.IntegerField(null=True)  # not full generalized here -- takes only a single arg for now.
    active = models.NullBooleanField(default=True) 

    def __unicode__(self):
        return "Task %s arg:%s ID# %s %s: State %s " % (self.function_name, self.function_args, self.task_id, self.description, self.state)

    @property
    def AsyncResult(self):
        f = getattr(regluit.core.tasks,self.function_name)
        return f.AsyncResult(self.task_id)
    @property
    def state(self):
        f = getattr(regluit.core.tasks,self.function_name)
        return f.AsyncResult(self.task_id).state
    @property
    def result(self):
        f = getattr(regluit.core.tasks,self.function_name)
        return f.AsyncResult(self.task_id).result
    @property
    def info(self):
        f = getattr(regluit.core.tasks,self.function_name)
        return f.AsyncResult(self.task_id).info        
        
class Claim(models.Model):
    STATUSES = ((
        u'active', u'Claim has been accepted.'),
        (u'pending', u'Claim is pending acceptance.'),
        (u'release', u'Claim has not been accepted.'),
    )
    created =  models.DateTimeField(auto_now_add=True)  
    rights_holder =  models.ForeignKey("RightsHolder", related_name="claim", null=False )    
    work =  models.ForeignKey("Work", related_name="claim", null=False )    
    user =  models.ForeignKey(settings.AUTH_USER_MODEL, related_name="claim", null=False ) 
    status = models.CharField(max_length=7, choices=STATUSES, default='active')
    
    @property
    def can_open_new(self):
        # whether a campaign can be opened for this claim
        
        #must be an active claim
        if self.status != 'active':
            return False
        #can't already be a campaign
        for campaign in self.campaigns:
            if campaign.status in ['ACTIVE','INITIALIZED']:
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
    if 'example.org' in instance.user.email or hasattr(instance,'dont_notify'):
        return
    try:
        (rights, new_rights) = User.objects.get_or_create(email='rights@gluejar.com',defaults={'username':'RightsatUnglueit'})
    except:
        rights = None
    if instance.user == instance.rights_holder.owner:
        ul=(instance.user, rights)
    else:
        ul=(instance.user, instance.rights_holder.owner, rights)
    notification.send(ul, "rights_holder_claim", {'claim': instance,})
post_save.connect(notify_claim,sender=Claim)
        
class RightsHolder(models.Model):
    created =  models.DateTimeField(auto_now_add=True)  
    email = models.CharField(max_length=100, blank=True)
    rights_holder_name = models.CharField(max_length=100, blank=False)
    owner =  models.ForeignKey(settings.AUTH_USER_MODEL, related_name="rights_holder", null=False )
    can_sell = models.BooleanField(default=False)
    def __unicode__(self):
        return self.rights_holder_name
    
class Premium(models.Model):
    PREMIUM_TYPES = ((u'00', u'Default'),(u'CU', u'Custom'),(u'XX', u'Inactive'))
    TIERS = {"supporter":25, "patron":50, "bibliophile":100} #should load this from fixture
    created =  models.DateTimeField(auto_now_add=True)  
    type = models.CharField(max_length=2, choices=PREMIUM_TYPES)
    campaign = models.ForeignKey("Campaign", related_name="premiums", null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=0, blank=False)
    description =  models.TextField(null=True, blank=False)
    limit = models.IntegerField(default = 0)

    @property
    def premium_count(self):
        t_model=apps.get_model('payment','Transaction')
        return t_model.objects.filter(premium=self).count()
    @property
    def premium_remaining(self):
        t_model=apps.get_model('payment','Transaction')
        return self.limit - t_model.objects.filter(premium=self).count()
    def  __unicode__(self):
        return  (self.campaign.work.title if self.campaign else '')  + ' $' + str(self.amount)
    
class PledgeExtra:
    def __init__(self,premium=None,anonymous=False,ack_name='',ack_dedication='',offer=None):
        self.anonymous = anonymous
        self.premium = premium
        self.offer = offer
        self.extra = {}
        if ack_name:
            self.extra['ack_name']=ack_name
        if ack_dedication:
            self.extra['ack_dedication']=ack_dedication

class CampaignAction(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    # anticipated types: activated, withdrawn, suspended, restarted, succeeded, failed, unglued
    type = models.CharField(max_length=15)
    comment = models.TextField(null=True, blank=True)
    campaign = models.ForeignKey("Campaign", related_name="actions", null=False)
    
class Offer(models.Model):
    CHOICES = ((INDIVIDUAL,'Individual license'),(LIBRARY,'Library License'))
    work = models.ForeignKey("Work", related_name="offers", null=False)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=False)
    license = models.PositiveSmallIntegerField(null = False, default = INDIVIDUAL,
            choices=CHOICES)
    active = models.BooleanField(default=False)
    
    @property
    def days_per_copy(self):
        return Decimal(float(self.price) / self.work.last_campaign().dollar_per_day )
    
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
    CHOICES = ((INDIVIDUAL,'Individual license'),(LIBRARY,'Library License'),(BORROWED,'Borrowed from Library'), (TESTING,'Just for Testing'), (RESERVE,'On Reserve'),(THANKED,'Already Thanked'),)
    created = models.DateTimeField(auto_now_add=True, db_index=True,)
    expires = models.DateTimeField(null=True)
    refreshes = models.DateTimeField(auto_now_add=True)
    refreshed = models.BooleanField(default=True)
    work = models.ForeignKey("Work", related_name='acqs', null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acqs')
    license = models.PositiveSmallIntegerField(null = False, default = INDIVIDUAL,
            choices=CHOICES)
    watermarked = models.ForeignKey("booxtream.Boox",  null=True)
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
        if self.watermarked == None or self.watermarked.expired:
            if self.on_reserve:
                self.borrow(self.user)
            do_watermark= self.work.last_campaign().do_watermark
            params={
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
            self.watermarked = watermarker.platform(epubfile= personalized, **params)
            self.save()
        return self.watermarked
        
    def _hash(self):
        return hashlib.md5('%s:%s:%s:%s'%(settings.SOCIAL_AUTH_TWITTER_SECRET,self.user.id,self.work.id,self.created)).hexdigest() 
        
    def expire_in(self, delta):
        self.expires = (now() + delta) if delta else now()
        self.save()
        if self.lib_acq:
            self.lib_acq.refreshes = now() + delta
            self.lib_acq.refreshed = False
            self.lib_acq.save()
        
    @property
    def on_reserve(self):
        return self.license==RESERVE
        
    def borrow(self, user=None):
        if self.on_reserve:
            self.license=BORROWED
            self.expire_in(timedelta(days=14))
            self.user.wishlist.add_work( self.work, "borrow")
            notification.send([self.user], "library_borrow", {'acq':self})
            return self
        elif self.borrowable and user:
            user.wishlist.add_work( self.work, "borrow")
            borrowed = Acq.objects.create(user=user,work=self.work,license= BORROWED, lib_acq=self)
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
        return Hold.objects.filter(library__user=self.user,work=self.work).order_by('created')
        

def config_acq(sender, instance, created,  **kwargs):
    if created:
        instance.nonce=instance._hash()
        instance.save()
        if instance.license == RESERVE:
            instance.expire_in(timedelta(hours=24))
        if instance.license == BORROWED:
            instance.expire_in(timedelta(days=14))

post_save.connect(config_acq,sender=Acq)

class Hold(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    work = models.ForeignKey("Work", related_name='holds', null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='holds', null=False)
    library = models.ForeignKey(Library, related_name='holds', null=False)

    def __unicode__(self):
        return '%s for %s at %s' % (self.work,self.user.username,self.library)
    def ahead(self):
        return Hold.objects.filter(work=self.work,library=self.library,created__lt=self.created).count()

class Campaign(models.Model):
    LICENSE_CHOICES = cc.FREECHOICES
    created = models.DateTimeField(auto_now_add=True,)
    name = models.CharField(max_length=500, null=True, blank=False)
    description = RichTextField(null=True, blank=False)
    details = RichTextField(null=True, blank=True)
    target = models.DecimalField(max_digits=14, decimal_places=2, null=True, default=0.00)
    license = models.CharField(max_length=255, choices = LICENSE_CHOICES, default='CC BY-NC-ND')
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
    type = models.PositiveSmallIntegerField(null = False, default = REWARDS,
            choices=((REWARDS,'Pledge-to-unglue campaign'),(BUY2UNGLUE,'Buy-to-unglue campaign'),(THANKS,'Thanks-for-ungluing campaign')))
    edition = models.ForeignKey("Edition", related_name="campaigns", null=True)
    email =  models.CharField(max_length=100, blank=True)
    publisher = models.ForeignKey("Publisher", related_name="campaigns", null=True)
    do_watermark = models.BooleanField(default=True)
    use_add_ask = models.BooleanField(default=True)
    
    def __init__(self, *args, **kwargs):
        self.problems=[]
        return super(Campaign, self).__init__(*args, **kwargs)
    
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
            old_managers= self.managers.all()
            
            # copy custom premiums
            new_premiums= self.premiums.filter(type='CU')
 
            # setting pk to None will insert new copy http://stackoverflow.com/a/4736172/7782
            self.pk = None
            self.status = 'INITIALIZED'
 
            # set deadline far in future -- presumably RH will set deadline to proper value before campaign launched
            self.deadline = date_today() + timedelta(days=int(settings.UNGLUEIT_LONGEST_DEADLINE))
            
            # allow created, activated dates to be autoset by db
            self.created = None
            self.name = 'copy of %s' % self.name
            self.activated = None
            self.update_left()
            self.save()
            self.managers=old_managers
            
            # clone associated premiums
            for premium in new_premiums:
                premium.pk=None
                premium.created = None
                premium.campaign = self
                premium.save()
            return self
        else:
            return None

    def clonable(self):
        """campaign clonable if it's UNSUCCESSFUL and is the last campaign associated with a Work"""
        
        if self.status == 'UNSUCCESSFUL' and self.work.last_campaign().id==self.id:
            return True
        else:
            return False

    @property
    def launchable(self):
        may_launch=True
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
            if self.type==REWARDS:
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
            if self.type==BUY2UNGLUE:
                if self.work.offers.filter(price__gt=0,active=True).count()==0: 
                    self.problems.append(_('You can\'t launch a buy-to-unglue campaign before setting a price for your ebooks' ))
                    may_launch = False  
                if EbookFile.objects.filter(edition__work=self.work).count()==0: 
                    self.problems.append(_('You can\'t launch a buy-to-unglue campaign if you don\'t have any ebook files uploaded' ))
                    may_launch = False  
                if ((self.cc_date_initial is None) or (self.cc_date_initial > datetime.combine(settings.MAX_CC_DATE, datetime.min.time())) or (self.cc_date_initial < now())):
                    self.problems.append(_('You must set an initial Ungluing Date that is in the future and not after %s' % settings.MAX_CC_DATE ))
                    may_launch = False  
                if self.target:
                    if self.target < Decimal(settings.UNGLUEIT_MINIMUM_TARGET):
                        self.problems.append(_('A buy-to-unglue campaign may not be launched with a target less than $%s' % settings.UNGLUEIT_MINIMUM_TARGET))
                        may_launch = False
                else:
                    self.problems.append(_('A buy-to-unglue campaign must have a target'))
                    may_launch = False
            if self.type==THANKS:
                # the case in which there is no EbookFile and no Ebook associated with work (We have ebooks without ebook files.)
                if EbookFile.objects.filter(edition__work=self.work).count()==0 and self.work.ebooks().count()==0: 
                    self.problems.append(_('You can\'t launch a thanks-for-ungluing campaign if you don\'t have any ebook files uploaded' ))
                    may_launch = False  
        except Exception as e :
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
        if not self.status=='ACTIVE':
            return False
        elif self.type==REWARDS:
            if (ignore_deadline_for_success or self.deadline < now()) and self.current_total >= self.target:
                self.status = 'SUCCESSFUL'
                self.save()
                action = CampaignAction(campaign=self, type='succeeded', comment = self.current_total) 
                action.save()

                if process_transactions:
                    p = PaymentManager()
                    results = p.execute_campaign(self)
                
                if send_notice:
                    successful_campaign.send(sender=None,campaign=self)
                
                # should be more sophisticated in whether to return True -- look at all the transactions?
                return True
            elif self.deadline < now() and self.current_total < self.target:
                self.status = 'UNSUCCESSFUL'
                self.save()
                action = CampaignAction(campaign=self, type='failed', comment = self.current_total) 
                action.save()

                if process_transactions:
                    p = PaymentManager()
                    results = p.cancel_campaign(self)            
            
                if send_notice:
                    regluit.core.signals.unsuccessful_campaign.send(sender=None,campaign=self)
                # should be more sophisticated in whether to return True -- look at all the transactions?
                return True
        elif  self.type==BUY2UNGLUE:
            if self.cc_date < date_today():
                self.status = 'SUCCESSFUL'
                self.save()
                action = CampaignAction(campaign=self, type='succeeded', comment = self.current_total) 
                action.save() 
                self.watermark_success()               
                if send_notice:
                    successful_campaign.send(sender=None,campaign=self)
                
                # should be more sophisticated in whether to return True -- look at all the transactions?
                return True
        
        return False
    
    _current_total = None
    @property
    def current_total(self):
        if self._current_total is None:
            p = PaymentManager()
            self._current_total =  p.query_campaign(self,summary=True, campaign_total=True)
        return self._current_total
    
    def set_dollar_per_day(self):
        if self.status!='INITIALIZED' and self.dollar_per_day:
            return self.dollar_per_day
        if self.cc_date_initial is None:
            return None
        
        start_datetime= self.activated if self.activated else datetime.today()
        
        time_to_cc = self.cc_date_initial - start_datetime
        
        self.dollar_per_day = float(self.target)/float(time_to_cc.days)
        if self.status!='DEMO':
            self.save()
        return self.dollar_per_day
    
    def set_cc_date_initial(self, a_date=settings.MAX_CC_DATE):
        self.cc_date_initial = datetime.combine(a_date, datetime.min.time()) 
        
    @property
    def cc_date(self):
        if self.type in { REWARDS, THANKS }:
            return None
        if self.dollar_per_day == None:
            return self.cc_date_initial.date()
        cc_advance_days = float(self.current_total) / self.dollar_per_day
        return (self.cc_date_initial-timedelta(days=cc_advance_days)).date()
            
        
    def update_left(self):
        self._current_total=None
        if self.type == THANKS:
            self.left == Decimal(0.00)
        elif self.type == BUY2UNGLUE:
            self.left = Decimal(self.dollar_per_day*float((self.cc_date_initial - datetime.today()).days))-self.current_total
        else:
            self.left = self.target - self.current_total
        if self.status != 'DEMO':
            self.save()
        
    def transactions(self,  **kwargs):
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
        self.status= 'ACTIVE'
        self.left = self.target
        self.activated = datetime.today()
        if self.type == THANKS:
            # make ebooks from ebookfiles
            self.work.make_ebooks_from_ebfs()
        self.save()
        action = CampaignAction( campaign = self, type='activated', comment = self.get_type_display()) 
        ungluers = self.work.wished_by()        
        notification.queue(ungluers, "wishlist_active", {'campaign':self}, True)
        return self


    def suspend(self, reason):
        status = self.status
        if status != 'ACTIVE':
            raise UnglueitError(_('Campaign needs to be active in order to be suspended'))
        action = CampaignAction( campaign = self, type='suspended', comment = reason) 
        action.save()
        self.status='SUSPENDED'
        self.save()
        return self
        
    def withdraw(self, reason):
        status = self.status
        if status != 'ACTIVE':
            raise UnglueitError(_('Campaign needs to be active in order to be withdrawn'))
        action = CampaignAction( campaign = self, type='withdrawn', comment = reason) 
        action.save()
        self.status='WITHDRAWN'
        self.save()
        return self

    def resume(self, reason):
        """Change campaign status from SUSPENDED to ACTIVE.  We may want to track reason for resuming and track history"""
        status = self.status
        if status != 'SUSPENDED':
            raise UnglueitError(_('Campaign needs to be suspended in order to be resumed'))
        if not reason:
            reason=''
        action = CampaignAction( campaign = self, type='restarted', comment = reason) 
        action.save()
        self.status= 'ACTIVE'
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
        complete = self.transactions().filter(status=TRANSACTION_STATUS_COMPLETE,user=None).count()
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
        ungluers={"all":[],"supporters":[], "patrons":[], "bibliophiles":[]}
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
        
        self._ungluers_= ungluers
        return ungluers

    def ungluer_transactions(self):
    	"""
    	returns a list of authorized transactions for campaigns in progress,
    	or completed transactions for successful campaigns
    	used to build the acks page -- because ack_name, _link, _dedication adhere to transactions,
    	it's easier to return transactions than ungluers
    	"""
        p = PaymentManager()
        ungluers={"all":[],"supporters":[], "anon_supporters": 0, "patrons":[], "anon_patrons": 0, "bibliophiles":[]}
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
            return Decimal(float(self.individual_offer.price) / self.dollar_per_day )
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
        if(self.status == 'SUCCESSFUL' or self.status == 'ACTIVE'):
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
        return (timedelta(days=int(settings.UNGLUEIT_LONGEST_DEADLINE)) + now())
    
    def make_mobi(self):
        for ebf in self.work.ebookfiles().filter(format='epub').order_by('-created'):
            if ebf.active:
                new_mobi_ebf = EbookFile.objects.create(edition=ebf.edition, format='mobi', asking=ebf.asking)
                new_mobi_ebf.file.save(path_for_file('ebf',None),ContentFile(mobi.convert_to_mobi(ebf.file.url)))
                new_mobi_ebf.save()
                self.work.make_ebooks_from_ebfs()
                return True
        return False
        
    def add_ask_to_ebfs(self, position=0):
        if not self.use_add_ask or  self.type != THANKS :
            return
        pdf_to_do = pdf_edition = None
        epub_to_do = epub_edition = None
        new_ebfs = {}
        for ebf in self.work.ebookfiles().filter(asking = False).order_by('-created'):
            if ebf.format=='pdf' and not pdf_to_do:
                ebf.file.open()
                pdf_to_do = ebf.file.read()
                pdf_edition = ebf.edition
            elif ebf.format=='epub' and not epub_to_do: 
                ebf.file.open()
                epub_to_do = ebf.file.read()
                epub_edition = ebf.edition
        for ebook in self.work.ebooks_all().exclude(provider='Unglue.it'):        
            if ebook.format=='pdf' and not pdf_to_do:
                r= requests.get(ebook.url)
                pdf_to_do = r.content
                pdf_edition = ebook.edition
            elif ebook.format=='epub' and not epub_to_do: 
                r= requests.get(ebook.url)
                epub_to_do = r.content
                epub_edition = ebook.edition
        if pdf_to_do:
            try:
                added = ask_pdf({'campaign':self, 'work':self.work, 'site':Site.objects.get_current()})
                new_file = SpooledTemporaryFile()
                old_file = SpooledTemporaryFile()
                old_file.write(pdf_to_do)
                if position==0:
                    pdf_append(added, old_file, new_file)
                else:
                    pdf_append(old_file, added, new_file)
                new_file.seek(0)
                new_pdf_ebf = EbookFile.objects.create(edition=pdf_edition, format='pdf', asking=True)
                new_pdf_ebf.file.save(path_for_file('ebf',None),ContentFile(new_file.read()))
                new_pdf_ebf.save()
                new_ebfs['pdf']=new_pdf_ebf
            except Exception as e:
                logger.error("error appending pdf ask  %s" % (e))
        if epub_to_do:
            try:
                old_file = SpooledTemporaryFile()
                old_file.write(epub_to_do)
                new_file= ask_epub(old_file, {'campaign':self, 'work':self.work, 'site':Site.objects.get_current()})
                new_file.seek(0)
                new_epub_ebf = EbookFile.objects.create(edition=epub_edition, format='epub', asking=True)
                new_epub_ebf.file.save(path_for_file(new_epub_ebf,None),ContentFile(new_file.read()))
                new_epub_ebf.save()
                new_ebfs['epub']=new_epub_ebf
                # now make the mobi file
                new_mobi_ebf = EbookFile.objects.create(edition=epub_edition, format='mobi', asking=True)
                new_mobi_ebf.file.save(path_for_file('ebf',None),ContentFile(mobi.convert_to_mobi(new_epub_ebf.file.url)))
                new_mobi_ebf.save()
                new_ebfs['mobi']=new_mobi_ebf
            except Exception as e:
                logger.error("error making epub ask or mobi  %s" % (e))
        for key in new_ebfs.keys():
            for old_ebf in self.work.ebookfiles().filter(asking = True, format=key).exclude(pk=new_ebfs[key].pk):
                obsolete = Ebook.objects.filter(url=old_ebf.file.url)
                for eb in obsolete:
                    eb.deactivate()
                old_ebf.file.delete()
                old_ebf.delete()
        self.work.make_ebooks_from_ebfs(add_ask=True)
        
    def make_unglued_ebf(self, format, watermarked):
        r=urllib2.urlopen(watermarked.download_link(format))
        ebf=EbookFile.objects.create(edition=self.work.preferred_edition, format=format)
        ebf.file.save(path_for_file(ebf,None),ContentFile(r.read()))
        ebf.file.close()
        ebf.save()
        ebook=Ebook.objects.create(
                edition=self.work.preferred_edition, 
                format=format, 
                rights=self.license, 
                provider="Unglue.it",
                url= settings.BASE_URL_SECURE + reverse('download_campaign',args=[self.work.id,format]),
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
            params={
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
            watermarked = watermarker.platform(epubfile= ungluified.filename, **params)
            self.make_unglued_ebf('epub', watermarked)
            self.make_unglued_ebf('mobi', watermarked)
            return True
        return False
    
    def is_pledge(self):
        return  self.type==REWARDS
    
    @property   
    def user_to_pay(self):
        return self.rh.owner
    
    ### for compatibility with MARC output
    def marc_records(self):
        return self.work.marc_records()

class Identifier(models.Model):
    # olib, ltwk, goog, gdrd, thng, isbn, oclc, olwk, olib, gute, glue
    type = models.CharField(max_length=4, null=False)
    value =  models.CharField(max_length=250, null=False)
    work = models.ForeignKey("Work", related_name="identifiers", null=False)
    edition = models.ForeignKey("Edition", related_name="identifiers", null=True)
    
    class Meta:
        unique_together = ("type", "value")
        
    @staticmethod
    def set(type=None, value=None, edition=None, work=None):
        # if there's already an id of this type for this work and edition, change it 
        # if not, create it. if the id exists and points to something else, change it.
        identifier= Identifier.get_or_add(type=type, value=value, edition = edition, work=work)
        if identifier.work.id != work.id:
            identifier.work=work
            identifier.save()
        if identifier.edition and edition:
            if identifier.edition.id != edition.id:
                identifier.edition = edition
                identifier.save()
            others= Identifier.objects.filter(type=type, work=work, edition=edition).exclude(value=value)
            if others.count()>0:
                for other in others:
                    other.delete()
        return identifier
    
    @staticmethod
    def get_or_add( type='goog', value=None, edition=None, work=None):
        try:
            return Identifier.objects.get(type=type, value=value)
        except Identifier.DoesNotExist:
            i=Identifier(type=type, value=value, edition=edition, work=work)
            i.save()
            return i
    
    def __unicode__(self):
        return u'{0}:{1}'.format(self.type, self.value)

class Work(models.Model):
    created = models.DateTimeField(auto_now_add=True, db_index=True,)
    title = models.CharField(max_length=1000)
    language = models.CharField(max_length=5, default="en", null=False, db_index=True,)
    openlibrary_lookup = models.DateTimeField(null=True)
    num_wishes = models.IntegerField(default=0, db_index=True)
    description = models.TextField(default='', null=True, blank=True)
    selected_edition =  models.ForeignKey("Edition", related_name = 'selected_works', null = True)
    # repurposed earliest_publication to actually be publication range
    publication_range =  models.CharField(max_length=50, null = True)
    featured = models.DateTimeField(null=True, blank=True, db_index=True,)
    is_free = models.BooleanField(default=False)
    landings = GenericRelation(Landing)

    class Meta:
        ordering = ['title']
    def __unicode__(self):
        return self.title

    def __init__(self, *args, **kwargs):
        self._last_campaign = None
        super(Work, self).__init__(*args, **kwargs)

    @property
    def googlebooks_id(self):
        try:
            preferred_id=self.preferred_edition.googlebooks_id
            # note that there should always be a preferred edition
        except AttributeError:
            # this work has no edition.
            return ''
        if preferred_id:
            return preferred_id
        try:
            return self.identifiers.filter(type='goog')[0].value
        except IndexError:
            return ''

    @property
    def googlebooks_url(self):
        if self.googlebooks_id:
            return "http://books.google.com/books?id=%s" % self.googlebooks_id
        else:
            return ''

    @property 
    def goodreads_id(self):
        preferred_id=self.preferred_edition.goodreads_id
        if preferred_id:
            return preferred_id
        try:
            return self.identifiers.filter(type='gdrd')[0].value
        except IndexError:
            return ''

    @property
    def goodreads_url(self):
        return "http://www.goodreads.com/book/show/%s" % self.goodreads_id

    @property 
    def librarything_id(self):
        try:
            return self.identifiers.filter(type='ltwk')[0].value
        except IndexError:
            return ''

    @property
    def librarything_url(self):
        return "http://www.librarything.com/work/%s" % self.librarything_id

    @property 
    def openlibrary_id(self):
        try:
            return self.identifiers.filter(type='olwk')[0].value
        except IndexError:
            return ''
    
    @property
    def openlibrary_url(self):
        return "http://openlibrary.org" + self.openlibrary_id
    
    def cover_filetype(self):
        if self.uses_google_cover():
            return 'jpeg'
        else:
            # consider the path only and not the params, query, or fragment
            url = urlparse(self.cover_image_small().lower()).path

            if url.endswith('.png'):
                return 'png'
            elif url.endswith('.gif'):
                return 'gif'
            elif url.endswith('.jpg') or url.endswith('.jpeg'):
                return 'jpeg'
            else:
                return 'image'
    
    def uses_google_cover(self):
        if self.preferred_edition and self.preferred_edition.cover_image:
            return False
        else: 
            return self.googlebooks_id
    
    def cover_image_large(self):
        if self.preferred_edition and self.preferred_edition.has_cover_image():
            return self.preferred_edition.cover_image_large()
        return "/static/images/generic_cover_larger.png"

    def cover_image_small(self):
        if self.preferred_edition and self.preferred_edition.has_cover_image():
            return self.preferred_edition.cover_image_small()
        return "/static/images/generic_cover_larger.png"

    def cover_image_thumbnail(self):
        try:
            if self.preferred_edition and self.preferred_edition.has_cover_image():
                return self.preferred_edition.cover_image_thumbnail()
        except IndexError:
            pass
        return "/static/images/generic_cover_larger.png"
        
    def authors(self):
        # assumes that they come out in the same order they go in!
        if self.preferred_edition and self.preferred_edition.authors.all().count()>0:
            return  self.preferred_edition.authors.all()
        for edition in self.editions.all():
            if edition.authors.all().count()>0:
                return edition.authors.all()
        return Author.objects.none()

    def relators(self):
        # assumes that they come out in the same order they go in!
        if self.preferred_edition and self.preferred_edition.relators.all().count()>0:
            return  self.preferred_edition.relators.all()
        for edition in self.editions.all():
            if edition.relators.all().count()>0:
                return edition.relators.all()
        return Relator.objects.none()
        
    def author(self):
        # assumes that they come out in the same order they go in!
        if self.relators().count()>0:
            return self.relators()[0].name
        return ''
        
    def authors_short(self):
        # assumes that they come out in the same order they go in!
        if self.relators().count()==1:
            return self.relators()[0].name 
        elif self.relators().count()==2:
            if self.relators()[0].relation == self.relators()[1].relation:
                if self.relators()[0].relation.code == 'aut':
                    return "%s and %s" % (self.relators()[0].author.name, self.relators()[1].author.name)
                else:
                    return "%s and %s, %ss" % (self.relators()[0].author.name, self.relators()[1].author.name, self.relators()[0].relation.name)
            else:
                return "%s (%s) and %s (%s)" % (self.relators()[0].author.name, self.relators()[0].relation.name, self.relators()[1].author.name, self.relators()[1].relation.name)
        elif self.relators().count()>2:
            auths = self.relators().order_by("relation__code")
            if auths[0].relation.code == 'aut':
                return "%s et al." % auths[0].author.name
            else:
                return "%s et al. (%ss)" % (auths[0].author.name , auths[0].relation.name )
        return ''
    
    def kindle_safe_title(self):
        """
        Removes accents, keeps letters and numbers, replaces non-Latin characters with "#", and replaces punctuation with "_"
        """
        safe = u''
        nkfd_form = unicodedata.normalize('NFKD', self.title) #unaccent accented letters
        for c in nkfd_form:
            ccat = unicodedata.category(c)
            #print ccat
            if ccat.startswith('L') or  ccat.startswith('N'): # only letters and numbers
                if ord(c) > 127:
                    safe = safe + '#' #a non latin script letter or number
                else:
                    safe = safe + c
            elif not unicodedata.combining(c): #not accents (combining forms)
                safe = safe + '_' #punctuation
        return safe

    def last_campaign(self):
        # stash away the last campaign to prevent repeated lookups
        if hasattr(self, '_last_campaign_'):
            return self._last_campaign_
        try:
            self._last_campaign_ = self.campaigns.order_by('-created')[0]
        except IndexError:
            self._last_campaign_ = None
        return self._last_campaign_
        
    @property
    def preferred_edition(self):
        if self.selected_edition:
            return self.selected_edition
        if self.last_campaign():
            if self.last_campaign().edition:
                self.selected_edition = self.last_campaign().edition
                self.save()
                return self.last_campaign().edition
        try:
            self.selected_edition = self.editions.all().order_by('-cover_image', '-created')[0] # prefer editions with covers
            self.save()
            return self.selected_edition 
        except IndexError:
            #should only happen if there are no editions for the work, 
            #which can happen when works are being merged
            try:
                return WasWork.objects.get(was=self.id).work.preferred_edition
            except WasWork.DoesNotExist:
                #should not happen
                logger.warning('work {} has no edition'.format(self.id))
                return None
        
    def last_campaign_status(self):
        campaign = self.last_campaign()
        if campaign:
            status = campaign.status
        else:
            if self.first_ebook():
                status = "Available"
            else:
                status = "No campaign yet"
        return status

    def percent_unglued(self):
        status = 0
        campaign = self.last_campaign()
        if campaign is not None:
            if(campaign.status == 'SUCCESSFUL'):
                status = 6
            elif(campaign.status == 'ACTIVE'):
                if campaign.target is not None:
                    target = float(campaign.target)
                else:
                    #shouldn't happen, but did once because of a failed pdf conversion
                    return 0
                if target <= 0:
                    status = 6
                else:
                    if campaign.type == BUY2UNGLUE:
                        status = int( 6 - 6*campaign.left/campaign.target)
                    else:
                        status = int(float(campaign.current_total)*6/target)
                    if status >= 6:
                        status = 6
        return status

    def percent_of_goal(self):
        campaign = self.last_campaign()
        return 0 if campaign is None else campaign.percent_of_goal()
    
    def ebooks_all(self):
        return self.ebooks(all=True)
        
    def ebooks(self, all=False):
        if all:
            return Ebook.objects.filter(edition__work=self).order_by('-created')
        else:
            return Ebook.objects.filter(edition__work=self,active=True).order_by('-created')

    def ebookfiles(self):
        return EbookFile.objects.filter(edition__work=self).exclude(file='').order_by('-created')

    def epubfiles(self):
        # filter out non-epub because that's what booxtream accepts 
        return EbookFile.objects.filter(edition__work=self, format='epub').exclude(file='').order_by('-created')

    def mobifiles(self):
        return EbookFile.objects.filter(edition__work=self, format='mobi').exclude(file='').order_by('-created')

    def pdffiles(self):
        return EbookFile.objects.filter(edition__work=self, format='pdf').exclude(file='').order_by('-created')

    def formats(self):
        fmts=[]
        for fmt in ['pdf', 'epub', 'mobi', 'html']:
            for ebook in self.ebooks().filter(format=fmt):
                fmts.append(fmt)
                break
        return fmts
    
    def make_ebooks_from_ebfs(self, add_ask=True):
        # either the ebf has been uploaded or a created (perhaps an ask was added or mobi generated)
        if self.last_campaign().type != THANKS:  # just to make sure that ebf's can be unglued by mistake
            return
        ebfs=EbookFile.objects.filter(edition__work=self).exclude(file='').order_by('-created')
        done_formats= []
        for ebf in ebfs:
            previous_ebooks=Ebook.objects.filter(url= ebf.file.url,) 
            try:
                previous_ebook = previous_ebooks[0]
                for eb in previous_ebooks[1:]:  #housekeeping
                        eb.deactivate()
            except IndexError:
                previous_ebook = None
            
            if ebf.format not in done_formats:
                if ebf.asking==add_ask or ebf.format=='mobi':
                    if previous_ebook:
                        previous_ebook.activate()
                    else:
                        ebook=Ebook.objects.get_or_create(
                                edition=ebf.edition, 
                                format=ebf.format, 
                                rights=self.last_campaign().license, 
                                provider="Unglue.it",
                                url= ebf.file.url,
                                )
                    done_formats.append(ebf.format)
                elif previous_ebook:
                    previous_ebook.deactivate()
            elif previous_ebook:
                previous_ebook.deactivate()
        return 
        
    def remove_old_ebooks(self):
        old=Ebook.objects.filter(edition__work=self, active=True).order_by('-created')
        done_formats= []
        for eb in old:
            if eb.format in done_formats:
                eb.deactivate()
            else:
                done_formats.append(eb.format)
        null_files=EbookFile.objects.filter(edition__work=self, file='')
        for ebf in null_files:
            ebf.file.delete()
            ebf.delete()
        
    @property
    def download_count(self):
        dlc=0
        for ebook in self.ebooks(all=True):
            dlc += ebook.download_count
        return dlc
            
    def first_pdf(self):
        return self.first_ebook('pdf')

    def first_epub(self):
        return self.first_ebook('epub')

    def first_pdf_url(self):
        try:
            url = self.first_ebook('pdf').url
            return url
        except:
            return None

    def first_epub_url(self):
        try:
            url = self.first_ebook('epub').url
            return url
        except:
            return None

    def first_ebook(self, ebook_format=None):
        if ebook_format:
            for ebook in self.ebooks().filter(format=ebook_format):
                return ebook
        else:
            for ebook in self.ebooks():
                return ebook

    def wished_by(self):
        return User.objects.filter(wishlist__works__in=[self])
        
    def update_num_wishes(self):
        self.num_wishes = Wishes.objects.filter(work=self).count()
        self.save()

    def priority(self):
        if self.last_campaign():
            return 5
        freedom = 1 if self.is_free else 0
        wishing = int(math.log(self.num_wishes )) + 1 if self.num_wishes else 0
        return min( freedom + wishing, 5 )

    def first_oclc(self):
        if self.preferred_edition == None:
            return ''
        preferred_id=self.preferred_edition.oclc
        if preferred_id:
            return preferred_id
        try:
            return self.identifiers.filter(type='oclc')[0].value
        except IndexError:
            return ''

    def first_isbn_13(self):
        if self.preferred_edition == None:
            return ''
        preferred_id=self.preferred_edition.isbn_13
        if preferred_id:
            return preferred_id
        try:
            return self.identifiers.filter(type='isbn')[0].value
        except IndexError:
            return ''
    
    @property
    def earliest_publication_date(self):
        for edition in Edition.objects.filter(work=self, publication_date__isnull=False).order_by('publication_date'):
            if edition.publication_date and len(edition.publication_date)>=4:
                return edition.publication_date
        
    @property
    def publication_date(self):
        if self.publication_range:
            return  self.publication_range
        for edition in Edition.objects.filter(work=self, publication_date__isnull=False).order_by('publication_date'):
            if edition.publication_date:
                try:
                    earliest_publication = edition.publication_date[:4]
                except IndexError:
                    continue
                latest_publication = None
                for edition in Edition.objects.filter(work=self, publication_date__isnull=False).order_by('-publication_date'):
                    if edition.publication_date:
                        try:
                            latest_publication =  edition.publication_date[:4]
                        except IndexError:
                            continue
                        break
                if earliest_publication == latest_publication:
                    publication_range = earliest_publication
                else:
                    publication_range = earliest_publication + "-" + latest_publication
                self.publication_range = publication_range  
                self.save()
                return publication_range
        return ''
        
    @property
    def has_unglued_edition(self):
        """
        allows us to distinguish successful campaigns with ebooks still in progress from successful campaigns with ebooks available
        """
        if self.ebooks().filter(edition__unglued=True):
            return True
        return False
        
    @property
    def user_with_rights(self):
        """
        return queryset of users (should be at most one) who act for rights holders with active claims to the work
        """
        claims = self.claim.filter(status='active')
        assert claims.count() < 2, "There is more than one active claim on %r" % self.title
        try:
            return claims[0].user
        except:
            return False

    def get_absolute_url(self):
        return reverse('work', args=[str(self.id)])
        
    def publishers(self):
        # returns a set of publishers associated with this Work
        return Publisher.objects.filter(name__editions__work=self).distinct()

    def create_offers(self):
        for choice in Offer.CHOICES:
            if not self.offers.filter(license=choice[0]):
                self.offers.create(license=choice[0],active=True,price=Decimal(10))
        return self.offers.all()
    
    def get_lib_license(self,user):
        lib_user=(lib.user for lib in user.profile.libraries)
        return self.get_user_license(lib_user)
        
    def borrowable(self, user):
        if user.is_anonymous():
            return False
        lib_license=self.get_lib_license(user)
        if lib_license and lib_license.borrowable:
            return True
        return False
    
    def lib_thanked(self, user):
        if user.is_anonymous():
            return False
        lib_license=self.get_lib_license(user)
        if lib_license and lib_license.thanked:
            return True
        return False
    
    def in_library(self,user):
        if user.is_anonymous():
            return False
        lib_license=self.get_lib_license(user)
        if lib_license and lib_license.acqs.count():
            return True
        return False

    @property
    def lib_acqs(self):
        return  self.acqs.filter(license=LIBRARY)

    @property
    def test_acqs(self):
        return  self.acqs.filter(license=TESTING).order_by('-created')

    class user_license:
        acqs=Acq.objects.none()
        def __init__(self,acqs):
            self.acqs=acqs
        
        @property
        def is_active(self):
            return  self.acqs.filter(expires__isnull = True).count()>0 or self.acqs.filter(expires__gt= now()).count()>0
        
        @property
        def borrowed(self):
            loans =  self.acqs.filter(license=BORROWED,expires__gt= now())
            if loans.count()==0:
                return None
            else:
                return loans[0]
                
        @property
        def purchased(self):
            purchases =  self.acqs.filter(license=INDIVIDUAL, expires__isnull = True)
            if purchases.count()==0:
                return None
            else:
                return purchases[0]

        @property
        def thanked(self):
            purchases =  self.acqs.filter(license=THANKED)
            if purchases.count()==0:
                return None
            else:
                return purchases[0]

        @property
        def lib_acqs(self):
            return  self.acqs.filter(license=LIBRARY)
        
        @property
        def next_acq(self): 
            """ This is the next available copy in the user's libraries"""
            loans = self.acqs.filter(license=LIBRARY, refreshes__gt=now()).order_by('refreshes')
            if loans.count()==0:
                return None
            else:
                return loans[0]
                
        @property
        def borrowable(self):
            return  self.acqs.filter(license=LIBRARY, refreshes__lt=now()).count()>0
            
        @property
        def thanked(self):
            return  self.acqs.filter(license=THANKED).count()>0
            
        @property
        def borrowable_acq(self):
            for acq in self.acqs.filter(license=LIBRARY, refreshes__lt=now()):
                return acq
            else:
                return None
        
        @property       
        def is_duplicate(self):
            # does user have two individual licenses?
            pending = self.acqs.filter(license=INDIVIDUAL, expires__isnull = True, gifts__used__isnull = True).count()
            return self.acqs.filter(license=INDIVIDUAL, expires__isnull = True).count() > pending
        
    
    def get_user_license(self, user):
        """ This is all the acqs, wrapped in user_license object for the work, user(s) """
        if user==None:
            return None
        if hasattr(user, 'is_anonymous'):
            if user.is_anonymous():
                return None
            return self.user_license(self.acqs.filter(user=user))
        else:
            # assume it's several users
            return self.user_license(self.acqs.filter(user__in=user))
    
    @property
    def has_marc(self):
        for record in  NewMARC.objects.filter(edition__work=self):
            return True
        return False
        
    ### for compatibility with MARC output
    def marc_records(self):
        record_list = []
        record_list.extend(NewMARC.objects.filter(edition__work=self))
        for obj in record_list:
            break
        else:
            for ebook in self.ebooks():
                record_list.append(ebook.edition)
                break
        return record_list
            
        
                
class Author(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, unique=True)
    editions = models.ManyToManyField("Edition", related_name="authors", through="Relator")

    def __unicode__(self):
        return self.name
    
    @property
    def last_name_first(self):
        names = self.name.rsplit()
        if len(names) == 0:
            return ''
        elif len(names) == 1:
            return names[0]
        elif len(names) == 2:
            return names[1] + ", " + names[0]
        else:
            reversed_name= names[-1]+","
            for name in names[0:-1]:
                reversed_name+=" "
                reversed_name+=name
            return reversed_name

class Relation(models.Model):
    code = models.CharField(max_length=3, blank=False, db_index=True, unique=True)
    name = models.CharField(max_length=30, blank=True,)
    
class Relator(models.Model):
    relation =  models.ForeignKey('Relation', default=1) #first relation should have code='aut'
    author  = models.ForeignKey('Author')
    edition = models.ForeignKey('Edition', related_name='relators')
    class Meta:
        db_table = 'core_author_editions'
        
    @property
    def name(self):
        if self.relation.code == 'aut':
            return self.author.name
        else:
            return "%s (%s)" % (self.author.name, self.relation.name)
            
    def set (self, relation_code):
        if self.relation.code != relation_code:
            try:
                self.relation = Relation.objects.get(code = relation_code)
                self.save()
            except Relation.DoesNotExist:
                logger.warning("relation not found: code = %s" % relation_code)
        
class Subject(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200, unique=True)
    works = models.ManyToManyField("Work", related_name="subjects")
    is_visible = models.BooleanField(default = True)
    authority = models.CharField(max_length=10, blank=False, default="")

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name
    
    
    @property 
    def kw(self):
        return 'kw.%s' % self.name
        
    def free_works(self):
        return self.works.filter( is_free = True )
    
class Edition(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=1000)
    publisher_name = models.ForeignKey("PublisherName", related_name="editions", null=True)
    publication_date = models.CharField(max_length=50, null=True, blank=True, db_index=True,)
    work = models.ForeignKey("Work", related_name="editions", null=True)
    cover_image = models.URLField(null=True, blank=True)
    unglued = models.BooleanField(default=False)

    def __unicode__(self):
        if self.isbn_13:
            return "%s (ISBN %s) %s" % (self.title, self.isbn_13, self.publisher)
        if self.oclc:
            return "%s (OCLC %s) %s" % (self.title, self.oclc, self.publisher)
        if self.googlebooks_id:
            return "%s (GOOG %s) %s" % (self.title, self.googlebooks_id, self.publisher)
        else:
            return "%s (GLUE %s) %s" % (self.title, self.id, self.publisher)

    def cover_image_large(self):
        #550 pixel high image
        if self.cover_image: 
            im = get_thumbnail(self.cover_image, 'x550', crop='noop', quality=95)  
            if im.exists():  
                return im.url
        elif self.googlebooks_id:
            url = "https://encrypted.google.com/books?id=%s&printsec=frontcover&img=1&zoom=0" % self.googlebooks_id
            im = get_thumbnail(url, 'x550', crop='noop', quality=95) 
            if not im.exists() or im.storage.size(im.name)==16392: # check for "image not available" image
                url = "https://encrypted.google.com/books?id=%s&printsec=frontcover&img=1&zoom=1" % self.googlebooks_id
                im = get_thumbnail(url, 'x550', crop='noop', quality=95) 
            if im.exists():
                return im.url
            else:
                return ''
        else:
            return ''
            
    def cover_image_small(self):
        #80 pixel high image
        if self.cover_image: 
            im = get_thumbnail(self.cover_image, 'x80', crop='noop', quality=95)       
            if im.exists():
                return im.url
        if self.googlebooks_id:
            return "https://encrypted.google.com/books?id=%s&printsec=frontcover&img=1&zoom=5" % self.googlebooks_id
        else:
            return ''
            
    def cover_image_thumbnail(self):
        #128 pixel wide image
        if self.cover_image:        
            im = get_thumbnail(self.cover_image, '128', crop='noop', quality=95) 
            if im.exists():
                return im.url      
        if self.googlebooks_id:
            return "https://encrypted.google.com/books?id=%s&printsec=frontcover&img=1&zoom=1" % self.googlebooks_id
        else:
            return ''
    
    def has_cover_image(self):
        if self.cover_image:        
            return self.cover_image      
        elif self.googlebooks_id:
            return True
        else:
            return False
    
    @property
    def publisher(self):
        if self.publisher_name:
            return self.publisher_name.name
        return ''
        
    @property
    def isbn_10(self):
        return regluit.core.isbn.convert_13_to_10(self.isbn_13)
    
    def id_for(self,type):
        if not self.pk:
            return ''
        try:
            return self.identifiers.filter(type=type)[0].value
        except IndexError:
            return ''

    @property
    def isbn_13(self):
        return self.id_for('isbn')
        
    @property
    def googlebooks_id(self):
        return self.id_for('goog')

    @property
    def librarything_id(self):
        return self.id_for('thng')

    @property
    def oclc(self):
        return self.id_for('oclc')

    @property
    def goodreads_id(self):
        return self.id_for('gdrd')

    @property 
    def http_id(self):
        return self.id_for('http')

    @staticmethod
    def get_by_isbn( isbn):
        if len(isbn)==10:
            isbn=regluit.core.isbn.convert_10_to_13(isbn)
        try:
            return Identifier.objects.get( type='isbn', value=isbn ).edition
        except Identifier.DoesNotExist:
            return None
    
    def add_author(self, author_name, relation='aut'):
        if author_name:
            (author, created) = Author.objects.get_or_create(name=author_name)
            (relation,created) = Relation.objects.get_or_create(code=relation)
            (new_relator,created) = Relator.objects.get_or_create(author=author, edition=self)
            if new_relator.relation != relation:
                new_relator.relation = relation
                new_relator.save()

    def remove_author(self, author):
        if author:
            try:
                relator = Relator.objects.get(author=author, edition=self)
                relator.delete()
            except Relator.DoesNotExist:
                pass

    def set_publisher(self,publisher_name):
        if publisher_name and publisher_name != '':
            try:
                pub_name = PublisherName.objects.get(name=publisher_name)
                if pub_name.publisher:
                    pub_name = pub_name.publisher.name
            except PublisherName.DoesNotExist:
                pub_name = PublisherName.objects.create(name=publisher_name)
                pub_name.save()
                
            self.publisher_name = pub_name
            self.save()

    #### following methods for compatibility with marc outputter
    def downloads(self):
        return self.ebooks.filter(active=True)

    def download_via_url(self):
        return settings.BASE_URL_SECURE + reverse('download', args=[self.work.id])
        
    def authnames(self):
        return [auth.last_name_first for auth in self.authors.all()]
    
    @property
    def license(self):
        try:
            return self.ebooks.all()[0].rights
        except:
            return None
    
    @property
    def funding_info(self): 
        if self.ebooks.all().count()==0:
            return ''  
        if self.unglued:
            return 'The book is available as a free download thanks to the generous support of interested readers and organizations, who made donations using the crowd-funding website Unglue.it.'
        else:
            if self.ebooks.all()[0].rights in cc.LICENSE_LIST:
                return 'The book is available as a free download thanks to a Creative Commons license.'
            else:
                return 'The book is available as a free download because it is in the Public Domain.'
    
    @property
    def description(self): 
        return self.work.description


class Publisher(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.ForeignKey('PublisherName', related_name='key_publisher')
    url = models.URLField(max_length=1024, null=True, blank=True)
    logo_url = models.URLField(max_length=1024, null=True, blank=True)
    description = models.TextField(default='', null=True, blank=True)

    def __unicode__(self):
        return self.name.name

class PublisherName(models.Model):
    name = models.CharField(max_length=255,  blank=False, unique=True)
    
    publisher =  models.ForeignKey('Publisher', related_name='alternate_names', null=True)

    def __unicode__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        super(PublisherName, self).save(*args, **kwargs) # Call the "real" save() method.
        if self.publisher and self != self.publisher.name:
            #this name is an alias, repoint all editions with this name to the other.
            for edition in Edition.objects.filter(publisher_name=self):
                edition.publisher_name = self.publisher.name
                edition.save()
            

class WasWork(models.Model):
    work = models.ForeignKey('Work')
    was = models.IntegerField(unique = True)
    moved = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)

def safe_get_work(work_id):
    """
    use this rather than querying the db directly for a work by id
    """
    try:
        work = Work.objects.get(id = work_id)
    except Work.DoesNotExist:
        try:
            work = WasWork.objects.get(was = work_id).work
        except WasWork.DoesNotExist:
            raise Work.DoesNotExist()
    except ValueError:
        #work_id is not a number
        raise Work.DoesNotExist()
    return work

FORMAT_CHOICES = (('pdf','PDF'),( 'epub','EPUB'), ('html','HTML'), ('text','TEXT'), ('mobi','MOBI'))

def path_for_file(instance, filename):
    return "ebf/{}.{}".format(uuid.uuid4().get_hex(), instance.format)
    
class EbookFile(models.Model):
    file = models.FileField(upload_to=path_for_file)
    format = models.CharField(max_length=25, choices = FORMAT_CHOICES)
    edition = models.ForeignKey('Edition', related_name='ebook_files')
    created =  models.DateTimeField(auto_now_add=True)
    asking = models.BooleanField(default=False)
    
    def check_file(self):
        if self.format == 'epub':
            return test_epub(self.file)
        return None
    
    @property
    def active(self):
        try:
            return Ebook.objects.filter(url=self.file.url)[0].active
        except:
            return False

send_to_kindle_limit=7492232

class Ebook(models.Model):
    FORMAT_CHOICES = settings.FORMATS
    RIGHTS_CHOICES = cc.CHOICES
    url = models.URLField(max_length=1024) #change to unique?
    created = models.DateTimeField(auto_now_add=True, db_index=True,)
    format = models.CharField(max_length=25, choices = FORMAT_CHOICES)
    provider = models.CharField(max_length=255)
    download_count = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    filesize = models.PositiveIntegerField(null=True)
    version = None #placeholder
    
    # use 'PD-US', 'CC BY', 'CC BY-NC-SA', 'CC BY-NC-ND', 'CC BY-NC', 'CC BY-ND', 'CC BY-SA', 'CC0'
    rights = models.CharField(max_length=255, null=True, choices = RIGHTS_CHOICES, db_index=True)
    edition = models.ForeignKey('Edition', related_name='ebooks')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)

    def kindle_sendable(self):
        if not self.filesize or self.filesize < send_to_kindle_limit:
            return True
        else:
            return False
    
    def get_archive(self): # returns an archived file
        if self.edition.ebook_files.filter(format=self.format).count()==0:
            if self.provider is not 'Unglue.it':
                try:
                    r=urllib2.urlopen(self.url)
                    try:
                        self.filesize = int(r.info().getheaders("Content-Length")[0])
                        if self.save:
                            self.filesize =  self.filesize if self.filesize < 2147483647 else 2147483647  # largest safe positive integer
                            self.save()
                        ebf=EbookFile.objects.create(edition=self.edition, format=self.format)
                        ebf.file.save(path_for_file(ebf,None),ContentFile(r.read()))
                        ebf.file.close()
                        ebf.save()
                        ebf.file.open()
                        return ebf.file
                    except IndexError:
                        # response has no Content-Length header probably a bad link
                        logging.error( 'Bad link error: {}'.format(self.url) )
                except IOError:
                    logger.error(u'could not open {}'.format(self.url) )
            else:
                # this shouldn't happen, except in testing perhaps
                logger.error(u'couldn\'t find ebookfile for {}'.format(self.url) )
                # try the url instead
                f = urllib.urlopen(self.url)
                return f
        else:
            ebf = self.edition.ebook_files.filter(format=self.format).order_by('-created')[0]
            try:
                ebf.file.open()
            except ValueError:
                logger.error(u'couldn\'t open EbookFile {}'.format(ebf.id) )
                return None
            except IOError:
                logger.error(u'EbookFile {} does not exist'.format(ebf.id) )
                return None
            return ebf.file
        
    def set_provider(self):
        self.provider=Ebook.infer_provider(self.url)
        return self.provider
        
    @property
    def rights_badge(self):
        if self.rights is None :
            return cc.CCLicense.badge('PD-US')
        return cc.CCLicense.badge(self.rights)
    
    @staticmethod
    def infer_provider( url):
        if not url:
            return None
        # provider derived from url. returns provider value. remember to call save() afterward
        if re.match('https?://books.google.com/', url):
            provider='Google Books'
        elif re.match('https?://www.gutenberg.org/', url):
            provider='Project Gutenberg'
        elif re.match('https?://(www\.|)archive.org/', url): 
            provider='Internet Archive'
        elif url.startswith('http://hdl.handle.net/2027/') or url.startswith('http://babel.hathitrust.org/'):
            provider='Hathitrust'
        elif re.match('https?://\w\w\.wikisource\.org/', url):
            provider='Wikisource'
        elif re.match('https?://\w\w\.wikibooks\.org/', url):
            provider='Wikibooks'
        elif re.match('https://github\.com/[^/ ]+/[^/ ]+/raw/[^ ]+', url):
            provider='Github'
        else:
            provider=None
        return provider
    
    def increment(self):
        Ebook.objects.filter(id=self.id).update(download_count = F('download_count') +1)
        
    @property
    def download_url(self):
        return settings.BASE_URL_SECURE + reverse('download_ebook',args=[self.id])

    def is_direct(self):
        return self.provider not in ('Google Books', 'Project Gutenberg')
    
    def __unicode__(self):
        return "%s (%s from %s)" % (self.edition.title, self.format, self.provider)
        
    def deactivate(self):
        self.active=False
        self.save()
    
    def activate(self):
        self.active=True
        self.save()

def set_free_flag(sender, instance, created,  **kwargs):
    if created:
        if not instance.edition.work.is_free and instance.active:
            instance.edition.work.is_free = True
            instance.edition.work.save()
    elif not instance.active and instance.edition.work.is_free==True and instance.edition.work.ebooks().count()==0:
        instance.edition.work.is_free = False
        instance.edition.work.save()
    elif instance.active and instance.edition.work.is_free==False and instance.edition.work.ebooks().count()>0:
        instance.edition.work.is_free = True
        instance.edition.work.save()
            
post_save.connect(set_free_flag,sender=Ebook)

def reset_free_flag(sender, instance, **kwargs):
    # if the Work associated with the instance Ebook currenly has only 1 Ebook, then it's no longer a free Work 
    # once the instance Ebook is deleted.  
    if instance.edition.work.ebooks().count()==1:
        instance.edition.work.is_free = False
        instance.edition.work.save()

pre_delete.connect(reset_free_flag,sender=Ebook)

class Wishlist(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='wishlist')
    works = models.ManyToManyField('Work', related_name='wishlists', through='Wishes')

    def __unicode__(self):
        return "%s's Books" % self.user.username
        
    def add_work(self, work, source, notify=False):
        try:
            w = Wishes.objects.get(wishlist=self,work=work)
        except:
            Wishes.objects.create(source=source,wishlist=self,work=work) 
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
    wishlist  = models.ForeignKey('Wishlist')
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
pledger.instance=None

def pledger2():
    if not pledger2.instance:
        pledger2.instance = Badge.objects.get(name='pledger2')
    return pledger2.instance
pledger2.instance=None

ANONYMOUS_AVATAR = '/static/images/header/avatar.png'
(NO_AVATAR, GRAVATAR, TWITTER, FACEBOOK, UNGLUEITAR) = AVATARS

class Libpref(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='libpref')
    marc_link_target = models.CharField(
        max_length=6,
        default = 'UNGLUE', 
        choices = settings.MARC_PREF_OPTIONS,
        verbose_name="MARC record link targets"
    )


class UserProfile(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile')
    tagline = models.CharField(max_length=140, blank=True)
    pic_url = models.URLField(blank=True) 
    home_url = models.URLField(blank=True)
    twitter_id = models.CharField(max_length=15, blank=True)
    facebook_id = models.BigIntegerField(null=True)
    librarything_id = models.CharField(max_length=31, blank=True)
    badges = models.ManyToManyField('Badge', related_name='holders')
    kindle_email = models.EmailField(max_length=254, blank=True)

    goodreads_user_id = models.CharField(max_length=32, null=True, blank=True)
    goodreads_user_name = models.CharField(max_length=200, null=True, blank=True)
    goodreads_auth_token = models.TextField(null=True, blank=True)
    goodreads_auth_secret = models.TextField(null=True, blank=True)
    goodreads_user_link = models.CharField(max_length=200, null=True, blank=True)  
    
    avatar_source = models.PositiveSmallIntegerField(null = True, default = UNGLUEITAR,
            choices=((NO_AVATAR,'No Avatar, Please'),(GRAVATAR,'Gravatar'),(TWITTER,'Twitter'),(FACEBOOK,'Facebook'),(UNGLUEITAR,'Unglueitar')))
    
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
        return self.user.transaction_set.exclude(status='NONE').exclude(status='Canceled',reason=None).exclude(anonymous=True).count()

    @property
    def account(self):
        # there should be only one active account per user
        accounts = self.user.account_set.filter(date_deactivated__isnull=True)
        if accounts.count()==0:
            return None
        else:
            return accounts[0]
            
    @property
    def old_account(self):
        accounts = self.user.account_set.filter(date_deactivated__isnull=False).order_by('-date_deactivated')
        if accounts.count()==0:
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
            if e.code!=215: # don't log case where user is not on a list
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
        socials= self.user.social_auth.all()
        auths={}
        for social in socials:
            auths[social.provider]=True
        return auths

    @property
    def libraries(self):
        libs=[]
        for group in self.user.groups.all():
            try:
                libs.append(group.library)
            except Library.DoesNotExist:
                pass
        return libs
            
        
class Press(models.Model):
    url =  models.URLField()
    title = models.CharField(max_length=140)
    source = models.CharField(max_length=140)
    date = models.DateField( db_index=True,)
    language = models.CharField(max_length=20, blank=True)
    highlight = models.BooleanField(default=False)
    note = models.CharField(max_length=140, blank=True)

class Gift(models.Model):
    # the acq will contain the recipient, and the work
    acq = models.ForeignKey('Acq', related_name='gifts')
    to = models.CharField(max_length = 75, blank = True) # store the email address originally sent to, not necessarily the email of the recipient
    giver = models.ForeignKey(User, related_name='gifts')
    message = models.TextField(max_length=512, default='')
    used = models.DateTimeField(null=True)

    @staticmethod
    def giftee(email, t_id):
        # return a user (create a user if necessary)
        (giftee, new_user) = User.objects.get_or_create(email=email,defaults={'username':'giftee%s' % t_id})
        giftee.new_user = new_user
        return giftee
        
    def use(self):
        self.used = now()
        self.save()
        notification.send([self.giver], "purchase_got_gift", {'gift': self }, True)
           

# this was causing a circular import problem and we do not seem to be using
# anything from regluit.core.signals after this line
# from regluit.core import signals
from regluit.payment.manager import PaymentManager

