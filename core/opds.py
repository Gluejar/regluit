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

def text_node(tag, text):
    node = etree.Element(tag)
    node.text = text
    return node

def map_to_unglueit(url, domain="unglue.it", protocol="https"):
    m = list(urlparse.urlparse(url))
    (m[0], m[1]) = (protocol,domain)
    return urlparse.urlunparse(m)

def work_node(work, domain="unglue.it", protocol="https"):
    
    node = etree.Element("entry")
    # title
    node.append(text_node("title", work.title))
    
    # id
    node.append(text_node('id', "{protocol}://{domain}{url}".format(url=work.get_absolute_url(),
                                                                          protocol=protocol,
                                                                          domain=domain)))
    
    # updated -- using creation date
    node.append(text_node('updated', work.created.isoformat()))
    
    # links for all ebooks
    
    for ebook in work.ebooks():
        link_node = etree.Element("link")
        link_node.attrib.update({"href":map_to_unglueit(ebook.download_url, domain, protocol),
                                 "type":FORMAT_TO_MIMETYPE.get(ebook.format, ""),
                                 "rel":"http://opds-spec.org/acquisition"})
        node.append(link_node)
        
    # get the cover -- assume jpg?
    
    cover_node = etree.Element("link")
    cover_node.attrib.update({"href":work.cover_image_small(),
                              "type":"image/jpeg",
                              "rel":"http://opds-spec.org/image/thumbnail"})
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

    # subject tags
    # [[subject.name for subject in work.subjects.all()] for work in ccworks if work.subjects.all()]
    if work.subjects.all():
        for subject in work.subjects.all():
            category_node = etree.Element("category")
            category_node.attrib["term"] = subject.name 
            node.append(category_node)
            
    return node

def creativecommons(domain="unglue.it", protocol="https"):

    feed_xml = """<feed xmlns:dcterms="http://purl.org/dc/terms/" 
      xmlns:opds="http://opds-spec.org/"
      xmlns="http://www.w3.org/2005/Atom"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:noNamespaceSchemaLocation="http://www.kbcafe.com/rss/atom.xsd.xml"
      xsi:schemaLocation="http://purl.org/dc/elements/1.1/ http://dublincore.org/schemas/xmls/qdc/2008/02/11/dc.xsd http://purl.org/dc/terms/ http://dublincore.org/schemas/xmls/qdc/2008/02/11/dcterms.xsd"/>"""
    
    feed = etree.fromstring(feed_xml)
    
    # add title
    # TO DO: will need to calculate the number items and where in the feed we are
    
    feed.append(text_node('title', "Unglue.it Catalog: crawlable feed"))
    
    # id 
    
    feed.append(text_node('id', "{protocol}://{domain}/opds/creativecommons.xml".format(protocol=protocol,
                                                                                             domain=domain)))
    
    # updated
    # TO DO:  fix time zone?
    # also use our wrapped datetime code
    
    feed.append(text_node('updated',
                          pytz.utc.localize(datetime.datetime.utcnow()).isoformat()))
    
    # author
    
    author_node = etree.Element("author")
    author_node.append(text_node('name', 'unglue.it'))
    author_node.append(text_node('uri', '{protocol}://{domain}'.format(protocol=protocol,
                                                                           domain=domain)))
    feed.append(author_node)
    
    # links:  start, self, next/prev (depending what's necessary -- to start with put all CC books)
    
    # start link
    
    start_link = etree.Element("link")
    start_link.attrib.update({"rel":"start",
     "href":"https://unglue.it/opds",
     "type":"application/atom+xml;profile=opds-catalog;kind=navigation",
    })
    feed.append(start_link)
    
    licenses = cc.LICENSE_LIST
    
    ccworks = models.Work.objects.filter(editions__ebooks__isnull=False, 
                        editions__ebooks__rights__in=licenses).distinct().order_by('-created')
    
    for work in islice(ccworks,None):
        node = work_node(work, domain=domain, protocol=protocol)
        feed.append(node)
    
    return etree.tostring(feed, pretty_print=True)