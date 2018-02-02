from django.apps import apps
from django.contrib.auth.models import User
from django.db.models import Q
from regluit.core import cc

class BaseFacet(object):
    facet_name = 'all'
    model_filters ={}
    
    def __init__(self, outer_facet):
        self.outer_facet = outer_facet if outer_facet else None
        self.model = apps.get_model('core', 'Work')
    
    def _get_query_set(self):
        if self.outer_facet:
            return self.outer_facet.get_query_set()
        else:
            return self.model.objects.filter(is_free=True)

    def _filter_model(self, model, query_set):
        if self.outer_facet:
            return self.outer_facet.filter_model(model, query_set)
        else:
            return query_set
    
    def __unicode__(self):
        if self.facet_name == 'all':
            return 'Free eBooks'
        return unicode(self.facet_name)
    
    @property    
    def title(self):
        return self.__unicode__()
    
    @property    
    def label(self):
        return self.__unicode__()
    
    def get_query_set(self):
        return self._get_query_set()

    def filter_model(self, model, query_set):
        model_filter =  self.model_filters.get(model,None) 
        if model_filter:
            return model_filter( self._filter_model(model, query_set))
        else:
            return self._filter_model( model, query_set)

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

    @property
    def description(self):
        return self.__unicode__()
        
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
        self.label = '{} is ...'.format(self.title)
    
    def get_facet_class(self, facet_name):
        class FormatFacet(NamedFacet):
            def set_name(self):
                self.facet_name=facet_name
            def format_filter(query_set):
                return query_set.filter(format=facet_name)
            def edition_format_filter(query_set):
                return query_set.filter(ebooks__format=facet_name)
            model_filters = {"Ebook": format_filter, "Edition": edition_format_filter}
            def get_query_set(self):
                return self._get_query_set().filter(editions__ebooks__format=self.facet_name)
            def template(self):
                return 'facets/format.html'
            @property
            def title(self):
                return "eBooks available in format: " + self.facet_name
            @property
            def description(self):
                return  "These eBooks available in %s format." % self.facet_name
        return FormatFacet    

idtitles = {'doab': 'indexed in DOAB', 'gtbg':'available in Project Gutenberg', 
            '-doab': 'not in DOAB', '-gtbg':'not from Project Gutenberg', }
idlabels = {'doab': 'DOAB', 'gtbg':'Project Gutenberg', 
            '-doab': 'not DOAB', '-gtbg':'not Project Gutenberg'}
class IdFacetGroup(FacetGroup):
    def __init__(self):
        super(FacetGroup,self).__init__()
        self.title = 'Collection'
        self.facets = idtitles.keys()
        self.label = 'Included in ...'        
    
    def get_facet_class(self, facet_name):
        class IdFacet(NamedFacet):
            def set_name(self):
                self.facet_name=facet_name
            def id_filter(query_set):
                if facet_name[0] == '-':
                    return query_set.exclude(identifiers__type=facet_name[1:])
                else:
                    return query_set.filter(identifiers__type=facet_name)
            model_filters = {}
            def get_query_set(self):
                if facet_name[0] == '-':
                    return self._get_query_set().exclude(identifiers__type=self.facet_name[1:])
                else:
                    return self._get_query_set().filter(identifiers__type=self.facet_name)
            def template(self):
                return 'facets/id.html'
            @property    
            def label(self):
                return idlabels[self.facet_name]
            @property
            def title(self):
                return idtitles[self.facet_name]
            @property
            def description(self):
                return  "These eBooks are {}.".format(idtitles[self.facet_name])
        return IdFacet    
        
        
class LicenseFacetGroup(FacetGroup):
    def __init__(self):
        super(FacetGroup,self).__init__()
        self.title = 'License'
        self.licenses = cc.LICENSE_LIST_ALL
        self.facets = cc.FACET_LIST
        self.label = '{} is ...'.format(self.title)
        
        
    def get_facet_class(self, facet_name):
        class LicenseFacet(NamedFacet):            
            def set_name(self):
                self.facet_name=facet_name
                self.license = cc.ccinfo(facet_name)
            def license_filter(query_set):
                return query_set.filter(rights=cc.ccinfo(facet_name))
            def edition_license_filter(query_set):
                return query_set.filter(ebooks__rights=cc.ccinfo(facet_name))
            model_filters = {"Ebook": license_filter, "Edition": edition_license_filter}
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
            @property
            def title(self):
                return "license: " + self.license.title
            @property
            def description(self):
                return  "These eBooks are available under the %s license." % self.facet_name
        return LicenseFacet

TOPKW = ["Fiction", "Nonfiction", "Literature",  "History", "Classic Literature", 
    "Children's literature, English", "History and criticism", "Science", "Juvenile fiction", 
    "Sociology", "Software", "Science Fiction"]

class KeywordFacetGroup(FacetGroup):
    
    def __init__(self):
        super(FacetGroup,self).__init__()
        self.title = 'Keyword'
        # make facets in TOPKW available for display
        self.facets = [('kw.%s' % kw) for kw in TOPKW]
        self.label = '{} is ...'.format(self.title)
        
    def has_facet(self, facet_name):
    
        # recognize any facet_name that starts with "kw." as a valid facet name
        return facet_name.startswith('kw.')

    def get_facet_class(self, facet_name):
        class KeywordFacet(NamedFacet):
            def set_name(self):
                self.facet_name=facet_name
                # facet_names of the form 'kw.SUBJECT' and SUBJECT is therefore the 4th character on
                self.keyword=self.facet_name[3:].replace(';', '/')
            def get_query_set(self):
                return self._get_query_set().filter(subjects__name=self.keyword)
            def template(self):
                return 'facets/keyword.html'
            @property    
            def title(self):
                return self.keyword
            @property    
            def label(self):
                return self.keyword
            @property
            def description(self):
                return  "%s eBooks" % self.keyword
        return KeywordFacet    

class SearchFacetGroup(FacetGroup):
    
    def __init__(self):
        super(FacetGroup,self).__init__()
        self.title = 'Search Term'
        # make facets in TOPKW available for display
        self.facets = []
        self.label = '{} is ...'.format(self.title)
        
    def has_facet(self, facet_name):
    
        # recognize any facet_name that starts with "s." as a valid facet name
        return facet_name.startswith('s.')

    def get_facet_class(self, facet_name):
        class KeywordFacet(NamedFacet):
            def set_name(self):
                self.facet_name=facet_name
                # facet_names of the form 's.SUBJECT' and SUBJECT is therefore the 3rd character on
                self.term=self.facet_name[2:]
            def get_query_set(self):
                return self._get_query_set().filter(
                    Q(title__icontains=self.term) | 
                    Q(editions__authors__name__icontains=self.term) | 
                    Q(subjects__name__iexact=self.term)
                    )
                 
            def template(self):
                return 'facets/search.html'
            @property    
            def title(self):
                return self.term
            @property    
            def label(self):
                return self.term
            @property
            def description(self):
                return  "eBooks for {}".format(self.term)
        return KeywordFacet    

class SupporterFacetGroup(FacetGroup):
    
    def __init__(self):
        super(FacetGroup,self).__init__()
        self.title = 'Supporter Faves'
        # make facets in TOPKW available for display
        self.facets = []
        self.label = '{} are ...'.format(self.title)
        
    def has_facet(self, facet_name):
    
        # recognize any facet_name that starts with "@" as a valid facet name
        return facet_name.startswith('@')

    def get_facet_class(self, facet_name):
        class SupporterFacet(NamedFacet):
            def set_name(self):
                self.facet_name = facet_name
                self.username = self.facet_name[1:]
                try:
                    user = User.objects.get(username=self.username)
                    self.fave_set = user.wishlist.works.all()
                except User.DoesNotExist:
                    self.fave_set = self.model.objects.none()
            
            def get_query_set(self):
                return self._get_query_set().filter(pk__in=self.fave_set)
                 
            def template(self):
                return 'facets/supporter.html'

            @property
            def description(self):
                return  "eBooks faved by @{}".format(self.username)
        return SupporterFacet    
   
class PublisherFacetGroup(FacetGroup):
    
    def __init__(self):
        super(FacetGroup,self).__init__()
        self.title = 'Publisher'
        # don't display facets
        self.facets = []
        self.label = 'Published by ...'

    def has_facet(self, facet_name):
    
        # recognize any facet_name that starts with "pub." as a valid facet name
        return facet_name.startswith('pub.')

    def get_facet_class(self, facet_name):
        class PublisherFacet(NamedFacet):
            def set_name(self):
                self.facet_name=facet_name
                # facet_names of the form 'pub.PUB_ID' and PUB_ID is therefore the 5th character on
                self.pub_id=self.facet_name[4:]
                pubmodel = apps.get_model('core', 'Publisher')
                try:
                    self.publisher =  pubmodel.objects.get(id=self.pub_id)
                except pubmodel.DoesNotExist:
                    self.publisher =  None
                except ValueError: # pub_id is not a number
                    self.publisher =  None
            def pub_filter(query_set):
                return query_set.filter(edition__publisher_name__publisher__id=facet_name[4:])
            def edition_pub_filter(query_set):
                return query_set.filter(publisher_name__publisher__id=facet_name[4:])
            model_filters = {"Ebook": pub_filter, "Edition": edition_pub_filter }
            def get_query_set(self):
                return self._get_query_set().filter(editions__publisher_name__publisher=self.publisher)
            def template(self):
                return 'facets/publisher.html'
            @property    
            def title(self):
                return self.publisher.name.name if self.publisher else ""
            @property    
            def label(self):
                return self.publisher.name.name if self.publisher else ""
            @property
            def description(self):
                return  "eBooks published by %s" % self.title
        return PublisherFacet    

# order of groups in facet_groups determines order of display on /free/    
facet_groups = [KeywordFacetGroup(), FormatFacetGroup(),  LicenseFacetGroup(), PublisherFacetGroup(), IdFacetGroup(), SearchFacetGroup(), SupporterFacetGroup()]

def get_facet(facet_name):
    for facet_group in facet_groups:
        if facet_group.has_facet(facet_name):
            return facet_group.get_facet_class(facet_name)
    return BaseFacet

def get_all_facets(group='all'):
    facets=[]
    for facet_group in facet_groups:
        if group == 'all' or facet_group.title == group:
            facets = facets + facet_group.facets
    return facets

def get_facet_object(facet_path):
    facets = facet_path.replace('//','/').strip('/').split('/')
    facet_object = None
    for facet in facets:
        facet_object = get_facet(facet)(facet_object)
    return facet_object

order_by_keys = {
    'newest':['-featured', '-created'],
    'oldest':['created'],
    'featured':['-featured', '-num_wishes'],
    'popular':['-num_wishes'],
    'title':['title'],
    'none':[], #no ordering 
}   
           
def get_order_by(order_by_key):
    # return the args to use as arguments for order_by
    return order_by_keys.get(order_by_key,'')