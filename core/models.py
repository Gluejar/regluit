'''
external library imports
'''
import binascii
import logging
import hashlib
import re
import random
import urllib
import urllib2

from ckeditor.fields import RichTextField
from datetime import timedelta, datetime
from decimal import Decimal
from notification import models as notification
from postmonkey import PostMonkey, MailChimpException

'''
django imports
'''
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import F, Q, get_model
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

'''
regluit imports
'''
import regluit
import regluit.core.isbn
from regluit.core.epub import personalize, ungluify, test_epub

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
    created = models.DateTimeField(auto_now_add=True, default=now())
    task_id = models.CharField(max_length=255)
    user =  models.ForeignKey(User, related_name="tasks", null=True) 
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
    user =  models.ForeignKey(User, related_name="claim", null=False ) 
    status = models.CharField(max_length=7, choices=STATUSES, default='pending')
    
    @property
    def can_open_new(self):
        # whether a campaign can be opened for this claim
        
        #must be an active claim
        if self.status != 'active':
            return False
        #can't already be a campaign
        for campaign in self.campaigns:
            if campaign.status in ['ACTIVE','INITIALIZED', 'SUCCESSFUL']:
                return False
        return True
    def  __unicode__(self):
        return self.work.title

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
    owner =  models.ForeignKey(User, related_name="rights_holder", null=False )
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
        t_model=get_model('payment','Transaction')
        return t_model.objects.filter(premium=self).count()
    @property
    def premium_remaining(self):
        t_model=get_model('payment','Transaction')
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

class CCLicense():
    CHOICES = settings.CHOICES
    
    @staticmethod
    def url(license):
        if license == 'PD-US':
            return 'http://creativecommons.org/publicdomain/mark/1.0/'
        elif license == 'CC0':
            return 'http://creativecommons.org/publicdomain/zero/1.0/'
        elif license == 'CC BY':
            return 'http://creativecommons.org/licenses/by/3.0/'
        elif license == 'CC BY-NC-ND':
            return 'http://creativecommons.org/licenses/by-nc-nd/3.0/'
        elif license == 'CC BY-NC-SA':
            return 'http://creativecommons.org/licenses/by-nc-sa/3.0/'
        elif license == 'CC BY-NC':
            return 'http://creativecommons.org/licenses/by-nc/3.0/'
        elif license == 'CC BY-SA':
            return 'http://creativecommons.org/licenses/by-sa/3.0/'
        elif license == 'CC BY-ND':
            return 'http://creativecommons.org/licenses/by-nd/3.0/'
        else:
            return ''
    
    @staticmethod
    def badge(license):
        if license == 'PD-US':
            return 'https://i.creativecommons.org/p/mark/1.0/88x31.png'
        elif license == 'CC0':
            return 'https://i.creativecommons.org/p/zero/1.0/88x31.png'
        elif license == 'CC BY':
            return 'https://i.creativecommons.org/l/by/3.0/88x31.png'
        elif license == 'CC BY-NC-ND':
            return 'https://i.creativecommons.org/l/by-nc-nd/3.0/88x31.png'
        elif license == 'CC BY-NC-SA':
            return 'https://i.creativecommons.org/l/by-nc-sa/3.0/88x31.png'
        elif license == 'CC BY-NC':
            return 'https://i.creativecommons.org/l/by-nc/3.0/88x31.png'
        elif license == 'CC BY-SA':
            return 'https://i.creativecommons.org/l/by-sa/3.0/88x31.png'
        elif license == 'CC BY-ND':
            return 'https://i.creativecommons.org/l/by-nd/3.0/88x31.png'
        else:
            return ''

    
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
    created = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField(null=True)
    refreshes = models.DateTimeField(auto_now_add=True, default=now())
    refreshes.editable=True
    refreshed = models.BooleanField(default=True)
    work = models.ForeignKey("Work", related_name='acqs', null=False)
    user = models.ForeignKey(User, related_name='acqs')
    license = models.PositiveSmallIntegerField(null = False, default = INDIVIDUAL,
            choices=CHOICES)
    watermarked = models.ForeignKey("booxtream.Boox",  null=True)
    nonce = models.CharField(max_length=32, null=True)
    
    # when the acq is a loan, this points at the library's acq it's derived from 
    lib_acq = models.ForeignKey("self", related_name="loans", null=True)
    
    def __unicode__(self):
        if self.lib_acq:
            return "%s, %s: %s for %s" % (self.work, self.get_license_display(), self.lib_acq.user, self.user)
        else:
            return "%s, %s for %s" % (self.work, self.get_license_display(), self.user,)
        
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
                'chapterfooter': 1 if do_watermark else 0,
                'disclaimer':0,
                'referenceid': '%s:%s:%s' % (self.work.id, self.user.id, self.id) if do_watermark else 'N/A',
                'kf8mobi': True,
                'epub': True,
                }
            personalized = personalize(self.work.ebookfiles()[0].file, self)
            personalized.filename.seek(0)
            self.watermarked = watermarker.platform(epubfile= personalized.filename, **params)
            self.save()
        return self.watermarked
        
    def _hash(self):
        return hashlib.md5('%s:%s:%s:%s'%(settings.TWITTER_CONSUMER_SECRET,self.user.id,self.work.id,self.created)).hexdigest() 
        
    def expire_in(self, delta):
        self.expires = now() + delta
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
    user = models.ForeignKey(User, related_name='holds', null=False)
    library = models.ForeignKey(Library, related_name='holds', null=False)

    def __unicode__(self):
        return '%s for %s at %s' % (self.work,self.user.username,self.library)
    def ahead(self):
        return Hold.objects.filter(work=self.work,library=self.library,created__lt=self.created).count()

class Campaign(models.Model):
    LICENSE_CHOICES = settings.CCCHOICES
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=500, null=True, blank=False)
    description = RichTextField(null=True, blank=False)
    details = RichTextField(null=True, blank=True)
    target = models.DecimalField(max_digits=14, decimal_places=2, null=True, default=0.00)
    license = models.CharField(max_length=255, choices = LICENSE_CHOICES, default='CC BY-NC-ND')
    left = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    deadline = models.DateTimeField(db_index=True, null=True)
    dollar_per_day = models.FloatField(null=True)
    cc_date_initial = models.DateTimeField(null=True)
    activated = models.DateTimeField(null=True)
    paypal_receiver = models.CharField(max_length=100, blank=True)
    amazon_receiver = models.CharField(max_length=100, blank=True)
    work = models.ForeignKey("Work", related_name="campaigns", null=False)
    managers = models.ManyToManyField(User, related_name="campaigns", null=False)
    # status: INITIALIZED, ACTIVE, SUSPENDED, WITHDRAWN, SUCCESSFUL, UNSUCCESSFUL
    status = models.CharField(max_length=15, null=True, blank=False, default="INITIALIZED")
    type = models.PositiveSmallIntegerField(null = False, default = REWARDS,
            choices=((REWARDS,'Rewards-based fixed duration campaign'),(BUY2UNGLUE,'Buy-to-unglue campaign'),(THANKS,'Thanks-for-ungluing campaign')))
    edition = models.ForeignKey("Edition", related_name="campaigns", null=True)
    email =  models.CharField(max_length=100, blank=True)
    publisher = models.ForeignKey("Publisher", related_name="campaigns", null=True)
    do_watermark = models.BooleanField(default=True)
    
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
                if self.work.offers.filter(price__gt=0,active=True).count()==0: 
                    self.problems.append(_('You can\'t launch a thanks-for-ungluing campaign without suggesting a contribution amount > 0' ))
                    may_launch = False  
                if EbookFile.objects.filter(edition__work=self.work).count()==0: 
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
        return CCLicense.url(self.license)

    @property
    def license_badge(self):
        return CCLicense.badge(self.license)
        
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
    
    def make_unglued_ebf(self, format, watermarked):
        ebf=EbookFile.objects.create(edition=self.work.preferred_edition, format=format)
        r=urllib2.urlopen(watermarked.download_link(format))
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
            ungluified = ungluify(self.work.ebookfiles()[0].file, self)
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

class Identifier(models.Model):
    # olib, ltwk, goog, gdrd, thng, isbn, oclc, olwk, olib, gute, glue
    type = models.CharField(max_length=4, null=False)
    value =  models.CharField(max_length=31, null=False)
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
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=1000)
    language = models.CharField(max_length=2, default="en", null=False)
    openlibrary_lookup = models.DateTimeField(null=True)
    num_wishes = models.IntegerField(default=0, db_index=True)
    description = models.TextField(default='', null=True, blank=True)

    class Meta:
        ordering = ['title']

    def __init__(self, *args, **kwargs):
        self._last_campaign = None
        super(Work, self).__init__(*args, **kwargs)

    @property
    def googlebooks_id(self):
        preferred_id=self.preferred_edition.googlebooks_id
        # note that there's always a preferred edition
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

    def cover_image_small(self):
        try:
            if self.preferred_edition.cover_image_small():
                return self.preferred_edition.cover_image_small()
        except (IndexError, AttributeError):
            pass
        return "/static/images/generic_cover_larger.png"

    def cover_image_thumbnail(self):
        try:
            if self.preferred_edition and self.preferred_edition.cover_image_thumbnail():
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
        
    def author(self):
        # assumes that they come out in the same order they go in!
        if self.authors().count()>0:
            return self.authors()[0].name
        return ''
        
    def authors_short(self):
        # assumes that they come out in the same order they go in!
        if self.authors().count()==1:
            return self.authors()[0].name
        elif self.authors().count()==2:
            return "%s and %s" % (self.authors()[0].name, self.authors()[1].name)
        elif self.authors().count()>2:
            return "%s et al." % self.authors()[0].name
        return ''

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
        if self.last_campaign():
            if self.last_campaign().edition:
                return self.last_campaign().edition
        return self.editions.all()[0] if self.editions.all().count() else None
        
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
                target = float(campaign.target)
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

    def ebooks(self):
        return Ebook.objects.filter(edition__work=self).order_by('-created')

    def ebookfiles(self):
        # filter out non-epub because that's what booxtream accepts now
        return EbookFile.objects.filter(edition__work=self, format='epub').order_by('-created')

    def make_ebooks_from_ebfs(self):
        if self.last_campaign().type != THANKS:  # just to make sure that ebf's can be unglued by mistake
            return
        ebfs=EbookFile.objects.filter(edition__work=self).order_by('-created')
        done_formats= []
        for ebf in ebfs:
            if ebf.format not in done_formats:
                ebook=Ebook.objects.create(
                        edition=ebf.edition, 
                        format=ebf.format, 
                        rights=self.last_campaign().license, 
                        provider="Unglue.it",
                        url= ebf.file.url,
                        )
                done_formats.append(ebf.format)
        return 

    @property
    def download_count(self):
        dlc=0
        for ebook in self.ebooks():
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

    def first_oclc(self):
        preferred_id=self.preferred_edition.oclc
        if preferred_id:
            return preferred_id
        try:
            return self.identifiers.filter(type='oclc')[0].value
        except IndexError:
            return ''

    def first_isbn_13(self):
        preferred_id=self.preferred_edition.isbn_13
        if preferred_id:
            return preferred_id
        try:
            return self.identifiers.filter(type='isbn')[0].value
        except IndexError:
            return ''

    @property
    def publication_date(self):
        for edition in Edition.objects.filter(work=self):
            if edition.publication_date:
                return edition.publication_date
        return ''

    @property
    def publication_date_year(self):
        try:
            return self.publication_date[:4]
        except IndexError:
            return 'unknown'

    def __unicode__(self):
        return self.title
        
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
            purchases =  self.acqs.filter(license=INDIVIDUAL)
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
        def borrowable_acq(self):
            for acq in self.acqs.filter(license=LIBRARY, refreshes__lt=now()):
                return acq
            else:
                return None
    
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
            
class Author(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=500)
    editions = models.ManyToManyField("Edition", related_name="authors")

    def __unicode__(self):
        return self.name


class Subject(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200, unique=True)
    works = models.ManyToManyField("Work", related_name="subjects")

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


class Edition(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=1000)
    publisher_name = models.ForeignKey("PublisherName", related_name="editions", null=True)
    publication_date = models.CharField(max_length=50, null=True, blank=True)
    public_domain = models.NullBooleanField(null=True, blank=True)
    work = models.ForeignKey("Work", related_name="editions", null=True)
    cover_image = models.URLField(null=True, blank=True)
    unglued = models.BooleanField(blank=True)

    def __unicode__(self):
        if self.isbn_13:
            return "%s (ISBN %s) %s" % (self.title, self.isbn_13, self.publisher)
        if self.oclc:
            return "%s (OCLC %s) %s" % (self.title, self.oclc, self.publisher)
        if self.googlebooks_id:
            return "%s (GOOG %s) %s" % (self.title, self.googlebooks_id, self.publisher)
        else:
            return "%s (GLUE %s) %s" % (self.title, self.id, self.publisher)

    def cover_image_small(self):
        if self.cover_image:        
            return self.cover_image
        elif self.googlebooks_id:
            return "https://encrypted.google.com/books?id=%s&printsec=frontcover&img=1&zoom=5" % self.googlebooks_id
        else:
            return ''
            
    def cover_image_thumbnail(self):
        if self.cover_image:        
            return self.cover_image
        elif self.googlebooks_id:
            return "https://encrypted.google.com/books?id=%s&printsec=frontcover&img=1&zoom=1" % self.googlebooks_id
        else:
            return ''
    @property
    def publisher(self):
        if self.publisher_name:
            return self.publisher_name.name
        return ''
        
    @property
    def isbn_10(self):
        return regluit.core.isbn.convert_13_to_10(self.isbn_13)
    
    @property
    def isbn_13(self):
        try:
            return self.identifiers.filter(type='isbn')[0].value
        except IndexError:
            return ''

    @property
    def googlebooks_id(self):
        try:
            return self.identifiers.filter(type='goog')[0].value
        except IndexError:
            return ''

    @property
    def librarything_id(self):
        try:
            return self.identifiers.filter(type='thng')[0].value
        except IndexError:
            return ''

    @property
    def oclc(self):
        try:
            return self.identifiers.filter(type='oclc')[0].value
        except IndexError:
            return ''

    @property
    def goodreads_id(self):
        try:
            return self.identifiers.filter(type='gdrd')[0].value
        except IndexError:
            return ''

    @staticmethod
    def get_by_isbn( isbn):
        if len(isbn)==10:
            isbn=regluit.core.isbn.convert_10_to_13(isbn)
        try:
            return Identifier.objects.get( type='isbn', value=isbn ).edition
        except Identifier.DoesNotExist:
            return None
    
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

class Publisher(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.ForeignKey('PublisherName', related_name='key_publisher')
    url = models.URLField(max_length=1024, null=True, blank=True)
    logo_url = models.URLField(max_length=1024, null=True, blank=True)
    description = models.TextField(default='', null=True, blank=True)

    def __unicode__(self):
        return self.name.name

class PublisherName(models.Model):
    name = models.CharField(max_length=255,  blank=False)
    
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
    user = models.ForeignKey(User, null=True)

FORMAT_CHOICES = (('pdf','PDF'),( 'epub','EPUB'), ('html','HTML'), ('text','TEXT'), ('mobi','MOBI'))

def path_for_file(instance, filename):
    version = EbookFile.objects.filter(edition = instance.edition, format = instance.format).count()
    hash = hashlib.md5('%s.%s.%d'%(settings.TWITTER_CONSUMER_SECRET, instance.edition.pk, version)).hexdigest()
    fn = "ebf/%s.%s"%(hash,instance.format)
    return fn
    
class EbookFile(models.Model):
    file = models.FileField(upload_to=path_for_file)
    format = models.CharField(max_length=25, choices = FORMAT_CHOICES)
    edition = models.ForeignKey('Edition', related_name='ebook_files')
    created =  models.DateTimeField(auto_now_add=True)
    
    def check_file(self):
        if self.format == 'epub':
            return test_epub(self.file)
        return None
    
class Ebook(models.Model):
    FORMAT_CHOICES = settings.FORMATS
    RIGHTS_CHOICES = settings.CCCHOICES
    url = models.URLField(max_length=1024)
    created = models.DateTimeField(auto_now_add=True)
    format = models.CharField(max_length=25, choices = FORMAT_CHOICES)
    provider = models.CharField(max_length=255)
    download_count = models.IntegerField(default=0)
    
    # use 'PD-US', 'CC BY', 'CC BY-NC-SA', 'CC BY-NC-ND', 'CC BY-NC', 'CC BY-ND', 'CC BY-SA', 'CC0'
    rights = models.CharField(max_length=255, null=True, choices = RIGHTS_CHOICES, db_index=True)
    edition = models.ForeignKey('Edition', related_name='ebooks')
    user = models.ForeignKey(User, null=True)

    def set_provider(self):
        self.provider=Ebook.infer_provider(self.url)
        return self.provider
        
    @property
    def rights_badge(self):
        if self.rights is None :
            return CCLicense.badge('PD-US')
        return CCLicense.badge(self.rights)
    
    @staticmethod
    def infer_provider( url):
        if not url:
            return None
        # provider derived from url. returns provider value. remember to call save() afterward
        if url.startswith('http://books.google.com/'):
            provider='Google Books'
        elif url.startswith('http://www.gutenberg.org/'):
            provider='Project Gutenberg'
        elif re.match('https?://(www\.|)archive.org/', url): 
            provider='Internet Archive'
        elif url.startswith('http://hdl.handle.net/2027/') or url.startswith('http://babel.hathitrust.org/'):
            provider='Hathitrust'
        elif re.match('http://\w\w\.wikisource\.org/', url):
            provider='Wikisource'
        else:
            provider=None
        return provider
    
    def increment(self):
        Ebook.objects.filter(id=self.id).update(download_count = F('download_count') +1)
        
    @property
    def download_url(self):
        return settings.BASE_URL_SECURE + reverse('download_ebook',args=[self.id])
    
    def __unicode__(self):
        return "%s (%s from %s)" % (self.edition.title, self.format, self.provider)

class Wishlist(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, related_name='wishlist')
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
    created = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=15, blank=True)
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
(NO_AVATAR, GRAVATAR, TWITTER, FACEBOOK) = (0, 1, 2, 3)

class Libpref(models.Model):
    user = models.OneToOneField(User, related_name='libpref')
    marc_link_target = models.CharField(
        max_length=6,
        default = 'UNGLUE', 
        choices = settings.MARC_PREF_OPTIONS,
        verbose_name="MARC record link targets"
    )


class UserProfile(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, related_name='profile')
    tagline = models.CharField(max_length=140, blank=True)
    pic_url = models.URLField(blank=True) 
    home_url = models.URLField(blank=True)
    twitter_id = models.CharField(max_length=15, blank=True)
    facebook_id = models.PositiveIntegerField(null=True)
    librarything_id = models.CharField(max_length=31, blank=True)
    badges = models.ManyToManyField('Badge', related_name='holders')
    kindle_email = models.EmailField(max_length=254, blank=True)

    goodreads_user_id = models.CharField(max_length=32, null=True, blank=True)
    goodreads_user_name = models.CharField(max_length=200, null=True, blank=True)
    goodreads_auth_token = models.TextField(null=True, blank=True)
    goodreads_auth_secret = models.TextField(null=True, blank=True)
    goodreads_user_link = models.CharField(max_length=200, null=True, blank=True)  
    
    avatar_source = models.PositiveSmallIntegerField(null = True, default = GRAVATAR,
            choices=((NO_AVATAR,'No Avatar, Please'),(GRAVATAR,'Gravatar'),(TWITTER,'Twitter'),(FACEBOOK,'Facebook')))
    
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
        return self.user.transaction_set.filter(status=TRANSACTION_STATUS_ACTIVE)

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
        try:
            if not self.on_ml:
                return pm.listSubscribe(id=settings.MAILCHIMP_NEWS_ID, email_address=self.user.email, **kwargs)
        except Exception, e:
            logger.error("error subscribing to mailchimp list %s" % (e))
            return False

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
        

    @property
    def avatar_url(self):
        if self.avatar_source is None or self.avatar_source is TWITTER:
            if self.pic_url:
                return self.pic_url
            else:
                return ANONYMOUS_AVATAR
        elif self.avatar_source == GRAVATAR:
            return self.gravatar()
        elif self.avatar_source == FACEBOOK and self.facebook_id != None:
            return 'https://graph.facebook.com/' + str(self.facebook_id) + '/picture'
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
    date = models.DateField()
    language = models.CharField(max_length=20, blank=True)
    highlight = models.BooleanField(default=False)
    note = models.CharField(max_length=140, blank=True)
    
class MARCRecord(models.Model):
    edition = models.ForeignKey("Edition", related_name="MARCrecords", null=True)
    # this is where the download link points to, direct link or via Unglue.it.
    link_target = models.CharField(max_length=6,choices = settings.MARC_CHOICES, default='DIRECT')
    
    @property
    def accession(self):
        zeroes = 9 - len(str(self.id))
        return 'ung' + zeroes*'0' + str(self.id)
        
    @property
    def xml_record(self):
        return self._record('xml')
        
    @property
    def mrc_record(self):
        return self._record('mrc')
        
    def _record(self, filetype):
        test = '' if '/unglue.it' in settings.BASE_URL else '_test'
        if self.link_target == 'DIRECT':
            fn = '_unglued.'
        elif self.link_target == 'UNGLUE':
            fn = '_via_unglueit.'  
        else:
            fn = '_ungluing.'
        return 'marc' + test + '/' + self.accession + fn + filetype

# this was causing a circular import problem and we do not seem to be using
# anything from regluit.core.signals after this line
# from regluit.core import signals
from regluit.payment.manager import PaymentManager

