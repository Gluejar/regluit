import random
import datetime
from decimal import Decimal

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

class UnglueitError(RuntimeError):
    pass

class Campaign(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=500, null=False)
    description = models.TextField(null=False)
    target = models.DecimalField(max_digits=14, decimal_places=2)
    deadline = models.DateTimeField(null=False)
    activated = models.DateTimeField(null=True)
    suspended = models.DateTimeField(null=True)
    withdrawn = models.DateTimeField(null=True)
    supended_reason = models.TextField(null=True)
    withdrawn_reason = models.TextField(null=True)
    paypal_receiver = models.CharField(max_length=100, null=True)
    amazon_receiver = models.CharField(max_length=100, null=True)
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
        self.supended_reason = reason
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


class Work(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=1000)
    openlibrary_id = models.CharField(max_length=50, null=True)

    @classmethod
    def get_by_isbn(klass, isbn):
        for w in Work.objects.filter(Q(editions__isbn_10=isbn) | Q(editions__isbn_13=isbn)):
            return w
        return None

    def cover_image_small(self):
        server_id = random.randint(0, 9)
        gb_id = self.editions.all()[0].googlebooks_id
        return "http://bks%i.books.google.com/books?id=%s&printsec=frontcover&img=1&zoom=5" % (server_id, gb_id)

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

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.isbn_13)

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
    user = models.OneToOneField(User)
    tagline = models.CharField(max_length=140, blank=True)

from regluit.core import signals
from regluit.payment.manager import PaymentManager
