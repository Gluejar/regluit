from regluit.core import models
from django.db.models import Q, Count, Sum
from regluit.core import userlists

from itertools import izip

def list_popular():
    work_set = models.Work.objects.annotate(wished=Count('wishlists')).order_by('-wished')
    print work_set
    
    counts={}
    counts['unglued'] = work_set.filter(editions__ebooks__isnull=False).distinct().count()
    counts['unglueing'] = work_set.filter(campaigns__status='ACTIVE').count()
    counts['wished'] = work_set.count() - counts['unglued'] - counts['unglueing']
    print counts
    
    ungluers = userlists.work_list_users(work_set,5)
    print ungluers
   
def list_new():
    works1 = models.Work.objects.filter(wishlists__isnull=False).distinct().order_by('-created')
    print works1.count()
    