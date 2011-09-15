import logging

from django.contrib.auth.models import User
from django.conf.urls.defaults import url
from django.db.models import Q

from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.resources import ModelResource, Resource, Bundle
from tastypie.utils import trailing_slash

from regluit.core import models


logger = logging.getLogger(__name__)


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['username', 'first_name', 'last_name']

class EditionResource(ModelResource):
    class Meta:
        queryset = models.Edition.objects.all()
        resource_name = 'edition'
        filtering = {
            "isbn_10": ALL,
        }
  
class WorkResource(ModelResource):
    editions = fields.ToManyField(EditionResource, 'editions')
    class Meta:
        queryset = models.Work.objects.all()
        resource_name = 'work'
        filtering = {'editions': ALL_WITH_RELATIONS, 'id': ALL}
    
class CampaignResource(ModelResource):
    work = fields.ToOneField(WorkResource, 'work')
    class Meta:
        queryset = models.Campaign.objects.all()
        resource_name = 'campaign'
        excludes = ['amazon_receiver', 'paypal_receiver']
        filtering = {
            "work": ALL_WITH_RELATIONS,
        }

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
    edition = fields.ToManyField(EditionResource, 'editions')
    class Meta:
        queryset = models.EditionCover.objects.all()
        resource_name = 'editioncover'

class WishlistResource(ModelResource):
    user = fields.ToOneField(UserResource, 'user')
    works = fields.ToManyField(WorkResource, 'works')
    class Meta:
        queryset = models.Wishlist.objects.all()
        resource_name = 'wishlist'
