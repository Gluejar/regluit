from django.contrib.auth.models import User
from django.db.models import Q

from regluit.core import models

from tastypie.resources import ModelResource, Resource, Bundle
from tastypie import fields

import logging

# Get an instance of a specific named logger
logger = logging.getLogger(__name__)

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

# http://django-tastypie.readthedocs.org/en/latest/non_orm_data_sources.html

def get_all_isbn():
    # need to deal with isbn-13 too
    return [e.isbn_10 for e in models.Edition.objects.all() if e.isbn_10 is not None]

class IsbnObject(object):
    def __init__(self, initial=None):
        self.__dict__['_data'] = {}

        if hasattr(initial, 'items'):
            self.__dict__['_data'] = initial

    def __getattr__(self, name):
        return self._data.get(name, None)

    def __setattr__(self, name, value):
        self.__dict__['_data'][name] = value

    def to_dict(self):
        return self._data

class IsbnResource(Resource):
    
    isbn_10 = fields.CharField(attribute='isbn_10')
    title = fields.CharField(attribute='title')
    edition_id = fields.CharField(attribute='edition_id')

    class Meta:
        resource_name = 'isbn'
        object_class = IsbnObject

    # The following methods will need overriding regardless of your
    # data source.
    def get_resource_uri(self, bundle_or_obj):
        """
        Handles generating a resource URI for a single resource.

        Uses the model's ``pk`` in order to create the URI.
        """
        kwargs = {
            'resource_name': self._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.isbn_10
        else:
            kwargs['pk'] = bundle_or_obj.isbn_10

        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name

        return self._build_reverse_url("api_dispatch_detail", kwargs=kwargs)

    def get_object_list(self, request):
        """
        A hook to allow making returning the list of available objects.

        This needs to be implemented at the user level.

        ``ModelResource`` includes a full working version specific to Django's
        ``Models``.
        """
        results = []
        isbns = get_all_isbn()
        logger.info("isbn_10: %s" % (isbns))
        for isbn in isbns:
            editions = models.Edition.objects.filter(isbn_10=isbn)
            new_obj = IsbnObject()
            new_obj.isbn_10 = isbn
            new_obj.title = editions[0].title
            new_obj.edition_id = editions[0].id
            results.append(new_obj)
        logger.info("results: %s" % ([r.editions for r in results]))
        return results

    def obj_get_list(self, request=None, **kwargs):
        # Filtering disabled for brevity...
        return self.get_object_list(request)

    def obj_get(self, request=None, **kwargs):
        isbn = kwargs['pk']
        editions = models.Edition.objects.filter(isbn_10=isbn)
        new_obj = IsbnObject()
        new_obj.isbn_10 = isbn
        new_obj.title = editions[0].title
        new_obj.edition_id = editions[0].id        
        return new_obj      
        

    