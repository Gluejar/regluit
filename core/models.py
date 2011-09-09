from django.db import models
from django.contrib.auth.models import User

from regluit.core import signals

class Campaign(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=500, null=False)
    description = models.CharField(max_length=10000, null=False)
    target = models.FloatField()
    deadline = models.DateTimeField()
    paypal_receiver = models.CharField(max_length=100, null=True)
    amazon_receiver = models.CharField(max_length=100, null=True)
    work = models.ForeignKey("Work", related_name="campaign")
 
class Work(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=1000)

class WorkIdentifier(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=10)
    value = models.CharField(max_length=500)
    work = models.ForeignKey("Work", related_name="identifiers")

class Author(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=500)
    works = models.ManyToManyField("Work", related_name="authors")

    def __unicode__(self):
        return self.name

class Subject(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=500)
    works = models.ManyToManyField("Work", related_name="subjects")

class Edition(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=1000)
    description = models.TextField(default='')
    publisher = models.CharField(max_length=255)
    publication_date = models.CharField(max_length=50)
    work = models.ForeignKey("Work", related_name="editions")

    @property
    def isbn_10(self):
        return self._id('isbn_10')

    @property
    def isbn_13(self):
        return self._id('isbn_13')

    def _id(self, name):
        for i in self.identifiers.all():
            if i.name == name:
                return i.value
        return None

class EditionIdentifier(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=10)
    value = models.CharField(max_length=500)
    edition = models.ForeignKey("Edition", related_name="identifiers")

class EditionCover(models.Model):
    openlibrary_id = models.IntegerField()
    edition = models.ForeignKey("Edition", related_name="covers")

class Wishlist(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, related_name='wishlist')
    works = models.ManyToManyField('Work', related_name='wishlists')
