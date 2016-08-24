import logging
from datetime import datetime
from StringIO import StringIO


from regluit.core.facets import BaseFacet
from regluit.core.models import Work, good_providers
from regluit.api.onix import onix_feed

from .models import Target

logger = logging.getLogger(__name__)

def push_books(target, start=datetime(1900,1,1), new=False, max=0):
    """given a list of books this task will push the books, metadata and covers to the target
    """
    facet_class = get_target_facet(target, start=start, new=new)
    pushed_books = []
    for book in facet_class.works:
        pushed = target.push(book, new=new)
        if pushed:
            pushed_books.append(book)
            logger.info(u'{} pushed to {}'.format(book, target))
        else:
            logger.info(u'{} was not pushed to {}'.format(book, target))
        if max and len(pushed_books) >= max:
            break
    facet_class.works = pushed_books
    if len(pushed_books)>0:
        push_onix(target, facet_class)

def get_target_facet(target, start=datetime(1900,1,1), new=False):
    formats = [ format.name for format in target.formats.all() ]
    
    def format_filter(query_set):
        return query_set.filter(format__in=formats)

    def edition_format_filter(query_set):
        return query_set.filter(ebooks__format__in=formats)
        
    class TargetFacet(BaseFacet):
        def __init__(self):
            self.facet_object = self
            self.works = Work.objects.filter(
                    editions__ebooks__created__gt = start, 
                    identifiers__type="isbn", 
                    editions__ebooks__format__in = formats,
                    editions__ebooks__provider__in = good_providers,
                    ).distinct().order_by('-featured')
                
        model_filters = {"Ebook": format_filter, "Edition": edition_format_filter}    
        outer_facet = None
        title = u"Free Ebooks curated by Unglue.it"
        description = "Unglue.it eBooks for {} distribution.".format( target.name )
        
    return TargetFacet()

def push_onix(target, facet_class):
    target.push_file('unglueit_onix_{:%Y%m%d%H%M%S}.xml'.format(datetime.now()),StringIO(onix_feed(facet_class)))
    
def push_all(start=datetime(1900,1,1), new=False, max=0):
    for target in Target.objects.all():
        push_books(target, start=start, new=new, max=max)
