import logging

from django.contrib import auth
from django.contrib.auth.models import User, AnonymousUser
from django.conf.urls.defaults import url
from django.db.models import Q

from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.resources import ModelResource, Resource, Bundle
from tastypie.utils import trailing_slash
from tastypie.authentication import ApiKeyAuthentication, Authentication

from regluit.core import models

logger = logging.getLogger(__name__)

class UserResource(ModelResource):
    class Meta:
        authentication = ApiKeyAuthentication()
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['username', 'first_name', 'last_name']

class EditionResource(ModelResource):
    work = fields.ForeignKey('regluit.api.resources.WorkResource', 'work')
    identifiers = fields.ToManyField('regluit.api.resources.IdentifierResource', 'identifiers')
    class Meta:
        authentication = ApiKeyAuthentication()
        queryset = models.Edition.objects.all()
        resource_name = 'edition'
        filtering = {
            "isbn_13": ALL, "identifiers": ALL_WITH_RELATIONS, 
        }
    
    def build_filters(self, filters = None):
        if filters is None:
            filters = {}
        for filter_expr, value in filters.items():
            if filter_expr.startswith('isbn_13'):
                filters['identifiers__type'] = 'isbn'
                if len(filter_expr)>7:
                    filters['identifiers__value'+filter_expr[7:]] = value
                else:
                    filters['identifiers__value'] = value
                del filters[ filter_expr ]
        return super(EditionResource, self).build_filters(filters)

class IdentifierResource(ModelResource):
    work = fields.ForeignKey('regluit.api.resources.WorkResource', 'work')
    edition = fields.ForeignKey('regluit.api.resources.EditionResource', 'edition')
    
    class Meta:
        authentication = ApiKeyAuthentication()
        queryset = models.Identifier.objects.all()
        resource_name = 'identifier'
        filtering = {
            "value": ALL, "type" : ALL,
        }
    

  
class WorkResource(ModelResource):
    editions = fields.ToManyField(EditionResource, 'editions')
    identifiers = fields.ToManyField(IdentifierResource, 'identifiers')

    class Meta:
        authentication = ApiKeyAuthentication()
        queryset = models.Work.objects.all()
        resource_name = 'work'
        filtering = {'editions': ALL_WITH_RELATIONS, 'id': ALL, 'identifiers': ALL_WITH_RELATIONS}
        ordering = ['num_wishes']
    
class CampaignResource(ModelResource):
    work = fields.ToOneField(WorkResource, 'work')

    def alter_list_data_to_serialize(self, request, data):
        """
        annotate the list of campaigns with information from the logged in
        user. note: this isn't the user identified by the api username/api_key 
        it's the the user that client might be logged into unglue.it as.
        """
        u = auth.get_user(request)
        if isinstance(u, User):
            data['meta']['logged_in_username'] = u.username
            wishlist_work_ids = [w.id for w in u.wishlist.works.all()]
        else:
            data['meta']['logged_in_username'] = None
            wishlist_work_ids = []

        for o in data['objects']:
            o.data['in_wishlist'] = o.obj.work.id in wishlist_work_ids
            # there's probably a better place up the chain (where the Campaign objects are directly available) to grab the status
            c = models.Campaign.objects.get(id=o.data["id"])
            o.data['status'] = c.status
            o.data['current_total'] = c.current_total

        # TODO: add pledging information
        return data
    
    def alter_detail_data_to_serialize(self, request, obj):
        c = models.Campaign.objects.get(id=obj.data["id"])
        obj.data['status'] = c.status
        obj.data['current_total'] = c.current_total
        return obj

    class Meta:
        authentication = ApiKeyAuthentication()
        queryset = models.Campaign.objects.all()
        resource_name = 'campaign'
        excludes = ['amazon_receiver', 'paypal_receiver']
        filtering = {
            "work": ALL_WITH_RELATIONS,
        }

class AuthorResource(ModelResource):
    works = fields.ToManyField(WorkResource, 'works')
    class Meta:
        authentication = ApiKeyAuthentication()
        queryset = models.Author.objects.all()
        resource_name = 'author'

class SubjectResource(ModelResource):
    works = fields.ToManyField(WorkResource, 'works')
    class Meta:
        authentication = ApiKeyAuthentication()
        queryset = models.Subject.objects.all()
        resource_name = 'subject'

class WishlistResource(ModelResource):
    user = fields.ToOneField(UserResource, 'user')
    works = fields.ToManyField(WorkResource, 'works')

    class Meta:
        authentication = ApiKeyAuthentication()
        queryset = models.Wishlist.objects.all()
        resource_name = 'wishlist'
