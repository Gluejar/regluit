from django.db import models

class Campaign(models.Model):
    name = models.CharField(max_length=500, null=False)
    description = models.CharField(max_length=10000, null=False)
    target = models.FloatField()
    deadline = models.DateTimeField()
    paypal_receiver = models.CharField(max_length=100, null=True)
    amazon_receiver = models.CharField(max_length=100, null=True)
    work = models.ForeignKey("Work", related_name="campaign")
 
class Work(models.Model):
    title = models.CharField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True)

class Edition(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=1000)
    publisher = models.CharField(max_length=255)
    year = models.CharField(max_length=10)
    work = models.ForeignKey("Work", related_name="editions")

class Identifier(models.Model):
    name = models.CharField(max_length=10)
    value = models.CharField(max_length=500)
    edition = models.ForeignKey("Edition", related_name="identifiers")

class Author(models.Model):
    name = models.CharField(max_length=500)
    edition = models.ForeignKey("Edition", related_name="authors")
