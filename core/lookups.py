from selectable.base import ModelLookup
from selectable.registry import registry

from django.contrib.auth.models import User
from django.db.models import Count
from regluit.core.models import Work, PublisherName, Edition, Subject, EditionNote

class OwnerLookup(ModelLookup):
    model = User
    search_fields = ('username__icontains',)

class WorkLookup(ModelLookup):
    model = Work
    search_fields = ('title__istartswith',)
    def get_item_label(self,item):
        return "%s (%s, %s)"%(item.title,item.id,item.language)
        
    def get_item_value(self,item):
        return "%s (%s, %s)"%(item.title,item.id,item.language)
        
    def get_query(self, request, term):
        results = super(WorkLookup, self).get_query(request, term)
        return results

class PublisherNameLookup(ModelLookup):
    model = PublisherName
    search_fields = ('name__icontains',)
    def create_item(self, value):
        publisher_name, created = PublisherName.objects.get_or_create(name=value)
        publisher_name.save()
        return publisher_name
           
class EditionLookup(ModelLookup):
    model = Edition
    search_fields = ('title__icontains',)
    filters = {'ebooks__isnull': False, }

    def get_query(self, request, term):
        return super(EditionLookup, self).get_query(request, term).distinct()

    def get_item(self, value):
        item = None
        if value:
            try:
                item = Edition.objects.get(pk=value)
            except (ValueError, Edition.DoesNotExist):
                item = None
        return item

class SubjectLookup(ModelLookup):
    model = Subject
    search_fields = ('name__icontains',)
    
    def get_query(self, request, term):
        return super(SubjectLookup, self).get_query( request, term).annotate(Count('works')).order_by('-works__count')

class EditionNoteLookup(ModelLookup):
    model = EditionNote
    search_fields = ('note__icontains',)
    def create_item(self, value):
        new_note, created = EditionNote.objects.get_or_create(note=value)
        new_note.save()
        return new_note

registry.register(OwnerLookup)
registry.register(WorkLookup)
registry.register(PublisherNameLookup)
registry.register(EditionLookup)
registry.register(SubjectLookup)
registry.register(EditionNoteLookup)