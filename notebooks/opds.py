
# coding: utf-8

# 
# 
# Let me see some examples of OPDS in the wild to see how it works:
# 
# available feeds: https://code.google.com/p/openpub/wiki/AvailableFeeds
# 
# let's look at archive.org, which presumably should have a good feed
# 
# * archive.org: http://bookserver.archive.org/catalog/
# * feedbooks.com: http://www.feedbooks.com/catalog.atom
# * oreilly.com: http://opds.oreilly.com/opds/
# 

## Some concepts

# http://www.slideshare.net/fullscreen/HadrienGardeur/understanding-opds/7
# 
# OPDS is based on
# 
# * resources
# * collections 
# 
# A collection aggregates resources.
# 
# Two kinds of resources:
# 
# * Navigation link 
# * Catalog entry 
# 
# for two kinds of collections:
# 
# * Navigation 
# * Acquisition

### Acquisition scenarios

# Multiple acquisition scenarios:
#     
# * Open Access
# * Sale
# * Lending
# * Subscription
# * Extract
# * Undefined

# In[ ]:

import requests
from lxml.etree import fromstring

ATOM_NS = "http://www.w3.org/2005/Atom"

def nsq(url, tag):
    return "{" + url +"}" + tag

url = "http://bookserver.archive.org/catalog/"
    
r = requests.get(url)


# In[ ]:

doc=fromstring(r.text)
doc


# In[ ]:

# get links
# what types specified in spec?

[link.attrib for link in doc.findall(nsq(ATOM_NS,'link'))]


# it might be useful to use specialized libraries to handle Atom or AtomPub.

# In[ ]:

doc.findall(nsq(ATOM_NS, "entry"))


## Atom feed generation

# https://github.com/sramana/pyatom
# 
#     pip install pyatom

# In[ ]:

# let's try the basics of pyatom
# puzzled wwhere <links> come from.

from pyatom import AtomFeed
import datetime

feed = AtomFeed(title="Unglue.it",
                subtitle="Unglue.it OPDS Navigation",
                feed_url="https://unglue.it/opds",
                url="https://unglue.it/",
                author="unglue.it")

# Do this for each feed entry
feed.add(title="My Post",
         content="Body of my post",
         content_type="html",
         author="Me",
         url="http://example.org/entry1",
         updated=datetime.datetime.utcnow())

print feed.to_string()


## Creating navigation feed

# template: https://gist.github.com/rdhyee/94d82f6639809fb7796f#file-unglueit_nav_opds-xml

# 
# ````xml
# <feed xmlns:dcterms="http://purl.org/dc/terms/" xmlns:opds="http://opds-spec.org/"
#   xmlns="http://www.w3.org/2005/Atom"
#   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
#   xsi:noNamespaceSchemaLocation="http://www.kbcafe.com/rss/atom.xsd.xml">
#   <title>Unglue.it Catalog</title>
#   <id>https://unglue.it/opds</id>
#   <updated>2014-06-13T21:48:34Z</updated>
#   <author>
#     <name>unglue.it</name>
#     <uri>https://unglue.it</uri>
#   </author>
#   <!-- crawlable link in archive.org (optional for unglue.it) -->
#   <link rel="http://opds-spec.org/crawlable" type="application/atom+xml;profile=opds-catalog;kind=acquisition" href="https://unglue.it/opds/crawlable" title="Crawlable feed"/>
#   <link rel="start" href="https://unglue.it/opds" type="application/atom+xml;profile=opds-catalog;kind=navigation" />
#   <entry>
#     <title>Creative Commons</title>
#     <id>https://unglue.it/creativecommons/</id>
#     <updated>2014-06-13T00:00:00Z</updated>
#     <link href="creativecommons.xml" type="application/atom+xml;profile=opds-catalog;kind=acquisition" />
#     <content>These Creative Commons licensed ebooks are ready to read - the people who created them want you to read and share them..</content>
#   </entry>
#   <entry>
#     <title>Active Campaigns</title>
#     <id>https://unglue.it/campaigns/ending#2</id>
#     <updated>2014-06-13T00:00:00Z</updated>
#     <link href="active_campaigns.xml" type="application/atom+xml;profile=opds-catalog;kind=acquisition"/>
#     <content>With your help we're raising money to make these books free to the world.</content>
#   </entry>
# </feed>````

# In[ ]:

from lxml import etree
import datetime
import pytz

def text_node(tag, text):
    node = etree.Element(tag)
    node.text = text
    return node

def entry_node(title, id_, updated, link_href, link_type, content):
    node = etree.Element("entry")
    node.append(text_node("title", title))
    node.append(text_node("id", id_))
    node.append(text_node("updated", updated))
    
    link_node = etree.Element("link")
    link_node.attrib.update({'href':link_href, 'type':link_type})
    node.append(link_node)
    
    node.append(text_node("content", content))
    return node

feed_xml = """<feed xmlns:dcterms="http://purl.org/dc/terms/" 
  xmlns:opds="http://opds-spec.org/"
  xmlns="http://www.w3.org/2005/Atom"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:noNamespaceSchemaLocation="http://www.kbcafe.com/rss/atom.xsd.xml"
  xsi:schemaLocation="http://purl.org/dc/elements/1.1/ http://dublincore.org/schemas/xmls/qdc/2008/02/11/dc.xsd http://purl.org/dc/terms/ http://dublincore.org/schemas/xmls/qdc/2008/02/11/dcterms.xsd"/>"""

feed = etree.fromstring(feed_xml)

# add title

feed.append(text_node('title', "Unglue.it Catalog"))

# id 

feed.append(text_node('id', "https://unglue.it/opds"))

# updated

feed.append(text_node('updated',
                      pytz.utc.localize(datetime.datetime.utcnow()).isoformat()))

# author

author_node = etree.Element("author")
author_node.append(text_node('name', 'unglue.it'))
author_node.append(text_node('uri', 'https://unglue.it'))
feed.append(author_node)

# start link

start_link = etree.Element("link")
start_link.attrib.update({"rel":"start",
 "href":"https://unglue.it/opds",
 "type":"application/atom+xml;profile=opds-catalog;kind=navigation",
})
feed.append(start_link)

# crawlable link

crawlable_link = etree.Element("link")
crawlable_link.attrib.update({"rel":"http://opds-spec.org/crawlable", 
 "href":"https://unglue.it/opds/crawlable",
 "type":"application/atom+xml;profile=opds-catalog;kind=acquisition",
  "title":"Crawlable feed"})
feed.append(crawlable_link)

# CC entry_node

cc_entry = entry_node(title="Creative Commons",
                      id_="https://unglue.it/creativecommons/",
                      updated="2014-06-13T00:00:00Z",
                      link_href="creativecommons.xml",
                      link_type="application/atom+xml;profile=opds-catalog;kind=acquisition",
                      content="These Creative Commons licensed ebooks are ready to read - the people who created them want you to read and share them..")
feed.append(cc_entry)

print etree.tostring(feed, pretty_print=True)


## Writing Crawlable Feed

# ````xml
# <feed xmlns:dcterms="http://purl.org/dc/terms/" xmlns:opds="http://opds-spec.org/"
#   xmlns="http://www.w3.org/2005/Atom"
#   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
#   xsi:noNamespaceSchemaLocation="http://www.kbcafe.com/rss/atom.xsd.xml"
#   xsi:schemaLocation="http://purl.org/dc/elements/1.1/ http://dublincore.org/schemas/xmls/qdc/2008/02/11/dc.xsd http://purl.org/dc/terms/ http://dublincore.org/schemas/xmls/qdc/2008/02/11/dcterms.xsd">  
#   <title>Unglue.it Catalog -- 1 to 1 of 2000 -- crawlable feed</title>
#   <id>https://unglue.it/opds/crawlable</id>
#   <updated>2014-06-16T00:00:00Z</updated>
#   <link rel="start" href="https://unglue.it/opds" type="application/atom+xml;profile=opds-catalog;kind=navigation" />
#   <link rel="self" type="application/atom+xml;profile=opds-catalog;kind=acquisition" href="https://unglue.it/opds/crawlable"/>
#   <author>
#     <name>unglue.it</name>
#     <uri>https://unglue.it</uri>
#   </author>
#   <link rel="next" type="application/atom+xml;profile=opds-catalog;kind=acquisition" href="/opds/crawlable/1" title="Next results"/>
#   <entry>
#     <title>Oral Literature In Africa</title>
#     <id>https://unglue.it/work/81834/</id>
#     <updated>2013-07-17T23:27:37Z</updated>
#     <link href="https://unglue.it/download_ebook/904/" type="application/pdf" rel="http://opds-spec.org/acquisition"/>
#     <link href="https://unglue.it/download_ebook/905/" type="application/epub+zip" rel="http://opds-spec.org/acquisition"/>
#     <link href="https://unglue.it/download_ebook/906/" type="application/x-mobipocket-ebook" rel="http://opds-spec.org/acquisition"/>
#     <link href="https://unglueit.files.wordpress.com/2012/05/olacover_thumbnail.jpg" type="image/jpeg" rel="http://opds-spec.org/image/thumbnail"/>
#     <dcterms:issued>2012</dcterms:issued>
#     <author>
#       <name>Ruth Finnegan</name>
#     </author>
#     <category term="Africa"/>
#     <category term="African Folk literature"/>
#     <category term="Folk literature"/>
#     <dcterms:publisher>Open Book Publishers</dcterms:publisher>
#     <dcterms:language>en</dcterms:language>
#     <content type="html"></content>
#   </entry>
# </feed>
# ````

# In[ ]:

# crawlable feed

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

def map_to_unglueit(url):
    m = list(urlparse.urlparse(url))
    (m[0], m[1]) = ('https','unglue.it')
    return urlparse.urlunparse(m)

def work_node(work):
    node = etree.Element("entry")
    # title
    node.append(text_node("title", work.title))
    
    # id
    node.append(text_node('id', "https://unglue.it{0}".format(work.get_absolute_url())))
    
    # updated -- using creation date
    node.append(text_node('updated', work.created.isoformat()))
    
    # links for all ebooks
    
    for ebook in work.ebooks():
        link_node = etree.Element("link")
        link_node.attrib.update({"href":map_to_unglueit(ebook.download_url),
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

feed.append(text_node('id', "https://unglue.it/opds/crawlable"))

# updated
# TO DO:  fix time zone?

feed.append(text_node('updated',
                      pytz.utc.localize(datetime.datetime.utcnow()).isoformat()))

# author

author_node = etree.Element("author")
author_node.append(text_node('name', 'unglue.it'))
author_node.append(text_node('uri', 'https://unglue.it'))
feed.append(author_node)

# links:  start, self, next/prev (depending what's necessary -- to start with put all CC books)

# start link

start_link = etree.Element("link")
start_link.attrib.update({"rel":"start",
 "href":"https://unglue.it/opds",
 "type":"application/atom+xml;profile=opds-catalog;kind=navigation",
})
feed.append(start_link)

# self link

self_link = etree.Element("link")
self_link.attrib.update({"rel":"self",
 "href":"https://unglue.it/opds/crawlable",
 "type":"application/atom+xml;profile=opds-catalog;kind=acquisition",
})
feed.append(self_link)

licenses = cc.LICENSE_LIST

ccworks = models.Work.objects.filter(editions__ebooks__isnull=False, 
                    editions__ebooks__rights__in=licenses).distinct().order_by('-created')

for work in islice(ccworks,None):
    node = work_node(work)
    feed.append(node)

print etree.tostring(feed, pretty_print=True)


# In[ ]:

# how to get CC books?
# make use of CCListView: https://github.com/Gluejar/regluit/blob/b675052736f79dcb8d84ddc6349c99fa392fa9bc/frontend/views.py#L878
# template: https://github.com/Gluejar/regluit/blob/b675052736f79dcb8d84ddc6349c99fa392fa9bc/frontend/templates/cc_list.html

from regluit.core import models
import regluit.core.cc as cc

licenses = cc.LICENSE_LIST

ccworks = models.Work.objects.filter(editions__ebooks__isnull=False, 
                    editions__ebooks__rights__in=licenses).distinct().order_by('-created')
ccworks


# In[ ]:

dir(ccworks[0])


# In[ ]:

work = ccworks[0]
ebook = work.ebooks()[0]
dir(ebook)


# In[ ]:

from collections import Counter

c = Counter()

for work in islice(ccworks,None):
    c.update([ebook.format for ebook in work.ebooks()])
    
print c

#[[ebook.format for ebook in work.ebooks()] for work in islice(ccworks,1)]


## Appendix:  dealing with namespaces in ElementTree

# Maybe come back to http://effbot.org/zone/element-namespaces.htm for more sophisticated ways to register namespaces.
