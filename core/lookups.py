from selectable.base import ModelLookup
from selectable.registry import registry

from django.contrib.auth.models import User
from regluit.core.models import Work, PublisherName

class OwnerLookup(ModelLookup):
    model = User
    search_fields = ('username__icontains',)

class WorkLookup(ModelLookup):
    model = Work
    search_fields = ('title__istartswith',)
    filters = {'language': 'en', }
    def get_item_label(self,item):
        return "%s (%s)"%(item.title,item.id)
        
    def get_query(self, request, term):
        results = super(WorkLookup, self).get_query(request, term)
        language = request.GET.get('language', 'en')
        results = results.filter(language=language)
        return results

class PublisherNameLookup(ModelLookup):
    model = PublisherName
    search_fields = ('name__icontains',)
    def create_item(self, value):
        publisher_name, created = PublisherName.objects.get_or_create(name=value)
        publisher_name.save()
        return publisher_name
           
registry.register(OwnerLookup)
registry.register(WorkLookup)
registry.register(PublisherNameLookup)