from selectable.base import ModelLookup
from selectable.registry import registry

from django.contrib.auth.models import User

class OwnerLookup(ModelLookup):
    model = User
    search_field = 'username__icontains'
    
registry.register(OwnerLookup)