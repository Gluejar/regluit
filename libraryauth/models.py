from . import authenticate

from django.contrib.auth.models import User, Group
from django.db import models

class Library(models.Model):
    '''
    name and other things derive from the User
    '''
    user = models.OneToOneField(User, related_name='library')
    backend =  models.CharField(max_length=10, default='IP')
    
    def authenticate(self, enduser):
        for group in enduser.groups.all():
            if enduser.username == group.name:
                return true
        return authenticate(enduser, self)
    
    @property
    def group(self):
        (libgroup, created)=Group.objects.get_or_create(name=self.user.username)
        return libgroup

    def __unicode__(self):
        return self.user.username
    
    
