from itertools import islice

from lxml import etree
import datetime
import urlparse

import pytz

from regluit.core import models
import regluit.core.cc as cc

licenses = cc.LICENSE_LIST

FORMAT_TO_MIMETYPE = {'pdf':"application/pdf",
                      'epub':"application/epub+zip",
                      'mobi':"application/x-mobipocket-ebook",
                      'html':"text/html",
                      'text':"text/html"}
facets = ["creative_commons","active_campaigns"]

UNGLUEIT_URL= 'https://unglue.it'
NAVIGATION = "application/atom+xml;profile=opds-catalog;kind=navigation"
def feeds():
    for facet in facets:
        yield globals()[facet]()

def text_node(tag, text):
    node = etree.Element(tag)
    node.text = text
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

def work_node(work):
    
    node = etree.Element("entry")
    # title
    node.append(text_node("title", work.title))
    
    # id
    node.append(text_node('id', "{base}{url}".format(base=UNGLUEIT_URL,url=work.get_absolute_url())))
    
    # updated -- using creation date
    node.append(text_node('updated', work.created.isoformat()))
    
    # links for all ebooks
    
    for ebook in work.ebooks():
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
    
    # identifiers
    if work.identifiers.filter(type='isbn'):
        for isbn in work.identifiers.filter(type='isbn')[0:9]:  #10 should be more than enough
            node.append(isbn_node(isbn.value))
    
    # subject tags
    # [[subject.name for subject in work.subjects.all()] for work in ccworks if work.subjects.all()]
    if work.subjects.all():
        for subject in work.subjects.all():
            category_node = etree.Element("category")
            category_node.attrib["term"] = subject.name 
            node.append(category_node)
            
    return node

class Facet:
    title = ''
    works = None
    feed_path = ''
        
    def feed(self, page=None):
        return opds_feed_for_works(self.works, self.feed_path, title=self.title, page=page)
        
    def updated(self):
        # return the creation date for most recently added item
        if not self.works:
            return pytz.utc.localize(datetime.datetime.utcnow()).isoformat()
        else:
            return pytz.utc.localize(self.works[0].created).isoformat()
        

class creative_commons(Facet):
    title = "Unglue.it Catalog:  Creative Commons Books"
    feed_path = "creative_commons"
    works = models.Work.objects.filter(editions__ebooks__isnull=False, 
                        editions__ebooks__rights__in=cc.LICENSE_LIST).distinct().order_by('-created')

class active_campaigns(Facet):
    """
    return opds feed for works associated with active campaigns
    """
    title = "Unglue.it Catalog:  Books under Active Campaign"
    feed_path = "active_campaigns"
    works = models.Work.objects.filter(campaigns__status='ACTIVE',
                               editions__ebooks__isnull=False).distinct().order_by('-created')

def opds_feed_for_works(works, feed_path, title="Unglue.it Catalog", page=None):

    feed_xml = """<feed xmlns:dcterms="http://purl.org/dc/terms/" 
      xmlns:opds="http://opds-spec.org/"
      xmlns="http://www.w3.org/2005/Atom"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:noNamespaceSchemaLocation="http://www.kbcafe.com/rss/atom.xsd.xml"
      xsi:schemaLocation="http://purl.org/dc/elements/1.1/ http://dublincore.org/schemas/xmls/qdc/2008/02/11/dc.xsd http://purl.org/dc/terms/ http://dublincore.org/schemas/xmls/qdc/2008/02/11/dcterms.xsd"/>"""
    
    feed = etree.fromstring(feed_xml)
    
    # add title
    # TO DO: will need to calculate the number items and where in the feed we are
    
    feed.append(text_node('title', title))
    
    # id 
    
    feed.append(text_node('id', "{url}/api/opds/{feed_path}".format(url=UNGLUEIT_URL,
                                                                         feed_path=feed_path)))
    
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
    append_navlink(feed, 'start', feed_path, None )
    
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
        append_navlink(feed, 'next', feed_path, page+1 )
    except IndexError:
        pass
                
    works = islice(works,  10 * page, 10 * page + 10)
    if page > 0:
        append_navlink(feed, 'previous', feed_path, page-1)
    for work in works:
        node = work_node(work)
        feed.append(node)
    
    return etree.tostring(feed, pretty_print=True)

def append_navlink(feed, rel, path, page):
    link = etree.Element("link")
    link.attrib.update({"rel":rel,
             "href": UNGLUEIT_URL + "/api/opds/" + path + ('/?page=' + unicode(page) if page!=None else '/'),
             "type": NAVIGATION,
            })
    feed.append(link)