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
    w1 = models.Work.objects.filter(wishlists__isnull=False).distinct().order_by('-created')
    w0 = [w for w in  models.Work.objects.order_by('-created') if w.wishlists.count()]
    
    print w1.count()
    print len(w0)
    print w0 == w1