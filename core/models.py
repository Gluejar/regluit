import random
import datetime
from decimal import Decimal

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

class UnglueitError(RuntimeError):
    pass

class Premium(models.Model)
    PREMIUM_TYPES = ((u'00', u'Default'),(u'CU', u'Custom'))
    type =  = models.CharField(max_length=2, choices=PREMIUM_TYPES)
    campaign = models.ForeignKey("Campaign", related_name="premiums", blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=0, blank=False)
    description =  models.TextField(null=True, blank=False)

class Campaign(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=500, null=True, blank=False)
    description = models.TextField(null=True, blank=False)
    target = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=False)
    deadline = models.DateTimeField()
    activated = models.DateTimeField(null=True)
    suspended = models.DateTimeField(null=True)
    withdrawn = models.DateTimeField(null=True)
    suspended_reason = models.TextField(null=True, blank=True)
    withdrawn_reason = models.TextField(null=True, blank=True)
    paypal_receiver = models.CharField(max_length=100, blank=True)
    amazon_receiver = models.CharField(max_length=100, blank=True)
    work = models.ForeignKey("Work", related_name="campaigns", null=False)

    def __unicode__(self):
        try:
            return u"Campaign for %s" % self.work.title
        except:
            return u"Campaign %s (no associated work)" % self.name
        
    @property
    def status(self):
        """Returns the status of the campaign
        """
        now = datetime.datetime.utcnow()
        
        if self.activated is None:
            return 'INITIALIZED'
        elif self.suspended is not None:
            return 'SUSPENDED'
        elif self.withdrawn is not None:
            return 'WITHDRAWN'
        elif self.deadline < now:
            if self.current_total >= self.target:
                return 'SUCCESSFUL'
            else:
                return 'UNSUCCESSFUL'
        else:
            return 'ACTIVE'

    @property
    def current_total(self):
        p = PaymentManager()
        return p.query_campaign(campaign=self,summary=True)
        
    def transactions(self, pledged=True, authorized=True):
        p = PaymentManager()
        return p.query_campaign(campaign=self, summary=False, pledged=pledged, authorized=authorized)
        
    def activate(self):
        status = self.status
        if status != 'INITIALIZED':
            raise UnglueitError('Campaign needs to be initialized in order to be activated')
        self.activated = datetime.datetime.utcnow()
        self.save()
        return self   

    def suspend(self, reason):
        status = self.status
        if status != 'ACTIVE':
            raise UnglueitError('Campaign needs to be active in order to be suspended')
        self.suspended = datetime.datetime.utcnow()
        self.suspended_reason = reason
        self.save()
        return self
        
    def withdraw(self, reason):
        status = self.status
        if status != 'ACTIVE':
            raise UnglueitError('Campaign needs to be active in order to be withdrawn')
        self.withdrawn = datetime.datetime.utcnow()
        self.withdrawn_reason = reason
        self.save()
        return self

    def resume(self):
        """Change campaign status from SUSPENDED to ACTIVE.  We may want to track reason for resuming and track history"""
        status = self.status
        if status != 'SUSPENDED':
            raise UnglueitError('Campaign needs to be suspended in order to be resumed')
        self.suspended = None
        self.suspended_reason = None
        self.save()
        return self
       
    def supporters(self):
    	translist = self.transactions().values_list('user', flat=True).distinct()
    	return translist

class Work(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=1000)
    openlibrary_id = models.CharField(max_length=50, null=True)

    def cover_image_small(self):
        return self.editions.all()[0].cover_image_small()

    def cover_image_thumbnail(self):
        return self.editions.all()[0].cover_image_thumbnail()
        
    def author(self):
    	authorlist = self.editions.all()[0].authors.all()
    	if authorlist.count() == 1:
    		myauthor = authorlist[0].name
    	elif authorlist.count() > 1:
    		myauthor = authorlist[0].name + ' et al.'
    	else:
    		myauthor = ''
    	return myauthor
    	
    def last_campaign(self):
        try:
            last = self.campaigns.order_by('-created')[0]
        except:
            last = None
        return last
        
    def last_campaign_status(self):
        campaign = self.last_campaign
        if campaign:
            status = campaign.status
        else:
            status = "No campaign yet"
        return status

    def percent_unglued(self):
        status = 0
        if last_campaign is not None:
            if(self.last_campaign().status == 'SUCCESSFUL'):
                status = 6;
            elif(self.last_campaign().status == 'ACTIVE'):
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
    name = models.CharField(max_length=500)
    editions = models.ManyToManyField("Edition", related_name="subjects")

    def __unicode__(self):
        return self.name


class Edition(models.Model):
    googlebooks_id = models.CharField(max_length=50, null=False)
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=1000)
    description = models.TextField(default='', null=True)
    publisher = models.CharField(max_length=255)
    publication_date = models.CharField(max_length=50)
    isbn_10 = models.CharField(max_length=10, null=True)
    isbn_13 = models.CharField(max_length=13, null=True)
    work = models.ForeignKey("Work", related_name="editions", null=True)
    language = models.CharField(max_length=2, null=True)

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.isbn_13)

    def cover_image_small(self):
        server_id = random.randint(0, 9)
        return "http://bks%i.books.google.com/books?id=%s&printsec=frontcover&img=1&zoom=5" % (server_id, self.googlebooks_id)

    def cover_image_thumbnail(self):
        server_id = random.randint(0, 9)
        return "http://bks%s.books.google.com/books?id=%s&printsec=frontcover&img=1&zoom=1" % (server_id, self.googlebooks_id)

    @classmethod
    def get_by_isbn(klass, isbn):
        for e in Edition.objects.filter(Q(isbn_10=isbn) | Q(isbn_13=isbn)):
            return e
        return None


class Wishlist(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, related_name='wishlist')
    works = models.ManyToManyField('Work', related_name='wishlists')

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    tagline = models.CharField(max_length=140, blank=True)
    home_url =  models.URLField(blank=True)
    twitter_id =  models.CharField(max_length=15, blank=True)
    
    goodreads_user_id = models.CharField(max_length=32, null=True, blank=True)
    goodreads_user_name = models.CharField(max_length=200, null=True, blank=True)
    goodreads_auth_token = models.TextField(null=True, blank=True)
    goodreads_auth_secret = models.TextField(null=True, blank=True)
    goodreads_user_link = models.CharField(max_length=200, null=True, blank=True)        


from regluit.core import signals
from regluit.payment.manager import PaymentManager
