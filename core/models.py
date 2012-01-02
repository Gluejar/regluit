import re
import random
import datetime
from decimal import Decimal

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

import regluit
import regluit.core.isbn

class UnglueitError(RuntimeError):
    pass

class CeleryTask(models.Model):
    created = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now())
    task_id = models.CharField(max_length=255)
    user =  models.ForeignKey(User, related_name="tasks", null=True) 
    description = models.CharField(max_length=2048, null=True)  # a description of what the task is 
    function_name = models.CharField(max_length=1024) # used to reconstitute the AsyncTask with which to get status
    function_args = models.IntegerField(null=True)  # not full generalized here -- takes only a single arg for now.
    active = models.NullBooleanField(default=True) 

    def __unicode__(self):
        return "Task %s arg:%d ID# %s %s: State %s " % (self.function_name, self.function_args, self.task_id, self.description, self.state)

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
        (u'release', u'Claim has been released.'),
    )
    created =  models.DateTimeField(auto_now_add=True)  
    rights_holder =  models.ForeignKey("RightsHolder", related_name="claim", null=False )    
    work =  models.ForeignKey("Work", related_name="claim", null=False )    
    user =  models.ForeignKey(User, related_name="claim", null=False ) 
    status = models.CharField(max_length=7, choices= STATUSES, default='pending')
    
class RightsHolder(models.Model):
    created =  models.DateTimeField(auto_now_add=True)  
    email = models.CharField(max_length=100, blank=True)
    rights_holder_name = models.CharField(max_length=100, blank=True)
    owner =  models.ForeignKey(User, related_name="rights_holder", null=False )
    def __unicode__(self):
        return self.rights_holder_name
    
class Premium(models.Model):
    PREMIUM_TYPES = ((u'00', u'Default'),(u'CU', u'Custom'))
    created =  models.DateTimeField(auto_now_add=True)  
    type = models.CharField(max_length=2, choices=PREMIUM_TYPES)
    campaign = models.ForeignKey("Campaign", related_name="premiums", null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=0, blank=False)
    description =  models.TextField(null=True, blank=False)

class CampaignAction(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    # anticipated types: activated, withdrawn, suspended, restarted, succeeded, failed, unglued
    type = models.CharField(max_length=15)
    comment = models.TextField(null=True, blank=True)
    campaign = models.ForeignKey("Campaign", related_name="actions", null=False)
    
class Campaign(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=500, null=True, blank=False)
    description = models.TextField(null=True, blank=False)
    details = models.TextField(null=True, blank=False)
    target = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=False)
    left = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=False)
    deadline = models.DateTimeField()
    activated = models.DateTimeField(null=True)
    paypal_receiver = models.CharField(max_length=100, blank=True)
    amazon_receiver = models.CharField(max_length=100, blank=True)
    work = models.ForeignKey("Work", related_name="campaigns", null=False)
    managers = models.ManyToManyField(User, related_name="campaigns", null=False)
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
        if self.deadline.date()-datetime.date.today() > datetime.timedelta(days=int(settings.UNGLUEIT_LONGEST_DEADLINE)):
            self.problems.append(_('The chosen closing date is more than %s days from now' % settings.UNGLUEIT_LONGEST_DEADLINE))
            may_launch = False  
        elif self.deadline.date()-datetime.date.today() < datetime.timedelta(days=int(settings.UNGLUEIT_SHORTEST_DEADLINE)):         
            self.problems.append(_('The chosen closing date is less than %s days from now' % settings.UNGLUEIT_SHORTEST_DEADLINE))
            may_launch = False  
        return may_launch

    
    def update_success(self):
        """  updates the campaign's status. returns true if updated
        """
        now = datetime.datetime.utcnow()
        if not self.status=='ACTIVE':
            return False
        elif self.deadline < now:
            if self.current_total >= self.target:
                self.status = 'SUCCESSFUL'
                action = CampaignAction(campaign=self, type='succeeded', comment = self.current_total) 
                action.save()
            else:
                self.status =  'UNSUCCESSFUL'
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
        
    def transactions(self, pledged=True, authorized=True):
        p = PaymentManager()
        return p.query_campaign(campaign=self, summary=False, pledged=pledged, authorized=authorized)
        
    def activate(self):
        status = self.status
        if status != 'INITIALIZED':
            raise UnglueitError(_('Campaign needs to be initialized in order to be activated'))
        self.status= 'ACTIVE'
        self.left = self.target
        self.save()
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
        """returns either the custom premiums for Campaign or any default premiums"""
        premiums = self.premiums.all()
        if premiums.count() == 0:
            premiums = Premium.objects.filter(campaign__isnull=True)
        return premiums
        
class Identifier(models.Model):
    # olib, ltwk, goog, gdrd, thng, isbn, oclc
    type = models.CharField(max_length=4, null=False)
    value =  models.CharField(max_length=31, null=False)
    work = models.ForeignKey("Work", related_name="identifiers", null=False)
    edition = models.ForeignKey("Edition", related_name="identifiers", null=True)
    
    class Meta:
        unique_together = ("type", "value")


class Work(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=1000)
    openlibrary_id = models.CharField(max_length=50, null=True)
    librarything_id = models.CharField(max_length=50, null=True)
    language = models.CharField(max_length=2, default="en", null=False)
    openlibrary_lookup = models.DateTimeField(null=True)

    class Meta:
        ordering = ['title']

    def __init__(self, *args, **kwargs):
        self._last_campaign = None
        super(Work, self).__init__(*args, **kwargs)

    @property
    def googlebooks_id(self):
        # may want to denormalize this at some point to avoid an extra query
        try:
        	return self.editions.all()[0].googlebooks_id
        except IndexError:
        	return ''

    @property
    def googlebooks_url(self):
        return "http://books.google.com/books?id=%s" % self.googlebooks_id

    @property 
    def goodreads_id(self):
        for e in self.editions.filter(goodreads_id__isnull=False):
            return e.goodreads_id

    @property
    def goodreads_url(self):
        return "http://www.goodreads.com/book/show/%s" % self.goodreads_id

    @property
    def librarything_url(self):
        return "http://www.librarything.com/work/%s" % self.librarything_id

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
        authors = list(Author.objects.filter(editions__work=self).all())
        if len(authors) == 1:
            return authors[0].name
        elif len(authors) > 1:
            return authors[0].name + ' et al.'
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
        for ebook in Ebook.objects.filter(edition__work=self, 
                                          format=ebook_format):
            return ebook
        return None

    def wished_by(self):
        return User.objects.filter(wishlist__works__in=[self])

    def longest_description(self):
        """get the longest description from an edition of this work
        """
        description = ""
        for edition in self.editions.all():
            if len(edition.description) > len(description):
                description = edition.description
        return description

    def first_isbn_13(self):
        for e in self.editions.filter(isbn_13__isnull=False):
            return e.isbn_13

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
    googlebooks_id = models.CharField(max_length=50, null=False, unique=True)
    goodreads_id = models.CharField(max_length=50, null=True)
    librarything_id = models.CharField(max_length=50, null=True)
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=1000)
    description = models.TextField(default='', null=True)
    publisher = models.CharField(max_length=255)
    publication_date = models.CharField(max_length=50)
    public_domain = models.NullBooleanField(null=True)
    isbn_13 = models.CharField(max_length=13, null=True)
    oclc = models.CharField(max_length=25, null=True)
    work = models.ForeignKey("Work", related_name="editions", null=True)

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.isbn_13)

    def cover_image_small(self):
        server_id = random.randint(0, 9)
        return "http://bks%i.books.google.com/books?id=%s&printsec=frontcover&img=1&zoom=5" % (server_id, self.googlebooks_id)

    def cover_image_thumbnail(self):
        server_id = random.randint(0, 9)
        return "http://bks%s.books.google.com/books?id=%s&printsec=frontcover&img=1&zoom=1" % (server_id, self.googlebooks_id)
    
    @property
    def isbn_10(self):
        return regluit.core.isbn.convert_13_to_10(self.isbn_13)
    
    @classmethod
    def get_by_isbn(klass, isbn):
        if length(isbn)==10:
            isbn=regluit.core.isbn.convert_10_to_13(isbn)

        for e in Edition.objects.filter( Q(isbn_13=isbn) ):
            return e
        return None

class Ebook(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    format = models.CharField(max_length=25)
    url = models.CharField(max_length=1024)
    provider = models.CharField(max_length=255)
    rights = models.CharField(max_length=255, null=True)
    edition = models.ForeignKey('Edition', related_name='ebooks')

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
    	    w.source=source
    	except:
            Wishes.objects.create(source=source,wishlist=self,work=work)        
    
    def remove_work(self, work):
        w = Wishes.objects.filter(wishlist=self, work=work)
        if w:
            w.delete()
    
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
    work = models.ForeignKey('Work')
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
    user.profile.pic_url = 'http://graph.facebook.com/' + facebook_id + '/picture'
    user.profile.save()
    return True

def twitter_extra_values(sender, user, response, details, **kwargs):
    twitter_id = response.get('screen_name')
    user.profile.twitter_id = twitter_id
    user.profile.pic_url = user.social_auth.get(provider='twitter').extra_data['profile_image_url']
    user.profile.save()
    return True

pre_update.connect(facebook_extra_values, sender=FacebookBackend)
pre_update.connect(twitter_extra_values, sender=TwitterBackend)
