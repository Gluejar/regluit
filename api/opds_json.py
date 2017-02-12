from itertools import islice

import datetime
import urlparse
from django.core.urlresolvers import reverse
from django.utils.http import urlquote
import json
import pytz

import logging
logger = logging.getLogger(__name__)

from regluit.core import models, facets
import regluit.core.cc as cc
from .opds import (
    feeds,
    get_facet_class,
    add_query_component,
    Facet,
    get_facet_facet,
    opds_feed_for_work,
)

licenses = cc.LICENSE_LIST

FORMAT_TO_MIMETYPE = {'pdf':"application/pdf",
                      'epub':"application/epub+zip",
                      'mobi':"application/x-mobipocket-ebook",
                      'html':"text/html",
                      'text':"text/html"}

UNGLUEIT_URL= 'https://unglue.it'
ACQUISITION = "application/vnd.opds.acquisition+json"
FACET_RELATION = "opds:facet"

def feeds():
    for facet_path in facets.get_all_facets('Format'):
        yield get_facet_facet(facet_path)
    for facet_path in facets.get_all_facets('Keyword'):
        yield get_facet_facet(facet_path)

def get_facet_class(name):
    return get_facet_facet(name)
     
def text_node(tag, text):
    return {tag:text}

def html_node(tag, html):
    return {tag:html}
    
def isbn_node(isbn):
    return  'urn:ISBN:'+ isbn

def work_node(work, facet=None):
    
    content={}
    # title
    content["title"] = work.title
    
    # id
    content.update(text_node('id', "{base}{url}".format(base=UNGLUEIT_URL,url=reverse('work_identifier',kwargs={'work_id':work.id}))))
    
    updated = None
    
    # links for all ebooks
    ebooks = facet.filter_model("Ebook",work.ebooks()) if facet else work.ebooks()
    versions = set()
    content['_links'] = links = {}

    for ebook in ebooks:
        if updated is None:
            # most recent ebook, first ebook in loop
            updated = ebook.created.isoformat()
            content.update(text_node('updated', updated))
        if not ebook.version_label in versions:
            versions.add(ebook.version_label)
            link_node_attrib = {}
            ebookfiles = links.get("opds:acquisition:open-access",[])
            ebookfiles.append(link_node_attrib)
            # ebook.download_url is an absolute URL with the protocol, domain, and path baked in
            link_node_attrib.update({"href":add_query_component(ebook.download_url, "feed=opds"),
                                         "rights": str(ebook.rights)})
            if ebook.is_direct(): 
                link_node_attrib["type"] = FORMAT_TO_MIMETYPE.get(ebook.format, "")
            else:
                """ indirect acquisition, i.e. google books """
                link_node_attrib["type"] = "text/html"
                indirect_attrib = {}
                indirect = {"indirectAcquisition":indirect_attrib}
                indirect_attrib["type"] = FORMAT_TO_MIMETYPE.get(ebook.format, "")
                link_node_attrib.update(indirect)
            if ebook.version_label:
                link_node_attrib.update({"version": ebook.version_label})
            links["opds:acquisition:open-access"] = ebookfiles
        
    # get the cover -- assume jpg?
    if work.cover_image_small():
        cover_node_attrib = {}
        cover_node = {"opds:image:thumbnail": cover_node_attrib}
        cover_node_attrib.update({"href":work.cover_image_small(),
                                  "type":"image/"+work.cover_filetype(),
                                  })
        links.update(cover_node)
    if work.cover_image_thumbnail():
        cover_node2_attrib = {}
        cover_node2 = {"opds:image": cover_node2_attrib}
        cover_node2_attrib.update({"href":work.cover_image_thumbnail(),
                                  "type":"image/"+work.cover_filetype(),
                                  })
        links.update(cover_node2)
    
    
    # <dcterms:issued>2012</dcterms:issued>
    content.update({"issued": work.publication_date})
    
    # author
    # TO DO: include all authors?
    content["contributor"] = {"name": work.author()}
    
    # publisher
    #<dcterms:publisher>Open Book Publishers</dcterms:publisher>
    if len(work.publishers()):
        content["publishers"] = [{"publisher": publisher.name.name} 
            for publisher in work.publishers()]
                    
    # language
    content["language"] = work.language
    
    # description
    content["summary"] = work.description
    
    # identifiers
    if work.identifiers.filter(type='isbn'):
        content['identifers'] = [isbn_node(isbn.value) 
            for isbn in work.identifiers.filter(type='isbn')[0:9]]  #10 should be more than enough

    
    # subject tags
    subjects = [subject.name for subject in work.subjects.all()] 
    if subjects:
        content["category"] = subjects

    # age level
    # <category term="15-18" scheme="http://schema.org/typicalAgeRange" label="Teen - Grade 10-12, Age 15-18"/>
    if work.age_level:
        age_level_node_attrib = {}
        age_level_node = {"category": age_level_node_attrib}
        age_level_node_attrib["scheme"] =  'http://schema.org/typicalAgeRange' 
        age_level_node_attrib["term"] =  work.age_level 
        age_level_node_attrib["label"] =  work.get_age_level_display()
        content.update(age_level_node)
    
                
    # rating            
    content["Rating"] = {"ratingValue":"{:}".format(work.priority())}
    return content

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

def opds_feed_for_work(work_id):
    class single_work_facet:
        def __init__(self, work_id):
            try:
                works=models.Work.objects.filter(id=work_id)
            except models.Work.DoesNotExist:
                works=models.Work.objects.none()
            except ValueError:
                # not a valid work_id
                works=models.Work.objects.none()
            self.works=works
            self.title='Unglue.it work #%s' % work_id
            self.feed_path=''
            self.facet_object= facets.BaseFacet(None)
    return opds_feed_for_works( single_work_facet(work_id) )

def opds_feed_for_works(the_facet, page=None, order_by='newest'):
    books_per_page = 50
    works = the_facet.works
    feed_path = the_facet.feed_path
    title = the_facet.title
     
    feed = {'_type': ACQUISITION}
    
    # add title
    # TO DO: will need to calculate the number items and where in the feed we are
    
    feed.update(text_node('title', title + ' - sorted by ' + order_by))
    
    # id 
    
    feed.update(text_node('id', "{url}/api/opdsjson/{feed_path}/?order_by={order_by}".format(url=UNGLUEIT_URL,
                                                                         feed_path=urlquote(feed_path), order_by=order_by)))
    
    # updated
    # TO DO:  fix time zone?
    # also use our wrapped datetime code
    
    feed.update(text_node('updated',
                          pytz.utc.localize(datetime.datetime.utcnow()).isoformat()))
    
    # author
    
    author_node = {"author":{'name': 'unglue.it','uri': UNGLUEIT_URL}}
    feed.update(author_node)
    
    # links:  start, self, next/prev (depending what's necessary -- to start with put all CC books)
    feed['_links'] = {}
    # start link
    append_navlink(feed, 'start', feed_path, None , order_by, title="First {}".format(books_per_page))
    
    # next link
    
    if not page:
        page =0
    else:
        try:
            page=int(page)
        except TypeError:
            page=0
    
    try:
        works[books_per_page * page + books_per_page]
        append_navlink(feed, 'next', feed_path, page+1 , order_by, title="Next {}".format(books_per_page))
    except IndexError:
        pass
    
    # sort facets
    append_navlink(feed, FACET_RELATION, feed_path, None, 'popular', group="Order", active = order_by=='popular', title="Sorted by popularity")
    append_navlink(feed, FACET_RELATION, feed_path, None, 'newest', group="Order", active = order_by=='newest', title="Sorted by newest")
    
    #other facets
    for other_group in the_facet.facet_object.get_other_groups():
        for facet_object in other_group.get_facets():
            append_navlink(feed, FACET_RELATION, feed_path + '/' + facet_object.facet_name, None, order_by, group=other_group.title, title=facet_object.title)
    
    works = islice(works,  books_per_page * page, books_per_page * page + books_per_page)
    if page > 0:
        append_navlink(feed, 'previous', feed_path, page-1, order_by, title="Previous {}".format(books_per_page))
    feedlist = []
    feed['publications'] = feedlist
    for work in works:
        node = work_node(work, facet=the_facet.facet_object)
        feedlist.append(node)
    return json.dumps(feed,indent=2, separators=(',', ': '), sort_keys=False)

def append_navlink(feed, rel, path, page, order_by, group=None, active=None , title=""):
    if page==None:
        return
    link = {
             "href": UNGLUEIT_URL + "/api/opdsjson/" + urlquote(path) + '/?order_by=' + order_by + ('&page=' + unicode(page) ),
             "type": ACQUISITION,
             "title": title,
            }
    if rel == FACET_RELATION:
        if group:
            link['facetGroup'] = group
            if active:
                link['activeFacet'] = 'true'
    feed['_links'][rel] = link