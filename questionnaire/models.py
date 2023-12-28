import hashlib
import json
import re
import uuid
from datetime import datetime
from six import text_type as unicodestr

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse


_numre = re.compile("(\d+)([a-z]+)", re.I)


class Landing(models.Model):
    # defines an entry point to a Feedback session
    nonce =  models.CharField(max_length=32, null=True,blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True,blank=True, related_name='landings')
    object_id = models.PositiveIntegerField(null=True,blank=True)
    content_object = GenericForeignKey('content_type', 'object_id') 
    label = models.CharField(max_length=64, blank=True)
    def _hash(self):
        return uuid.uuid4().hex 
    
    def __str__(self):
        return self.label
        
    def url(self):
        try:
            return  settings.BASE_URL_SECURE + reverse('landing', args=[self.nonce])
        except AttributeError:
            # not using sites
            return  reverse('landing', args=[self.nonce])
            

