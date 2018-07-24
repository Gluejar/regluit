from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from . import bisac

class BisacHeading(MPTTModel):
    full_label = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=60, unique=False)
    notation = models.CharField(max_length=9, unique=False)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', db_index=True)

    class MPTTMeta:
        order_insertion_by = ['notation']
    
    def __unicode__(self):
        return self.full_label
        
def populate_bisac_headings():
    for key in bisac.keys():
        full_label = key[0:-10] if key.endswith(' / General') else key
        (heading, created)= BisacHeading.objects.get_or_create(full_label = full_label)
        cats = full_label.split('/')
        heading.label = cats[-1].strip()
        heading.notation = bisac[key]['notation']
        if len(cats)>1:
            parent_label = '/'.join(cats[0:-1]).strip()
            (heading.parent, created) = BisacHeading.objects.get_or_create(full_label = parent_label)
        heading.save()

def attach_dangling_branches():
    # there was no "General" heading to link to
    for heading in BisacHeading.objects.filter(notation = "", parent = None):
        cats = heading.full_label.split('/')
        heading.label = cats[-1].strip()
        if len(cats)>1:
            parent_label = '/'.join(cats[0:-1]).strip()
            (heading.parent, created) = BisacHeading.objects.get_or_create(full_label = parent_label)
        heading.save()
    
    
