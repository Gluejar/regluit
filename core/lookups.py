from selectable.base import ModelLookup
from selectable.registry import registry

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count

from regluit.core.models import Work, PublisherName, Edition, Subject, EditionNote, Ebook
from regluit.utils.text import sanitize_line

class OwnerLookup(ModelLookup):
    model = User
    search_fields = ('username__icontains',)

class WorkLookup(ModelLookup):
    model = Work
    search_fields = ('title__istartswith',)
    def get_item_label(self, item):
        return "%s (%s, %s)"%(item.title, item.id, item.language)

    def get_item_value(self, item):
        return "%s (%s, %s)"%(item.title, item.id, item.language)

    def get_query(self, request, term):
        results = super(WorkLookup, self).get_query(request, term)
        return results

class PublisherNameLookup(ModelLookup):
    model = PublisherName
    search_fields = ('name__icontains',)
    def create_item(self, value):
        value = sanitize_line(value)
        publisher_name, created = PublisherName.objects.get_or_create(name=value)
        publisher_name.save()
        return publisher_name

class EbookLookup(ModelLookup):
    model = Ebook
    search_fields = ('edition__title__icontains',)
    filters = {'edition__isnull': False, }

    def get_item(self, value):
        item = None
        if value:
            try:
                item = Ebook.objects.get(pk=value)
            except (ValueError, Ebook.DoesNotExist):
                item = None
        return item

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
        return super(SubjectLookup, self).get_query(
            request, term
        ).annotate(Count('works')).order_by('-works__count')

class EditionNoteLookup(ModelLookup):
    model = EditionNote
    search_fields = ('note__icontains',)
    def create_item(self, value):
        new_note, created = EditionNote.objects.get_or_create(note=value)
        new_note.save()
        return new_note

class Search(models.Lookup):
    lookup_name = 'search'

    def as_mysql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return 'MATCH (%s) AGAINST (%s IN BOOLEAN MODE)' % (lhs, rhs), params

models.TextField.register_lookup(Search)

registry.register(OwnerLookup)
registry.register(WorkLookup)
registry.register(PublisherNameLookup)
registry.register(EditionLookup)
registry.register(SubjectLookup)
registry.register(EditionNoteLookup)
registry.register(EbookLookup)

