import re
import random
from regluit.utils.localdatetime import now, date_today
from regluit.utils import crypto
from datetime import timedelta
from decimal import Decimal
from notification import models as notification
from ckeditor.fields import RichTextField

from django.db import models
from django.db.models import Q, get_model
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

import regluit
import regluit.core.isbn
from regluit.core.signals import successful_campaign, unsuccessful_campaign, wishlist_added
import binascii

from regluit.payment.parameters import TRANSACTION_STATUS_ACTIVE, TRANSACTION_STATUS_COMPLETE, TRANSACTION_STATUS_CANCELED, TRANSACTION_STATUS_ERROR, TRANSACTION_STATUS_FAILED, TRANSACTION_STATUS_INCOMPLETE

from django.db.models import Q


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
    status = models.CharField(max_length=7, choices= STATUSES, default='pending')
    
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
    
class RightsHolder(models.Model):
    created =  models.DateTimeField(auto_now_add=True)  
    email = models.CharField(max_length=100, blank=True)
    rights_holder_name = models.CharField(max_length=100, blank=False)
    owner =  models.ForeignKey(User, related_name="rights_holder", null=False )
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
    
class PledgeExtra:
    premium=None
    anonymous=False
    ack_name=''
    ack_dedication=''
    def __init__(self,premium=None,anonymous=False,ack_name='',ack_dedication=''):
        self.premium=premium
        self.anonymous=anonymous
        self.ack_name=ack_name
        self.ack_dedication=ack_dedication

class CampaignAction(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    # anticipated types: activated, withdrawn, suspended, restarted, succeeded, failed, unglued
    type = models.CharField(max_length=15)
    comment = models.TextField(null=True, blank=True)
    campaign = models.ForeignKey("Campaign", related_name="actions", null=False)

class CCLicense():
    CCCHOICES = ( 
            ('CC BY-NC-ND','CC BY-NC-ND'), 
            ('CC BY-ND','CC BY-ND'), 
            ('CC BY','CC BY'), 
            ('CC BY-NC','CC BY-NC'),
            ( 'CC BY-NC-SA','CC BY-NC-SA'),
            ( 'CC BY-SA','CC BY-SA'),
            ( 'CC0','CC0'),
        )
    CHOICES = CCCHOICES+(('PD-US', 'Public Domain, US'),)
    
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

    
class Campaign(models.Model):
    LICENSE_CHOICES = CCLicense.CCCHOICES
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=500, null=True, blank=False)
    description = RichTextField(null=True, blank=False)
    details = RichTextField(null=True, blank=True)
    target = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=False)
    license = models.CharField(max_length=255, choices = LICENSE_CHOICES, default='CC BY-NC-ND')
    left = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=False)
    deadline = models.DateTimeField()
    activated = models.DateTimeField(null=True)
    paypal_receiver = models.CharField(max_length=100, blank=True)
    amazon_receiver = models.CharField(max_length=100, blank=True)
    work = models.ForeignKey("Work", related_name="campaigns", null=False)
    managers = models.ManyToManyField(User, related_name="campaigns", null=False)
    # status: INITIALIZED, ACTIVE, SUSPENDED, WITHDRAWN, SUCCESSFUL, UNSUCCESSFUL
    status = models.CharField(max_length=15, null=True, blank=False, default="INITIALIZED")
    edition = models.ForeignKey("Edition", related_name="campaigns", null=True)
    problems = []
    
    def __unicode__(self):
        try:
            return u"Campaign for %s" % self.work.title
        except:
            return u"Campaign %s (no associated work)" % self.name
    
    def clone(self):
        """use a previous UNSUCCESSFUL campaign's data as the basis for a new campaign"""
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
        if self.status != 'INITIALIZED':
            if self.status == 'ACTIVE':
                self.problems.append(_('The campaign is already launched'))            
            else:
                self.problems.append(_('A campaign must initialized properly before it can be launched'))
            may_launch = False
        if self.target < Decimal(settings.UNGLUEIT_MINIMUM_TARGET):
            self.problems.append(_('A campaign may not be launched with a target less than $%s' % settings.UNGLUEIT_MINIMUM_TARGET))
            may_launch = False
        if self.deadline.date()- date_today() > timedelta(days=int(settings.UNGLUEIT_LONGEST_DEADLINE)):
            self.problems.append(_('The chosen closing date is more than %s days from now' % settings.UNGLUEIT_LONGEST_DEADLINE))
            may_launch = False  
        elif self.deadline.date()- date_today() < timedelta(days=0):         
            self.problems.append(_('The chosen closing date is in the past'))
            may_launch = False  
        return may_launch

    
    def update_status(self, ignore_deadline_for_success=False, send_notice=False, process_transactions=False):
        """Updates the campaign's status. returns true if updated.
        Computes UNSUCCESSFUL only after the deadline has passed
        Computes SUCCESSFUL only after the deadline has passed if ignore_deadline_for_success is TRUE -- otherwise looks just at amount of pledges accumulated
        by default, send_notice is False so that we have to explicitly send specify delivery of successful_campaign notice
        
        if process_transactions is True, also execute or cancel associated transactions
          
        """
        if not self.status=='ACTIVE':
            return False
        elif (ignore_deadline_for_success or self.deadline < now()) and self.current_total >= self.target:
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
        else:
            return False

    @property
    def current_total(self):
        if self.left is not None:
            return self.target-self.left
        else:
            return 0
            
    def update_left(self):
        p = PaymentManager()
        amount = p.query_campaign(self,summary=True, campaign_total=True)
        self.left = self.target - amount
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
            
        self.status= 'ACTIVE'
        self.left = self.target
        self.save()

        ungluers = self.work.wished_by()        
        notification.queue(ungluers, "wishlist_active", {'campaign':self, 'site': Site.objects.get_current()}, True)
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
        """nb: returns (distinct) supporter IDs, not supporter objects"""
        translist = self.transactions().filter(status=TRANSACTION_STATUS_ACTIVE).values_list('user', flat=True).distinct()
        return translist
        
    @property
    def supporters_count(self):
        # avoid transmitting the whole list if you don't need to; let the db do the count.
        active = self.transactions().filter(status=TRANSACTION_STATUS_ACTIVE).values_list('user', flat=True).distinct().count()
        complete = self.transactions().filter(status=TRANSACTION_STATUS_COMPLETE).values_list('user', flat=True).distinct().count()
        return active+complete

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
            ungluers['all'].append(transaction.user)
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
        q = Q(campaign=self) | Q(campaign__isnull=True)
        return Premium.objects.filter(q).exclude(type='XX').order_by('amount')

    def custom_premiums(self):
        """returns only the active custom premiums for the Campaign"""
        return Premium.objects.filter(campaign=self).filter(type='CU').order_by('amount')
        
    @property
    def rightsholder(self):
        """returns the name of the rights holder for an active or initialized campaign"""
        try:
            q = Q(status='ACTIVE') | Q(status='INITIALIZED')
            rh = self.work.claim.filter(q)[0].rights_holder.rights_holder_name
            return rh
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
            return self.actions.filter(type='succeeded')[0].timestamp
        return ''
    

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
    num_wishes = models.IntegerField(default=0)
    description = models.TextField(default='', null=True)

    class Meta:
        ordering = ['title']

    def __init__(self, *args, **kwargs):
        self._last_campaign = None
        super(Work, self).__init__(*args, **kwargs)

    @property
    def googlebooks_id(self):
        preferred_id=self.preferred_edition.googlebooks_id
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
        except IndexError:
            pass
        return "/static/images/generic_cover_larger.png"

    def cover_image_thumbnail(self):
        try:
            if self.preferred_edition.cover_image_thumbnail():
                return self.preferred_edition.cover_image_thumbnail()
        except IndexError:
            pass
        return "/static/images/generic_cover_larger.png"
        
    def author(self):
        # note: if you want this to be a real list, use distinct()
        # perhaps should change this to vote on authors.
        authors = list(Author.objects.filter(editions__work=self).all())
        try:
            return authors[0].name
        except:
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
        return self.editions.all()[0]
        
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
        if self.last_campaign() is not None:
            if(self.last_campaign_status() == 'SUCCESSFUL'):
                status = 6
            elif(self.last_campaign_status() == 'ACTIVE'):
                target = float(self.campaigns.order_by('-created')[0].target)
                if target <= 0:
                    status = 6
                else:
                    total = float(self.campaigns.order_by('-created')[0].current_total)
                    percent = int(total*6/target)
                    if percent >= 6:
                        status = 6
                    else:
                        status = percent
        return status

    def percent_of_goal(self):
        percent = 0
        campaign = self.last_campaign()
        if campaign is not None:
            if(campaign.status == 'SUCCESSFUL' or campaign.status == 'ACTIVE'):
                target = campaign.target
                total = campaign.current_total
                percent = int(total/target*100)
        return percent

    def ebooks(self):
        return Ebook.objects.filter(edition__work=self).order_by('-created')
    
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
    publisher = models.CharField(max_length=255, null=True, blank=True)
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

class WasWork(models.Model):
    work = models.ForeignKey('Work')
    was = models.IntegerField(unique = True)
    moved = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True)
    
    
class Ebook(models.Model):
    FORMAT_CHOICES = (('pdf','PDF'),( 'epub','EPUB'), ('html','HTML'), ('text','TEXT'), ('mobi','MOBI'))
    RIGHTS_CHOICES = CCLicense.CHOICES
    url = models.URLField(max_length=1024)
    created = models.DateTimeField(auto_now_add=True)
    format = models.CharField(max_length=25, choices = FORMAT_CHOICES)
    provider = models.CharField(max_length=255)
    
    # use 'PD-US', 'CC BY', 'CC BY-NC-SA', 'CC BY-NC-ND', 'CC BY-NC', 'CC BY-ND', 'CC BY-SA', 'CC0'
    rights = models.CharField(max_length=255, null=True, choices = RIGHTS_CHOICES)
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
        elif url.startswith('http://www.archive.org/') or url.startswith('http://archive.org/'):
            provider='Internet Archive'
        elif url.startswith('http://hdl.handle.net/2027/') or url.startswith('http://babel.hathitrust.org/'):
            provider='Hathitrust'
        elif re.match('http://\w\w\.wikisource\.org/', url):
            provider='Wikisource'
        else:
            provider=None
        return provider
    
    def __unicode__(self):
        return "%s (%s from %s)" % (self.edition.title, self.format, self.provider)

class Wishlist(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, related_name='wishlist')
    works = models.ManyToManyField('Work', related_name='wishlists', through='Wishes')

    def __unicode__(self):
        return "%s's Wishlist" % self.user.username
        
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

class UserProfile(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, related_name='profile')
    tagline = models.CharField(max_length=140, blank=True)
    pic_url =  models.URLField(blank=True) 
    home_url =  models.URLField(blank=True)
    twitter_id =  models.CharField(max_length=15, blank=True)
    facebook_id =  models.PositiveIntegerField(null=True)
    librarything_id =  models.CharField(max_length=31, blank=True)
    badges = models.ManyToManyField('Badge', related_name='holders')
    
    goodreads_user_id = models.CharField(max_length=32, null=True, blank=True)
    goodreads_user_name = models.CharField(max_length=200, null=True, blank=True)
    goodreads_auth_token = models.TextField(null=True, blank=True)
    goodreads_auth_secret = models.TextField(null=True, blank=True)
    goodreads_user_link = models.CharField(max_length=200, null=True, blank=True)  
    
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
        if last and last.ack_name:
            return last.ack_name
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
    
#class CampaignSurveyResponse(models.Model):
#    # generic
#    campaign = models.ForeignKey("Campaign", related_name="surveyresponse", null=False)
#    user = models.OneToOneField(User, related_name='surveyresponse')
#    transaction = models.ForeignKey("payment.Transaction", null=True)
#    # for OLA only
#    premium = models.ForeignKey("Premium", null=True)
#    anonymous = models.BooleanField(null=False)
#    # relevant to all campaigns since these arise from acknowledgement requirements from generic premiums 
#    name = models.CharField(max_length=140, blank=True)
#    url = models.URLField(blank=True)
#    tagline = models.CharField(max_length=140, blank=True)
#    # do we need to collect address for Rupert or will he do that once he has emails?
  
# this was causing a circular import problem and we do not seem to be using
# anything from regluit.core.signals after this line
# from regluit.core import signals
from regluit.payment.manager import PaymentManager

from social_auth.signals import pre_update
from social_auth.backends.facebook import FacebookBackend
from social_auth.backends.twitter import TwitterBackend

def facebook_extra_values(sender, user, response, details, **kwargs):
    facebook_id = response.get('id')
    user.profile.facebook_id = facebook_id
    user.profile.pic_url = 'https://graph.facebook.com/' + facebook_id + '/picture'
    user.profile.save()
    return True

def twitter_extra_values(sender, user, response, details, **kwargs):
    import requests, urllib
    
    twitter_id = response.get('screen_name')
    profile_image_url = response.get('profile_image_url_https')
    user.profile.twitter_id = twitter_id
    user.profile.pic_url = profile_image_url
    user.profile.save()
    return True

pre_update.connect(facebook_extra_values, sender=FacebookBackend)
pre_update.connect(twitter_extra_values, sender=TwitterBackend)
