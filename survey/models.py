import hashlib
import uuid
from datetime import datetime
from django.conf import settings
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save

class Landing(models.Model):
    # defines an entry point to a Feedback session
    nonce =  models.CharField(max_length=32, null=True,blank=True)
    content_type = models.ForeignKey(ContentType, null=True,blank=True)
    object_id = models.PositiveIntegerField(null=True,blank=True)
    content_object = GenericForeignKey('content_type', 'object_id') 
    label = models.CharField(max_length=64, blank=True)

    def _hash(self):
        return uuid.uuid4().hex 
    
    def __str__(self):
        return self.label

def config_landing(sender, instance, created,  **kwargs):
    if created:
        instance.nonce=instance._hash()
        instance.save()

post_save.connect(config_landing,sender=Landing)

