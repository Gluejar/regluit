from datetime import timedelta, datetime

from django.db import models

class Boox(models.Model):
    """
    keeps a record of a file that's been watermarked
    """
    download_link_epub =  models.URLField(null=True)
    download_link_mobi =  models.URLField(null=True)
    referenceid = models.CharField(max_length=32)
    downloads_remaining = models.PositiveSmallIntegerField(default = 0)
    expirydays = models.PositiveSmallIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    
    @property
    def expired(self):
        return self.created+timedelta(days=self.expirydays) < datetime.now()
        
