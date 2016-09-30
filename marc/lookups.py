from django.apps import apps
from django.conf import settings
from selectable.base import ModelLookup
from selectable.registry import registry
from .models import EDITION_MODEL

class EditionLookup(ModelLookup):
    model = apps.get_model(*EDITION_MODEL.split('.'))
    search_fields = ('title__icontains',)
    filters = {'ebooks__isnull': False, }

    def get_query(self, request, term):
        return super(EditionLookup, self).get_query(request, term).distinct()

    def get_item(self, value):
        item = None
        if value:
            try:
                item = self.model.objects.get(pk=value)
            except (ValueError, self.model.DoesNotExist):
                item = None
        return item

class OwnerLookup(ModelLookup):
    model = apps.get_model(*settings.AUTH_USER_MODEL.split('.')) 
    search_fields = ('username__icontains',)

registry.register(EditionLookup)
registry.register(OwnerLookup)