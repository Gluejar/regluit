from itertools import izip

from django.db.models import Count

from regluit.core import models

def list_popular():
    """Compare calculating popular works using QuerySets + distinct() and order_by() with an alternate approach """
    
    w1 = models.Work.objects.filter(wishlists__isnull=False). \
             distinct().annotate(wished=Count('wishlists')).order_by('-wished', 'id')

    # create a list of tuples of Works + the wishlist count, filter by non-zero wishlist counts, sort the list by descending
    # number of wishlists + Work.id and then blot out the wishlist count
    
    w0 = map (lambda x: x[0],
             sorted(
                     filter(lambda x: x[1] > 0,
                             [(w, w.wishlists.count()) for w in models.Work.objects.all()]
                           ) ,
                      key=lambda x: (-x[1],x[0].id)
                    )
             )

    print w1.count()
    print len(w0)
    print list(w1.all()) == w0
    
    print "difference: ", filter(lambda item: item[1][0] != item[1][1], enumerate(izip(w0,w1)))
    
def list_new():
    """Compare calculating new works using QuerySets + distinct() and order_by() with an alternate approach """
    w1 = models.Work.objects.filter(wishlists__isnull=False).distinct().order_by('-created', 'id')
    w0 = [w for w in  models.Work.objects.order_by('-created', 'id') if w.wishlists.count()]
    
    print w1.count()
    print len(w0)
    print list(w1.all()) == w0
    
    print "difference: ", filter(lambda item: item[1][0] != item[1][1], enumerate(izip(w0,w1)))