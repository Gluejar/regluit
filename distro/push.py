import logging
from datetime import datetime
from StringIO import StringIO


from regluit.core.facets import BaseFacet
from regluit.core.models import Work
from regluit.api.onix import onix_feed

from .models import Target

logger = logging.getLogger(__name__)

def push_books(target, start=datetime(1900,1,1), end=datetime(2100,1,1),max=0):
    """given a list of books this task will push the books, metadata and covers to the target
    """
    facet_class = get_target_facet(target, start=start, end=end,max=max)
    for book in facet_class.works:
        target.push(book)
        logger.info(u'{} pushed to {}'.format(book, target))

def get_target_facet(target, start=datetime(1900,1,1), end=datetime(2100,1,1),max=0):
    formats = [ format.name for format in target.formats.all() ]
    
    def format_filter(query_set):
        return query_set.filter(format__in=formats)

    def edition_format_filter(query_set):
        return query_set.filter(ebooks__format__in=formats)
        
    class TargetFacet(BaseFacet):
        def __init__(self):
            self.facet_object = self
            works = Work.objects.filter(
                    editions__ebooks__created__lt = end, 
                    editions__ebooks__created__gt = start, 
                    identifiers__type="isbn", 
                    editions__ebooks__format__in = formats,
                    editions__ebooks__provider__in = ('Internet Archive', 'Unglue.it', 'Github', 'OAPEN Library'),
                    ).distinct().order_by('-featured')
            if  max > 0 :
                self.works = works[0:max]
            else:
                self.works = works
                
        model_filters = {"Ebook": format_filter, "Edition": edition_format_filter}    
        outer_facet = None
        title = u"Free Ebooks curated by Unglue.it"
        description = "Unglue.it eBooks for {} distribution.".format( target.name )
        
    return TargetFacet()

def push_onix(target, start=datetime(1900,1,1), end=datetime(2100,1,1),max=0):
    facet_class = get_target_facet(target, start=start, end=end,max=max)
    target.push_file('unglueit_onix_{:%Y%m%d}.xml'.format(datetime.now()),StringIO(onix_feed(facet_class)))