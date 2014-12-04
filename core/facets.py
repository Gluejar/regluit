from django.db.models import get_model
from regluit.core import cc

  
class BaseFacet(object):
    
    def __init__(self, outer_facet):
        self.facet_name = 'all'
        self.outer_facet = None
        self.model = get_model('core', 'Work')
        
        if outer_facet:
            self.outer_facet = outer_facet
    
    def _get_query_set(self):
        if self.outer_facet:
            return self.outer_facet.get_query_set()
        else:
            return self.model.objects.filter(editions__ebooks__isnull=False)
    
    def __unicode__(self):
        return unicode(self.facet_name)
    
    @property    
    def title(self):
        return self.__unicode__()
    
    @property    
    def label(self):
        return self.__unicode__()
    
    def get_query_set(self):
        return self._get_query_set()

    def get_facet_path(self):
        if self.outer_facet:
            return self.outer_facet.get_facet_path() + self.facet_name + '/'
        else:
            return self.facet_name + '/'
            
    def facets(self):
        facets=[self]
        if self.outer_facet:
            facets= self.outer_facet.facets() + facets
        return facets

    def context(self):
        return {}
    
    def template(self):
        return 'facets/default.html'
    
    _stash_others = None
    def get_other_groups(self):
        if self._stash_others != None:
            return self._stash_others
        others = []
        used = self.facets()
        for group in facet_groups:
            in_use = False
            for facet in used:
                if group.has_facet(facet.facet_name) :
                    in_use = True
                    break
            if not in_use:
                others.append(group)
        self._stash_others=others
        return others
        
class FacetGroup(object):
    # a FacetGroup should implement title, facets, has_facet(self, facet_name) and get_facet_class(self, facet_name)
    def has_facet(self, facet_name):
        return facet_name in self.facets
    def get_facets(self):
        for facet_name in self.facets:
            yield self.get_facet_class(facet_name)(None)
    
class NamedFacet(BaseFacet):
    # set_name() must be defined in classes implementing NamedFacet
    def __init__(self, outer_facet):
        super(NamedFacet, self).__init__( outer_facet )
        self.set_name() 
    
class FormatFacetGroup(FacetGroup):
    
    def __init__(self):
        super(FacetGroup,self).__init__()
        self.title = 'Format'
        self.facets = ['pdf', 'epub', 'mobi']
        
    
    def get_facet_class(self, facet_name):
        class FormatFacet(NamedFacet):
            def set_name(self):
                self.facet_name=facet_name
            def get_query_set(self):
                return self._get_query_set().filter(editions__ebooks__format=self.facet_name)
            def template(self):
                return 'facets/format.html'
        return FormatFacet    
        
        
class LicenseFacetGroup(FacetGroup):

    def __init__(self):
        super(FacetGroup,self).__init__()
        self.title = 'License'
        self.licenses = cc.LICENSE_LIST_ALL
        self.facets = cc.FACET_LIST
        
        
    def get_facet_class(self, facet_name):
        class LicenseFacet(NamedFacet):
            def set_name(self):
                self.facet_name=facet_name
                self.license = cc.ccinfo(facet_name)
            def get_query_set(self):
                return self._get_query_set().filter(editions__ebooks__rights=self.license.license)
            def template(self):
                return 'facets/license.html'
            def context(self):
                return   {
                    'license': self.license,
                    }
            def label(self):
                return self.license.__str__()
            def title(self):
                return self.license.title
        return LicenseFacet
    
facet_groups = [ FormatFacetGroup() , LicenseFacetGroup() ]

def get_facet(facet_name):
    for facet_group in facet_groups:
        if facet_group.has_facet(facet_name):
            return facet_group.get_facet_class(facet_name)
    return BaseFacet

order_by_keys = {
    'newest':['-featured', '-created'],
    'oldest':['created'],
    'featured':['-featured', '-num_wishes'],
    'popular':['-num_wishes'],
    'title':['title'],
}   
           
def get_order_by(order_by_key):
    # return the args to use as arguments for order_by
    return order_by_keys.get(order_by_key,'')