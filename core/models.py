import re
import random
from regluit.utils.localdatetime import now, date_today
from datetime import timedelta
from decimal import Decimal
from notification import models as notification

from django.db import models
from django.db.models import Q, get_model
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

import regluit
import regluit.core.isbn

class UnglueitError(RuntimeError):
    pass

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
        u'active', u'Claim has been registered and approved.'),
        (u'pending', u'Claim is pending approval.'),
        (u'release', u'Claim has not been accepted.'),
    )
    created =  models.DateTimeField(auto_now_add=True)  
    rights_holder =  models.ForeignKey("RightsHolder", related_name="claim", null=False )    
    work =  models.ForeignKey("Work", related_name="claim", null=False )    
    user =  models.ForeignKey(User, related_name="claim", null=False ) 
    status = models.CharField(max_length=7, choices= STATUSES, default='pending')
    
class RightsHolder(models.Model):
    created =  models.DateTimeField(auto_now_add=True)  
    email = models.CharField(max_length=100, blank=True)
    rights_holder_name = models.CharField(max_length=100, blank=False)
    owner =  models.ForeignKey(User, related_name="rights_holder", null=False )
    def __unicode__(self):
        return self.rights_holder_name
    
class Premium(models.Model):
    PREMIUM_TYPES = ((u'00', u'Default'),(u'CU', u'Custom'),(u'XX', u'Inactive'))
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

class CampaignAction(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    # anticipated types: activated, withdrawn, suspended, restarted, succeeded, failed, unglued
    type = models.CharField(max_length=15)
    comment = models.TextField(null=True, blank=True)
    campaign = models.ForeignKey("Campaign", related_name="actions", null=False)
    
class Campaign(models.Model):
    LICENSE_CHOICES = (('CC BY-NC-ND','CC BY-NC-ND'), 
            ('CC BY-ND','CC BY-ND'), 
            ('CC BY','CC BY'), 
            ('CC BY-NC','CC BY-NC'),
            ( 'CC BY-NC-SA','CC BY-NC-SA'),
            ( 'CC BY-SA','CC BY-SA'),
            ( 'CC0','CC0'),
        )
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=500, null=True, blank=False)
    description = models.TextField(null=True, blank=False)
    details = models.TextField(null=True, blank=False)
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
    problems = []
    
    def __unicode__(self):
        try:
            return u"Campaign for %s" % self.work.title
        except:
            return u"Campaign %s (no associated work)" % self.name
    
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
        elif self.deadline.date()- date_today() < timedelta(days=int(settings.UNGLUEIT_SHORTEST_DEADLINE)):         
            self.problems.append(_('The chosen closing date is less than %s days from now' % settings.UNGLUEIT_SHORTEST_DEADLINE))
            may_launch = False  
        return may_launch

    
    def update_status(self):
        """Updates the campaign's status. returns true if updated.  Computes SUCCESSFUL or UNSUCCESSFUL only after the deadline has passed
          
        """
        if not self.status=='ACTIVE':
            return False
        elif self.deadline < now():
            if self.current_total >= self.target:
                self.status = 'SUCCESSFUL'
                action = CampaignAction(campaign=self, type='succeeded', comment = self.current_total) 
                action.save()
                regluit.core.signals.successful_campaign.send(sender=None,campaign=self)
            else:
                self.status = 'UNSUCCESSFUL'
                action = CampaignAction(campaign=self, type='failed', comment = self.current_total) 
                action.save()
            self.save()
            return True            
        else:
            return False

    @property
    def current_total(self):
        if self.left:
            return self.target-self.left
        else:
            return 0
        
    def transactions(self, summary=False, pledged=True, authorized=True, incomplete=True, completed=True):
        p = PaymentManager()
        return p.query_campaign(campaign=self, summary=summary, pledged=pledged, authorized=authorized, incomplete=incomplete,
                                completed=completed)
        
    
    def activate(self):
        status = self.status
        if status != 'INITIALIZED':
            raise UnglueitError(_('Campaign needs to be initialized in order to be activated'))
        self.status= 'ACTIVE'
        self.left = self.target
        self.save()
        active_claim = self.work.claim.filter(status="active")[0]
        ungluers = self.work.wished_by()        
        notification.queue(ungluers, "active_campaign", {'campaign':self, 'active_claim':active_claim}, True)
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
        translist = self.transactions().values_list('user', flat=True).distinct()
        return translist

    def effective_premiums(self):
        """returns  the available premiums for the Campaign including any default premiums"""
        q = Q(campaign=self) | Q(campaign__isnull=True)
        return Premium.objects.filter(q).exclude(type='XX').order_by('amount')
        
class Identifier(models.Model):
    # olib, ltwk, goog, gdrd, thng, isbn, oclc, olwk, olib
    type = models.CharField(max_length=4, null=False)
    value =  models.CharField(max_length=31, null=False)
    work = models.ForeignKey("Work", related_name="identifiers", null=False)
    edition = models.ForeignKey("Edition", related_name="identifiers", null=True)
    
    class Meta:
        unique_together = ("type", "value")
    
    @classmethod
    def get_or_add(klass, type='goog', value=None, edition=None, work=None):
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

    class Meta:
        ordering = ['title']

    def __init__(self, *args, **kwargs):
        self._last_campaign = None
        super(Work, self).__init__(*args, **kwargs)

    @property
    def googlebooks_id(self):
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
            return self.editions.all()[0].cover_image_small()
        except IndexError:
            return "/static/images/generic_cover_larger.png"

    def cover_image_thumbnail(self):
        try:
            return self.editions.all()[0].cover_image_thumbnail()
        except IndexError:
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
                status = 6;
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
                        status = percent;
        return status;

    def percent_unglued_number(self):
        status = 0
        if self.last_campaign() is not None:
            if(self.last_campaign_status() == 'SUCCESSFUL'):
                status = 100;
            elif(self.last_campaign_status() == 'ACTIVE'):
                target = float(self.campaigns.order_by('-created')[0].target)
                if target <= 0:
                    status = 100
                else:
                    total = float(self.campaigns.order_by('-created')[0].current_total)
                    percent = int(total*100/target)
                    if percent >= 100:
                        status = 100
                    else:
                        status = percent;
        return status;
    
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

    def longest_description(self):
        """get the longest description from an edition of this work
        """
        description = ""
        for edition in self.editions.all():
            if len(edition.description) > len(description):
                description = edition.description
        return description

    def first_isbn_13(self):
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
    description = models.TextField(default='', null=True)
    publisher = models.CharField(max_length=255, null=True)
    publication_date = models.CharField(max_length=50, null=True)
    public_domain = models.NullBooleanField(null=True)
    work = models.ForeignKey("Work", related_name="editions", null=True)

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.isbn_13)

    def cover_image_small(self):
        if self.googlebooks_id:
            return "https://encrypted.google.com/books?id=%s&printsec=frontcover&img=1&zoom=5" % self.googlebooks_id
        else:
            return ''
            
    def cover_image_thumbnail(self):
        if self.googlebooks_id:
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

    @classmethod
    def get_by_isbn(klass, isbn):
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
    FORMAT_CHOICES = (('PDF','PDF'),( 'EPUB','EPUB'), ('HTML','HTML'), ('TEXT','TEXT'), ('MOBI','MOBI'))
    RIGHTS_CHOICES = (('PD-US', 'Public Domain, US'), 
            ('CC BY-NC-ND','CC BY-NC-ND'), 
            ('CC BY-ND','CC BY-ND'), 
            ('CC BY','CC BY'), 
            ('CC BY-NC','CC BY-NC'),
            ( 'CC BY-NC-SA','CC BY-NC-SA'),
            ( 'CC BY-SA','CC BY-SA'),
            ( 'CC0','CC0'),
        )
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
    
    @classmethod
    def infer_provider(klass, url):
        if not url:
            return None
        # provider derived from url. returns provider value. remember to call save() afterward
        if url.startswith('http://books.google.com/'):
            provider='Google Books'
        elif url.startswith('http://www.gutenberg.org/'):
            provider='Project Gutenberg'
        elif url.startswith('http://www.archive.org/'):
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
        
    def add_work(self, work, source):
        try:
            w = Wishes.objects.get(wishlist=self,work=work)
        except:
            Wishes.objects.create(source=source,wishlist=self,work=work) 
            work.update_num_wishes()       
    
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

class UserProfile(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, related_name='profile')
    tagline = models.CharField(max_length=140, blank=True)
    pic_url =  models.URLField(blank=True) 
    home_url =  models.URLField(blank=True)
    twitter_id =  models.CharField(max_length=15, blank=True)
    facebook_id =  models.PositiveIntegerField(null=True)
    librarything_id =  models.CharField(max_length=31, blank=True)
    
    goodreads_user_id = models.CharField(max_length=32, null=True, blank=True)
    goodreads_user_name = models.CharField(max_length=200, null=True, blank=True)
    goodreads_auth_token = models.TextField(null=True, blank=True)
    goodreads_auth_secret = models.TextField(null=True, blank=True)
    goodreads_user_link = models.CharField(max_length=200, null=True, blank=True)        


from regluit.core import signals
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
