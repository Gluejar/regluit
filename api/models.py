from tastypie.resources import ModelResource
from tastypie import fields
from regluit.core import models

class WorkResource(ModelResource):
    class Meta:
        queryset = models.Work.objects.all()
        resource_name = 'work'
        
class EditionResource(ModelResource):
    work = fields.ForeignKey(WorkResource, 'work')
    class Meta:
        queryset = models.Edition.objects.all()
        resource_name = 'edition'

class CampaignResource(ModelResource):
    work = fields.ForeignKey(WorkResource, 'work')
    class Meta:
        queryset = models.Campaign.objects.all()
        resource_name = 'campaign'
        
class AuthorResource(ModelResource):
    works = fields.ToManyField(WorkResource, 'works')
    class Meta:
        queryset = models.Author.objects.all()
        resource_name = 'author'

class SubjectResource(ModelResource):
    works = fields.ToManyField(WorkResource, 'works')
    class Meta:
        queryset = models.Subject.objects.all()
        resource_name = 'subject'