from tastypie.resources import ModelResource
from regluit.core import models

class WorkResource(ModelResource):
    class Meta:
        queryset = models.Work.objects.all()
        resource_name = 'work'