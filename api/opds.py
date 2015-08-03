from itertools import islice

from lxml import etree
import datetime
import urlparse
from django.utils.http import urlquote

import pytz

import logging
logger = logging.getLogger(__name__)

from regluit.core import models, facets
import regluit.core.cc as cc

licenses = cc.LICENSE_LIST

FORMAT_TO_MIMETYPE = {'pdf':"application/pdf",
                      'epub':"application/epub+zip",
                      'mobi':"application/x-mobipocket-ebook",
                      'html':"text/html",
                      'text':"text/html"}

UNGLUEIT_URL= 'https://unglue.it'
ACQUISITION = "application/atom+xml;profile=opds-catalog;kind=acquisition"
FACET_RELATION = "http://opds-spec.org/facet"

old_facets= ["creative_commons","active_campaigns"] 


def feeds():
    for facet in old_facets:
        yield globals()[facet]
    for facet_path in facets.get_all_facets('Format'):
        yield get_facet_facet(facet_path)
    for facet_path in facets.get_all_facets('Keyword'):
        yield get_facet_facet(facet_path)

def get_facet_class(name):
    if name in old_facets:
        return globals()[name]
    else:
        return get_facet_facet(name)
        
        
def text_node(tag, text):
    node = etree.Element(tag)
    node.text = text
    return node

def html_node(tag, html):
    node = text_node(tag, html)
    node.attrib.update({"{http://www.w3.org/2005/Atom}type":'html'})
    return node
    
def add_query_component(url, qc):
    """
    add component qc to the querystring of url
    """
    m = list(urlparse.urlparse(url))
    if len(m[4]):
        m[4] = "&".join([m[4],qc])
    else:
        m[4] = qc
    return urlparse.urlunparse(m)

def isbn_node(isbn):
    node = etree.Element("{http://purl.org/dc/terms/}identifier")
    node.attrib.update({"{http://www.w3.org/2001/XMLSchema-instance}type":'dcterms:URI'})
    node.text = 'urn:ISBN:'+ isbn
    return node

def work_node(work, facet=None):
    
    node = etree.Element("entry")
    # title
    node.append(text_node("title", work.title))
    
    # id
    node.append(text_node('id', "{base}{url}".format(base=UNGLUEIT_URL,url=work.get_absolute_url())))
    
    # updated -- using creation date
    node.append(text_node('updated', work.created.isoformat()))
    
    # links for all ebooks
    ebooks=facet.filter_model("Ebook",work.ebooks()) if facet else work.ebooks()
    for ebook in ebooks:
        link_node = etree.Element("link")
        
        # ebook.download_url is an absolute URL with the protocol, domain, and path baked in
        
        link_node.attrib.update({"href":add_query_component(ebook.download_url, "feed=opds"),
                                 "type":FORMAT_TO_MIMETYPE.get(ebook.format, ""),
                                 "rel":"http://opds-spec.org/acquisition"})
        node.append(link_node)
        
    # get the cover -- assume jpg?
    
    cover_node = etree.Element("link")
    cover_node.attrib.update({"href":work.cover_image_small(),
                              "type":"image/"+work.cover_filetype(),
                              "rel":"http://opds-spec.org/image/thumbnail"})
    node.append(cover_node)
    cover_node = etree.Element("link")
    cover_node.attrib.update({"href":work.cover_image_thumbnail(),
                              "type":"image/"+work.cover_filetype(),
                              "rel":"http://opds-spec.org/image"})
    node.append(cover_node)
    
    
    # <dcterms:issued>2012</dcterms:issued>
    node.append(text_node("{http://purl.org/dc/terms/}issued", work.publication_date_year))
    
    # author
    # TO DO: include all authors?
    author_node = etree.Element("author")
    author_node.append(text_node("name", work.author()))
    node.append(author_node)
    
    # publisher
    #<dcterms:publisher>Open Book Publishers</dcterms:publisher>
    if len(work.publishers()):
        for publisher in work.publishers():
            node.append(text_node("{http://purl.org/dc/terms/}issued", publisher.name.name))
            
    # language
    #<dcterms:language>en</dcterms:language>
    node.append(text_node("{http://purl.org/dc/terms/}language", work.language))
    
    # description
    node.append(html_node("{http://www.w3.org/2005/Atom}content", work.description))
    
    # identifiers
    if work.identifiers.filter(type='isbn'):
        for isbn in work.identifiers.filter(type='isbn')[0:9]:  #10 should be more than enough
            node.append(isbn_node(isbn.value))
    
    # subject tags
    # [[subject.name for subject in work.subjects.all()] for work in ccworks if work.subjects.all()]
    for subject in work.subjects.all():
        if subject.is_visible:
            category_node = etree.Element("category")
            try:
                category_node.attrib["term"] =  subject.name 
                node.append(category_node)
                try:
                    subject.works.filter(is_free=True)[1]
                    # only show feed if there's another work in it
                    append_navlink(node, 'related', 'kw.'+ subject.name , 0, 'popular', title=subject.name)
                except:
                    pass
            except ValueError:
                # caused by control chars in subject.name
                logger.warning('Deleting subject: %s' % subject.name)
                subject.delete()
                
                
            
    return node

class Facet:
    title = ''
    works = None
    feed_path = ''
    description = ''
    
    def feed(self, page=None, order_by='newest'):
        self.works = self.works.order_by(*facets.get_order_by(order_by))
        return opds_feed_for_works(self, page=page, order_by=order_by)
        
    def updated(self):
        # return the creation date for most recently added item
        if not self.works:
            return pytz.utc.localize(datetime.datetime.utcnow()).isoformat()
        else:
            return pytz.utc.localize(self.works[0].created).isoformat()

def get_facet_facet(facet_path):
    class Facet_Facet(Facet):
    
        def __init__(self, facet_path=facet_path):
            self.feed_path = facet_path
            self.facet_object = facets.get_facet_object(facet_path)
            self.title = "Unglue.it"
            for facet in self.facet_object.facets():
                self.title = self.title + " " + facet.title
            self.works = self.facet_object.get_query_set().distinct()
            self.description = self.facet_object.description
    return Facet_Facet

class creative_commons(Facet):
    title = "Unglue.it Catalog:  Creative Commons Books"
    feed_path = "creative_commons"
    works = models.Work.objects.filter(editions__ebooks__isnull=False, 
                        editions__ebooks__rights__in=cc.LICENSE_LIST).distinct()
    description= "These Creative Commons licensed ebooks are free to read - the people who created them want you to read and share them."
    
class active_campaigns(Facet):
    """
    return opds feed for works associated with active campaigns
    """
    title = "Unglue.it Catalog:  Books under Active Campaign"
    feed_path = "active_campaigns"
    works = models.Work.objects.filter(campaigns__status='ACTIVE', is_free = True)
    description= "With your help we're raising money to make these books free to the world."

def opds_feed_for_works(the_facet, page=None, order_by='newest'):
    works = the_facet.works
    feed_path = the_facet.feed_path
    title = the_facet.title
    feed_xml = """<feed xmlns:dcterms="http://purl.org/dc/terms/" 
      xmlns:opds="http://opds-spec.org/"
      xmlns="http://www.w3.org/2005/Atom"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:noNamespaceSchemaLocation="http://www.kbcafe.com/rss/atom.xsd.xml"
      xsi:schemaLocation="http://purl.org/dc/elements/1.1/ http://dublincore.org/schemas/xmls/qdc/2008/02/11/dc.xsd http://purl.org/dc/terms/ http://dublincore.org/schemas/xmls/qdc/2008/02/11/dcterms.xsd"/>"""
    
    feed = etree.fromstring(feed_xml)
    
    # add title
    # TO DO: will need to calculate the number items and where in the feed we are
    
    feed.append(text_node('title', title + ' - sorted by ' + order_by))
    
    # id 
    
    feed.append(text_node('id', "{url}/api/opds/{feed_path}/?order_by={order_by}".format(url=UNGLUEIT_URL,
                                                                         feed_path=urlquote(feed_path), order_by=order_by)))
    
    # updated
    # TO DO:  fix time zone?
    # also use our wrapped datetime code
    
    feed.append(text_node('updated',
                          pytz.utc.localize(datetime.datetime.utcnow()).isoformat()))
    
    # author
    
    author_node = etree.Element("author")
    author_node.append(text_node('name', 'unglue.it'))
    author_node.append(text_node('uri', UNGLUEIT_URL))
    feed.append(author_node)
    
    # links:  start, self, next/prev (depending what's necessary -- to start with put all CC books)
    
    # start link
    append_navlink(feed, 'start', feed_path, None , order_by, title="First 10")
    
    # next link
    
    if not page:
        page =0
    else:
        try:
            page=int(page)
        except TypeError:
            page=0
    
    try:
        works[10 * page + 10]
        append_navlink(feed, 'next', feed_path, page+1 , order_by, title="Next 10")
    except IndexError:
        pass
    
    # sort facets
    append_navlink(feed, FACET_RELATION, feed_path, None, 'popular', group="Order", active = order_by=='popular', title="Sorted by popularity")
    append_navlink(feed, FACET_RELATION, feed_path, None, 'newest', group="Order", active = order_by=='newest', title="Sorted by newest")
    
    #other facets
    if feed_path not in old_facets:
        for other_group in the_facet.facet_object.get_other_groups():
            for facet_object in other_group.get_facets():
                append_navlink(feed, FACET_RELATION, feed_path + '/' + facet_object.facet_name, None, order_by, group=other_group.title, title=facet_object.title)
    
    works = islice(works,  10 * page, 10 * page + 10)
    print the_facet.facet_object
    if page > 0:
        append_navlink(feed, 'previous', feed_path, page-1, order_by, title="Previous 10")
    for work in works:
        node = work_node(work, facet=the_facet.facet_object)
        feed.append(node)
    
    return etree.tostring(feed, pretty_print=True)

def append_navlink(feed, rel, path, page, order_by, group=None, active=None , title=""):
    link = etree.Element("link")
    link.attrib.update({"rel":rel,
             "href": UNGLUEIT_URL + "/api/opds/" + urlquote(path) + '/?order_by=' + order_by + ('&page=' + unicode(page) if page!=None else ''),
             "type": ACQUISITION,
             "title": title,
            })
    if rel == FACET_RELATION:
        if group:
            link.attrib['{http://opds-spec.org/}facetGroup'] = group
            if active:
                link.attrib['{http://opds-spec.org/}activeFacet'] = 'true'
    feed.append(link)