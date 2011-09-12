from django.contrib.auth.models import User
from regluit.core import models

from tastypie.resources import ModelResource
from tastypie import fields

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['username', 'first_name', 'last_name']
    
class WorkResource(ModelResource):
    class Meta:
        queryset = models.Work.objects.all()
        resource_name = 'work'
        
class EditionResource(ModelResource):
    work = fields.ForeignKey(WorkResource, 'work')
    class Meta:
        queryset = models.Edition.objects.all()
        resource_name = 'edition'

class CampaignResource(ModelResource):
    work = fields.ForeignKey(WorkResource, 'work')
    class Meta:
        queryset = models.Campaign.objects.all()
        resource_name = 'campaign'
        excludes = ['amazon_receiver', 'paypal_receiver']
        
class AuthorResource(ModelResource):
    works = fields.ToManyField(WorkResource, 'works')
    class Meta:
        queryset = models.Author.objects.all()
        resource_name = 'author'

class SubjectResource(ModelResource):
    works = fields.ToManyField(WorkResource, 'works')
    class Meta:
        queryset = models.Subject.objects.all()
        resource_name = 'subject'

class EditionCoverResource(ModelResource):
    edition = fields.ForeignKey(EditionResource, 'edition')
    class Meta:
        queryset = models.EditionCover.objects.all()
        resource_name = 'editioncover'

class WishlistResource(ModelResource):
    user = fields.ToOneField(UserResource, 'user')
    works = fields.ToManyField(WorkResource, 'works')
    class Meta:
        queryset = models.Wishlist.objects.all()
        resource_name = 'wishlist'