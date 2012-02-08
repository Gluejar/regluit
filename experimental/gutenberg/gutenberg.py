"""
Module to parse the Project Gutenberg Catalog and map to various work IDs
"""

import unittest
import os
import json

from copy import deepcopy

from freebase.api.mqlkey import quotekey, unquotekey

import freebase
import requests
from lxml import html
import httplib
from urlparse import urljoin
from urllib import urlencode
from pprint import pprint
from collections import defaultdict

from itertools import islice, chain, izip
import operator
import time

import re
from itertools import islice, izip
import logging
import random

from google.refine import refine

from datetime import datetime

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Sequence, Boolean, not_, and_, DateTime
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql.expression import ClauseElement

from bookdata import WorkMapper, OpenLibrary, FreebaseBooks, GoogleBooks, GOOGLE_BOOKS_KEY, thingisbn

try:
    from regluit.core import isbn as isbn_mod
except:
    import isbn as isbn_mod

logging.basicConfig(filename='gutenberg.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

def filter_none(d):
    d2 = {}
    for (k,v) in d.iteritems():
        if v is not None:
            d2[k] = v
    return d2

# http://stackoverflow.com/questions/2348317/how-to-write-a-pager-for-python-iterators/2350904#2350904        
def grouper(iterable, page_size):
    page= []
    for item in iterable:
        page.append( item )
        if len(page) == page_size:
            yield page
            page= []
    yield page
    
def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

# http://stackoverflow.com/a/2587041/7782
def get_or_create(session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.iteritems() if not isinstance(v, ClauseElement))
        if defaults is None:
            defaults = {}
        params.update(defaults)
        instance = model(**params)
        session.add(instance)
        return instance, True    

Base = declarative_base()

class GutenbergText(object):
    """ 
    CREATE TABLE `GutenbergText` (
      `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
      `etext_id` int(10) unsigned NOT NULL,
      `title` varchar(1024) DEFAULT NULL,
      `friendly_title` varchar(1024) DEFAULT NULL,
      `lang` char(5) DEFAULT NULL,
      `rights` varchar(512) DEFAULT NULL,
      `created` date DEFAULT NULL,
      `creator` varchar(1024) DEFAULT NULL,
      PRIMARY KEY (`id`),
      KEY `etext_id` (`etext_id`)
    ) ENGINE=MyISAM AUTO_INCREMENT=37874 DEFAULT CHARSET=utf8;    
    """
    pass

class GutenbergFile(object):
    """
    CREATE TABLE `GutenbergFile` (
      `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
      `about` varchar(300) NOT NULL DEFAULT '',
      `format` varchar(256) DEFAULT NULL,
      `extent` int(11) unsigned DEFAULT NULL,
      `modified` date DEFAULT NULL,
      `is_format_of` int(11) DEFAULT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `about_index` (`about`),
      KEY `is_format_of` (`is_format_of`)
    ) ENGINE=MyISAM AUTO_INCREMENT=463211 DEFAULT CHARSET=utf8;    
    """
    pass

class WikipediaLink(Base):

    __tablename__ = 'WikipediaLink'
    __table_args__ = (
        UniqueConstraint('gutenberg_etext_id', 'wikipedia_href', name='wikipedia_etext_id'),
        {'mysql_engine':'MyISAM'}
    )  
    
    id = Column(Integer, primary_key=True)
    gutenberg_etext_id = Column('gutenberg_etext_id', Integer(11))
    wikipedia_href = Column('wikipedia_href', String(255))
    wikipedia_title = Column('wikipedia_title', String(255))

class FreebaseEntity(Base):
    __tablename__ = 'FreebaseEntity'
    __table_args__ = (
        {'mysql_engine':'MyISAM'}
    )  

    id = Column('id', String(255), primary_key=True)
    wikipedia_href = Column('wikipedia_href', String(255))
    is_book_book = Column('is_book_book', Boolean)
    
class OpenLibraryWork(Base):
    __tablename__ = 'OpenLibraryWork'
    __table_args__ = (
        {'mysql_engine':'MyISAM'}
    )  

    id = Column('id', String(255), primary_key=True)
    title = Column('title', String(512), default=None)
    

class MappedWork(Base):
    __tablename__ = 'MappedWork'
    __table_args__ = (
        {'mysql_engine':'MyISAM'}
    )
    id = Column(Integer, primary_key=True)
    olid = Column('olid', String(255))
    freebase_id = Column('freebase_id', String(255))
    gutenberg_etext_id = Column(Integer)
    
class GutenbergIdMapped(Base):
    __tablename__ = 'GutenbergIdMapped'
    __table_args__ = (
        {'mysql_engine':'MyISAM'}
    )
    id = Column(Integer, primary_key=True, autoincrement=False)    
   
class MappingError(Base):
    __tablename__ = 'MappingError'
    __table_args__ = (
        {'mysql_engine':'MyISAM'}
    )
    id = Column('id', Integer, primary_key=True)
    created = Column('created', DateTime, default=datetime.utcnow())
    message = Column('message', String(1000))
    

@singleton
class GluejarDB(object):
    def __init__(self, user="gluejar", pw="gluejar", db="Gluejar", host="127.0.0.1", port=3306):
        mysql_connect_path = "mysql+mysqldb://%s:%s@%s:%s/%s?charset=utf8" % (user,pw,host,port,db)
        engine = create_engine(mysql_connect_path, echo=False)
      
        metadata = MetaData(engine)
        Base.metadata.create_all(engine) 
        
        gutenbergtext = Table('GutenbergText', metadata, autoload=True)
        mapper(GutenbergText, gutenbergtext)

        gutenbergfile = Table('GutenbergFile', metadata, autoload=True)
        mapper(GutenbergFile, gutenbergfile)
        
        Session = sessionmaker(bind=engine)
        session = Session()
        self.session = session
    def commit_db(self):
        self.session.commit()
    def rollback(self):
        self.session.rollback()
    def gutenberg_texts(self):
        """generator for all records in the GutenbergText table"""
        items = self.session.query(GutenbergText).all()
        for item in items:
            yield item
    def filtered_wikipedia_links(self):
        """generate wikipedia links that are in the main Wikipedia namespace"""
        # eliminate pages in the TO_FILTER namespace
        TO_FILTER = ['File:%', 'Portal:%', 'Portal talk:%', "Talk:%",
                     'Template:%', 'Template talk:%', 'User:%','User talk:%',
                     'Wikipedia:%', 'Wikipedia talk:%']
        total_filter = and_(*[not_(WikipediaLink.wikipedia_title.like(f)) for f in TO_FILTER])
        items = self.session.query(WikipediaLink).filter(total_filter)
        for item in items:
            yield item
    

def parse_project_gutenberg_catalog(fname='/Users/raymondyee/D/Document/Gluejar/gutenberg/catalog.rdf'):
    #URL = http://www.gutenberg.org/feeds/catalog.rdf.zip
    import re
    
    def text(node):
        node.normalize()
        return node.childNodes[0].data
        
    RDF_NS = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
    DC_NS = 'http://purl.org/dc/elements/1.1/'
    DCTERMS_NS = 'http://purl.org/dc/terms/'
    PGTERMS_NS = 'http://www.gutenberg.org/rdfterms/'
    
    from xml.dom.pulldom import START_ELEMENT, parse
    doc = parse(fname)
    for event, node in doc:
        if event == START_ELEMENT and node.localName == "etext":
            doc.expandNode(node)
            
            # etext_id
            id = node.getAttributeNS(RDF_NS,'ID')
            try:
                etext_id = int(re.match(r'^etext(\d+)$', id).group(1))
            except:
                etext_id = None
            # title
            try:
                title = text(node.getElementsByTagNameNS(DC_NS,'title')[0])
                title = title.replace("\n"," ").replace("\r"," ")
            except:
                title = None
            # friendly_title    
            try:
                friendly_title = text(node.getElementsByTagNameNS(PGTERMS_NS,'friendlytitle')[0])
                friendly_title = friendly_title.replace("\n"," ").replace("\r"," ")
            except:
                friendly_title = None
            
            # lang    
            try:
                lang = text(node.getElementsByTagNameNS(DC_NS,'language')[0].getElementsByTagNameNS(DCTERMS_NS,'ISO639-2')[0].getElementsByTagNameNS(RDF_NS,'value')[0])
            except Exception, e:
                logger.debug(e)
                lang = None
            
            # rights    
            try:
                rights_node = node.getElementsByTagNameNS(DC_NS,'rights')[0]
                rights = rights_node.getAttributeNS(RDF_NS, 'resource')
                if rights == '':
                    rights = text(rights_node)
            except Exception, e:
                logger.debug(e)
                right = None

            # created
            # <dc:created><dcterms:W3CDTF><rdf:value>2011-11-02</rdf:value></dcterms:W3CDTF></dc:created>
            try:
                created_str = text(node.getElementsByTagNameNS(DC_NS,'created')[0].getElementsByTagNameNS(DCTERMS_NS,'W3CDTF')[0].getElementsByTagNameNS(RDF_NS,'value')[0])
                created = datetime.date(datetime.strptime(created_str, "%Y-%m-%d"))
            except Exception, e:
                logger.debug(e)
                created = None
                
            # creator
            try:
                creator = text(node.getElementsByTagNameNS(DC_NS,'creator')[0])
            except Exception, e:
                logger.debug(e)
                creator = None              

                            
            yield {'type':'text', 'etext_id':etext_id, 'title':title, 'friendly_title':friendly_title,
                   'lang':lang, 'rights':rights, 'created':created, 'creator':creator}
            
        if event == START_ELEMENT and node.localName == "file":
            doc.expandNode(node)
            
            # about
            try:
                about = node.getAttributeNS(RDF_NS,'about')
            except Exception, e:
                logger.debug(e)
                about = None
                
            # isFormatOf
            try:
                is_format_of_raw = node.getElementsByTagNameNS(DCTERMS_NS,'isFormatOf')[0].getAttributeNS(RDF_NS,'resource')
                is_format_of = int(re.match(r'#etext(\d+)$',is_format_of_raw).group(1))
            except Exception, e:
                logger.debug(e)
                is_format_of = None
                
            # format: grab the first one
            try:
                format = text(node.getElementsByTagNameNS(DC_NS,'format')[0].getElementsByTagNameNS(DCTERMS_NS,'IMT')[0].getElementsByTagNameNS(RDF_NS,'value')[0])
            except Exception, e:
                logger.debug(e)
                format = None
                
            # modified
            try:
                modified_str = text(node.getElementsByTagNameNS(DCTERMS_NS,'modified')[0].getElementsByTagNameNS(DCTERMS_NS,'W3CDTF')[0].getElementsByTagNameNS(RDF_NS,'value')[0])
                modified = datetime.date(datetime.strptime(modified_str, "%Y-%m-%d"))
            except Exception, e:
                logger.info(e)
                modified = None            
            
            # extent
            try:
                extent = int(text(node.getElementsByTagNameNS(DCTERMS_NS,'extent')[0]))
            except Exception, e:
                raise e
                logger.info(e)
                extent = None   
            
                
            yield {'type':'file', 'about':about, 'is_format_of':is_format_of, 'format':format, 'modified':modified,
                   'extent':extent}
 
def walk_through_catalog(fname='/Users/raymondyee/D/Document/Gluejar/gutenberg/catalog.rdf',max=100000):
    for i, item in enumerate(islice(parse_project_gutenberg_catalog(fname),max)):
        print i, item
        
def load_texts_to_db(fname='/Users/raymondyee/D/Document/Gluejar/gutenberg/catalog_texts.rdf', max=None):
    gluejar_db = GluejarDB()

    for (i, item) in enumerate(islice(parse_project_gutenberg_catalog(fname),max)):
        print i, item
        if item['type'] == 'text':
            try:
                book = gluejar_db.session.query(GutenbergText).filter(GutenbergText.etext_id == item['etext_id']).one()
            except:
                book = GutenbergText()
                book.etext_id = item['etext_id']
                gluejar_db.session.add(book)
            book.title = item['title']
            book.friendly_title = item['friendly_title']
            book.lang = item['lang']
            book.rights = item['rights']
            book.created = item['created']
            book.creator = item['creator']

    gluejar_db.commit_db()
    
def load_files_to_db(fname='/Users/raymondyee/D/Document/Gluejar/gutenberg/catalog_files.rdf', max=100000):
    gluejar_db = GluejarDB()

    for (i, item) in enumerate(islice(parse_project_gutenberg_catalog(fname),max)):
        print i, item
        if item['type'] == 'file':
            # try to write if it's a problem do a query to update -- about is unique
            try:
                file = GutenbergFile()
                file.about = item['about']
                gluejar_db.session.add(file)
                gluejar_db.commit_db() 
            except IntegrityError, e:
                gluejar_db.session.rollback()
                file = gluejar_db.session.query(GutenbergFile).filter(GutenbergFile.about== item['about']).one() 

            file.is_format_of = item['is_format_of']
            file.format = item['format']
            file.modified = item['modified']
            file.extent = item['extent']
            gluejar_db.commit_db()

    gluejar_db.commit_db()    

def external_links_in_wikipedia(target, limit=500, offset=0):
    # e.g., http://en.wikipedia.org/w/index.php?title=Special:LinkSearch&target=http%3A%2F%2Fwww.gutenberg.org%2Fetext%2F&limit=500&offset=0
    base_url = "http://en.wikipedia.org/w/index.php"
    params = filter_none({"title":"Special:LinkSearch", "target":target,
              "limit":limit, offset:offset})
    
    url = "%s?%s" % (base_url, urlencode(params)) 
    
    # page through all the results
    
    more_pages = True
    
    while more_pages:
        
        r = requests.get(url)
        if r.status_code != httplib.OK:
            raise Exception("Problem with request on %s %s: %s %s", base_url, params, r.status_code, r.content)
    
        etree = html.fromstring(r.content)
        
        links = etree.xpath("//ol")[0].xpath("li")
        for link in links:
            (target_a, source_a) = link.xpath('a')
            yield {"target":target_a.attrib["href"], "source_href": source_a.attrib["href"], "source_title":source_a.text}

        # is there another page
        
        following_page = etree.xpath("//a[@class='mw-nextlink']")
        if len(following_page) > 0:
            url = urljoin(url, following_page[0].attrib["href"])
        else:
            more_pages = False        

def load_wikipedia_external_links_into_db(max=None):
    
    targets = ["http://www.gutenberg.org/etext", "http://www.gutenberg.org/ebook"]
    links = chain(*[external_links_in_wikipedia(target) for target in targets])
    
    gluejar_db = GluejarDB()
        
    for (i, link) in enumerate(islice(links,max)):
        link_target = link["target"]
        try:
            etext_id = re.search(r'\/(\d+)$', link_target).group(1)
        except:
            etext_id = None
        print i, link["source_href"], link["source_title"], link_target, etext_id
        
        if etext_id is not None:
            wl = WikipediaLink()
            wl.gutenberg_etext_id = etext_id
            wl.wikipedia_href = link["source_href"]
            wl.wikipedia_title = link["source_title"]
            gluejar_db.session.add(wl)
            try:
                gluejar_db.commit_db()
            except Exception, e:
                print e
                gluejar_db.rollback()

def map_wikipedia_links_to_freebase_ids(max=None ,page_size=5):
    fb = FreebaseClient('rdhyee', 'fbkule!')
    db = GluejarDB()
    
    wikipedia_ids = list( (wl.wikipedia_href for wl in islice(db.filtered_wikipedia_links(), max)) )
    for id in wikipedia_ids:
        print id
   
    resp = fb.wikipedia_href_to_freebase_id(wikipedia_ids,page_size=page_size)
    
    for (i,r) in enumerate(resp):
        print i, r

        if len(r):  # an actual result
            print r[0]['id'], r[0]['type'], r[0]['key'][0]['value']
        
            fb_entity = FreebaseEntity()
            fb_entity.id = r[0]['id']
            
            try:
                db.session.add(fb_entity)
                db.commit_db()
            except IntegrityError, e:
                db.rollback()
                fb_entity = db.session.query(FreebaseEntity).filter(FreebaseEntity.id==r[0]['id']).one() 
                
            fb_entity.wikipedia_href = '/wiki/%s' % (unquotekey(r[0]['key'][0]['value']))
            fb_entity.is_book_book = '/book/book' in r[0]['type']
            db.commit_db()

def map_refine_fb_links_to_openlibrary_work_ids(max=None):
    
    db = GluejarDB()
    refine_proj_id = "1884515736058"
    refine_obj = refine.Refine(refine.RefineServer())
    proj = refine_obj.open_project(refine_proj_id)
    cols_to_extract = ['etext_id', 'title', 'name', 'fb_id', 'fb_id_judgement', 'wikipedia_title']

    limit = max if max is not None else 1000000
    response = proj.get_rows(limit=limit)
    
    # get Gutenberg IDs already done
    done = set([r.id for r in db.session.query(GutenbergIdMapped).all()])
    
    print "response.total: ", response.total
    for i, row in enumerate(islice(response.rows,max)):
        print i, row.index, row['etext_id'], row['title'], row['name'], row['fb_id'], row['fb_id_judgement'],
        if row['etext_id'] is not None and (int(row['etext_id']) not in done):
            try:
                work_ids = list(WorkMapper.freebase_book_to_openlibrary_work(row['fb_id'], complete_search=True))
                print work_ids
                (fb_item, created) = get_or_create(db.session, FreebaseEntity, row['fb_id'])
                for work_id in work_ids:
                    (ol_item, created) = get_or_create(db.session, OpenLibraryWork, id=work_id)
                    (mapping, created) = get_or_create(db.session, MappedWork, olid=work_id, freebase_id=row['fb_id'],
                                            gutenberg_etext_id=int(row['etext_id']))
                done.add(int(row['etext_id']))
                (done_item, created) = get_or_create(db.session, GutenbergIdMapped, id=int(row['etext_id']))
            except Exception, e:
                message = "Problem with i %d, etext_id %s: %s"  % (i, row['etext_id'], e)
                print message
                (error_item, created) = get_or_create(db.session, MappingError, message=message)
        else:
            print "already done"
        
        db.commit_db()

def compute_ol_title_from_work_id(max=None):
    db = GluejarDB()
    # loop through the OpenLibraryWork with null title
    for (i,work) in enumerate(islice(db.session.query(OpenLibraryWork).filter(OpenLibraryWork.title==None),max)):
        print i, work.id, 
        try:
            title = OpenLibrary.json_for_olid(work.id)["title"]
            work.title = title
            print title
        except Exception, e:
            message = "Problem with i %d, work.id %s: %s"  % (i, work.id, e)
            print message
            
    db.commit_db()        

def export_gutenberg_to_ol_mapping(max=None,fname=None):
    SQL = """SELECT mw.gutenberg_etext_id, gt.title as gt_title, mw.olid, olw.title as ol_title, mw.freebase_id, gf.about as 'url', gf.format, gt.rights, gt.lang, DATE_FORMAT(gt.created, "%Y-%m-%d") as 'created'
  FROM MappedWork mw LEFT JOIN GutenbergText gt 
  ON mw.gutenberg_etext_id = gt.etext_id LEFT JOIN OpenLibraryWork olw ON olw.id=mw.olid LEFT JOIN GutenbergFile gf ON gf.is_format_of = gt.etext_id 
  WHERE gf.format = 'application/epub+zip';"""

    headers = ("gutenberg_etext_id", "gt_title", "olid", "ol_title", "freebase_id", "url", "format", "rights", "lang", "created")
    
    # getting the right fields?
    # (title, gutenberg_etext_id, ol_work_id, seed_isbn, url, format, license, lang, publication_date)
    
    db = GluejarDB()
    output = []

    resp = enumerate(islice(db.session.query(*headers).from_statement(SQL).all(),None))
    
    # what choice of serialization at this point?  JSON for now, but not the best for a large file
    for (i,r) in resp:
        print r, type(r), dict(izip(headers,r))
        output.append(dict(izip(headers,r)))
    
    #print json.dumps(output)
    
    if fname is not None:
        f = open(fname, "wb")
        f.write(json.dumps(output))
        f.close()

def import_gutenberg_json(fname):
    headers = ("gutenberg_etext_id", "gt_title", "olid", "ol_title", "freebase_id", "url", "format", "rights", "lang", "created")
    
    f = open(fname)
    records = json.load(f)
    for record in records:
        print [record[h] for h in headers]
    return records

def gutenberg_ol_fb_mappings(gutenberg_ids, max=None):
    """ For each element of the gutenberg_ids, return an good seed ISBN"""
    db = GluejarDB()
    for (i, g_id) in enumerate(islice(gutenberg_ids, max)):
        mappings = db.session.query(MappedWork).filter_by(gutenberg_etext_id = g_id)
        for mapping in mappings.all():
            yield {'fb': mapping.freebase_id, 'olid': mapping.olid}

def seed_isbn(olwk_ids, freebase_id, lang='en'):
    
    random.seed()
    
    logger.info("seed_isbn input: olwk_ids, freebase_id, lang: %s %s %s", olwk_ids, freebase_id, lang)
    lt_clusters = []
    lt_unrecognized = set()
    
    fb = FreebaseBooks()
    gb = GoogleBooks(key=GOOGLE_BOOKS_KEY)
    
    fb_isbn_set = set(fb.xisbn(book_id=freebase_id))
    
    ol_isbn_set = reduce(operator.or_,[set(OpenLibrary.xisbn(work_id=olwk_id)) for olwk_id in olwk_ids])
    
    #lt_isbn_set = set(map(lambda x: isbn_mod.ISBN(x).to_string('13'), thingisbn(SURFACING_ISBN)))
    
    logger.debug("Freebase set: %d %s", len(fb_isbn_set), fb_isbn_set)
    logger.debug("OpenLibrary set: %d %s", len(ol_isbn_set), ol_isbn_set)
    logger.debug("in both fb and ol: %d %s", len(fb_isbn_set & ol_isbn_set), fb_isbn_set & ol_isbn_set)
    logger.debug("in fb but not ol: %d %s", len(fb_isbn_set - ol_isbn_set), fb_isbn_set - ol_isbn_set)
    logger.debug("in ol but not fb: %d %s", len(ol_isbn_set - fb_isbn_set), ol_isbn_set - fb_isbn_set)
    
    # loop through union set and ask thingisbn to cluster
    
    to_cluster = (fb_isbn_set | ol_isbn_set)
    logger.debug("to cluster: %s, %d", to_cluster, len(to_cluster))
    
    while len (to_cluster):
        seed = to_cluster.pop()
        cluster = set(filter(None, map(lambda x: isbn_mod.ISBN(x).to_string('13'), thingisbn(seed))))
        # is there anything in the cluster
        if len(cluster) == 0:
            lt_unrecognized.add(seed)
        else:
            # check that seed is in the cluster
            assert seed in cluster
            lt_clusters.append(cluster)
            to_cluster -= cluster
                
    # print out the clusters
    logger.debug("clusters")
    for (i, lt_cluster) in enumerate(lt_clusters):
        logger.debug("%d %s %d", i, lt_cluster, len(lt_cluster))
    logger.debug("unrecognized by LT %s %d", lt_unrecognized, len(lt_unrecognized))
    
    # figure out new ISBNs found by LT
    new_isbns = (reduce(operator.or_,lt_clusters) | lt_unrecognized) - (fb_isbn_set | ol_isbn_set)
    logger.debug( "new isbns from LT %s %d", new_isbns, len(new_isbns))
        
    gbooks_data = {}
    
    # then pass to Google books to get info, including language
    for (i, isbn) in enumerate((reduce(operator.or_,lt_clusters) | lt_unrecognized)):
        gbooks_data[isbn] = gb.isbn(isbn)
        logger.debug("%d %s %s", i, isbn, gbooks_data[isbn])
    
    # subcluster the lt_clusters by language
    
    lt_clusters_by_lang = []
    
    for lt_cluster in lt_clusters:
        lang_map = defaultdict(list)
        for id in lt_cluster:
            lang_of_id = gbooks_data.get(id).get('language') if gbooks_data.get(id) is not None else None
            lang_map[lang_of_id].append((id))
        lt_clusters_by_lang.append(lang_map)        
    
    # boil the candidate down to a single ISBN:  take a random ISBN from the list of all ISBNs in the requested
    # language subcluster within the largest cluster that has such a language subcluster.
    # Return None if there is no matching sub-language
    # cluster in the largest cluster
    
    candidate_subclusters = filter(lambda x: x[0] is not None,
                                   [(c.get(lang), len(reduce(operator.add,c.values()))) for c in lt_clusters_by_lang]
                            )
    logger.debug("candidate_subclusters: %s", candidate_subclusters)
    if len(candidate_subclusters):
        candidate_seed_isbn = random.sample(
            max(candidate_subclusters, key=lambda x:x[1])[0], 1)[0]
    else:
        candidate_seed_isbn = None
    
    # return a dict with elements that are easy to turn into json
    
    logger.info("seed_isbn output: olwk_ids, freebase_id, lang, candidate_seed: %s %s %s %s", olwk_ids, freebase_id, lang,
                candidate_seed_isbn)
    
    details = {candidate_seed_isbn: candidate_seed_isbn, 'gbooks_data':gbooks_data, 'lt_clusters':map(tuple,lt_clusters),
            'lt_unrecognized':tuple(lt_unrecognized),
            'fb_isbns':tuple(fb_isbn_set), 'ol_isbns':tuple(ol_isbn_set), 'lt_clusters_by_lang':lt_clusters_by_lang}
    return (candidate_seed_isbn, details)

def surfacing_seed_isbn():
    SURFACING_WORK_OLID = 'OL675829W'
    surfacing_fb_id = '/m/05p_vg'
    book_isbn = '9780446311076'
    return seed_isbn(olwk_ids=(SURFACING_WORK_OLID,), freebase_id=surfacing_fb_id)    
    
def moby_dick_seed_isbn():
    return seed_isbn(olwk_ids=('OL102749W',), freebase_id='/en/moby-dick')
    
class FreebaseClient(object):
    def __init__(self, username=None, password=None, main_or_sandbox='main'):
        if main_or_sandbox == 'main':
            self.freebase = freebase
        else:
            self.freebase = freebase.sandbox
        if username is not None and password is not None:
            self.freebase.login(username,password)
    def wikipedia_href_to_freebase_id (self, hrefs, page_size = 10, chop_wiki=True):
        MQL = u"""[{
  "type": [],
  "id": null,
  "key": [{
    "namespace": "/wikipedia/en",
    "type": "/type/key",
    "value": null
  }]
}]
""".replace("\n"," ")
        
        for (page_num, page) in enumerate(grouper(hrefs, page_size)):
            queries = []
            for (href_num, href) in enumerate(page):
                query = json.loads(MQL)
                if chop_wiki:
                    href = href[6:] if href.startswith('/wiki/') else href
                query[0]['key'][0]['value'] = quotekey(href)
                print "%d, %d %s " % (page_num, href_num, href)
                queries.append(query)
            
            if len(queries):
                try:
                    resp = self.freebase.mqlreadmulti(queries)
                    #print "fb resp, len(resp): %s %d" % (resp, len(resp))
                    for r in resp:
                        yield r
                except Exception, e:
                    # for now, write out the stuff in the queries and then move on -- better to try on smaller pieces
                    print "Metaweb Error: %s for page %s" % (e, page)
    
class WikipediaLinksTest(unittest.TestCase):
    def test_external_links(self):
        target = "http://www.gutenberg.org/etext"
        max = 10
        links = []
        for (i, link) in enumerate(islice(external_links_in_wikipedia(target), max)):
            print i, link
            links.append((link["source_href"],link["target"]))
        self.assertEqual(len(links), max)

class DatabaseTest(unittest.TestCase):
    def test_insert_1_wikipedia_link(self):
        gluejar_db = GluejarDB()
        wl = WikipediaLink()
        wl.gutenberg_etext_id = 13920
        wl.wikipedia_href = "/wiki/stuffffdsfsf"
        wl.wikipedia_title = "stuffffdsfsf"
        
        # add one, read it back, and then delete it        
        gluejar_db.session.add(wl)
        gluejar_db.commit_db()
        
        query = gluejar_db.session.query(WikipediaLink).filter(WikipediaLink.wikipedia_href == "/wiki/stuffffdsfsf")
        obj = query.first()
        self.assertEqual(obj.wikipedia_href, "/wiki/stuffffdsfsf")
        
        gluejar_db.session.delete(obj)

        gluejar_db.commit_db()
    def test_integrity_constraint_wikipedia_link(self):
        gluejar_db = GluejarDB()
        
        wl = WikipediaLink()        
        wl.gutenberg_etext_id = 13920
        wl.wikipedia_href = "/wiki/stuffffdsfsf"
        wl.wikipedia_title = "stuffffdsfsf"
        
        wl2 = WikipediaLink()
        wl2.gutenberg_etext_id = 13920
        wl2.wikipedia_href = "/wiki/stuffffdsfsf"
        wl2.wikipedia_title = "stuffffdsfsf2"
        
        # try to add links with the same value twice
        gluejar_db.session.add(wl)
        gluejar_db.session.add(wl2)
        
        self.assertRaises(Exception, gluejar_db.commit_db)      
        gluejar_db.rollback()
        
        # delete the first item
        query = gluejar_db.session.query(WikipediaLink).filter(WikipediaLink.wikipedia_href == "/wiki/stuffffdsfsf")
        obj = query.first()
        self.assertEqual(obj.wikipedia_href, "/wiki/stuffffdsfsf")
        
        gluejar_db.session.delete(obj)
        gluejar_db.commit_db()     
    def test_filtered_wikipedia_links(self):
        db = GluejarDB()
        for item in islice(db.filtered_wikipedia_links(),100):
            print item.wikipedia_title, item.wikipedia_href
        self.assertTrue(True)
    def test_insert_1_fb_ol_link(self):
        db = GluejarDB()
        # in sqlalchemy...is there an equiv to Django get_one_or_new
        # /en/the_hunting_of_the_snark -> OL151447W for etext_id of 12
        (fb_item, created) = get_or_create(db.session, FreebaseEntity, id="/en/the_hunting_of_the_snark")
        (ol_item, created) = get_or_create(db.session, OpenLibraryWork, id="OL151447W")
        (mapping, created) = get_or_create(db.session, MappedWork, olid="OL151447W", freebase_id="/en/the_hunting_of_the_snark", gutenberg_etext_id=12)
        get_or_create(db.session, GutenbergIdMapped, id=12)
        db.commit_db()
    def test_mapping_error(self):
        db = GluejarDB()
        (error_item, created) = get_or_create(db.session, MappingError, message="testing")
        db.commit_db()


class ChainTest(unittest.TestCase):
    def test_chain(self):
        self.assertTrue(True)
        max = None
        sizes = [5, 8, 9]
        numbers = chain(*(xrange(size) for size in sizes))
        
        for (i, num) in enumerate(islice(numbers,max)):
            pass
            
        self.assertEqual(i+1,sum(sizes))

class FreebaseTest(unittest.TestCase):
    def test_query(self):
        fb = FreebaseClient()
        resp = list(fb.wikipedia_href_to_freebase_id(['Peter_and_Wendy', 'King_Lear']))
        for r in resp:
            #print r
            #print r[0]['id'], r[0]['type']
            self.assertTrue('/book/book' in r[0]['type'])
    def test_query_and_db_insert(self):
        fb = FreebaseClient()
        db = GluejarDB()
        resp = list(fb.wikipedia_href_to_freebase_id(['Peter_and_Wendy', 'King_Lear', 'Hamlet']))
        for r in resp:
            print r
            print r[0]['id'], r[0]['type'], r[0]['key'][0]['value']
            self.assertTrue('/book/book' in r[0]['type'])
            fb_entity = FreebaseEntity()
            fb_entity.id = r[0]['id']
            
            try:
                db.session.add(fb_entity)
                db.commit_db()
            except IntegrityError, e:
                db.rollback()
                fb_entity = db.session.query(FreebaseEntity).filter(FreebaseEntity.id==r[0]['id']).one() 
                
            fb_entity.wikipedia_href = '/wiki/%s' % (r[0]['key'][0]['value'])
            fb_entity.is_book_book = '/book/book' in r[0]['type']
            db.commit_db()
            
        # return True if no crashing
        self.assertTrue(True)


class RefineTest(unittest.TestCase):
    def setUp(self):
        self.refine_obj = refine.Refine(refine.RefineServer())
    def test_project_listing(self):
        # https://raw.github.com/PaulMakepeace/refine-client-py/master/refine.py
        projects = self.refine_obj.list_projects().items()
        def date_to_epoch(json_dt):
            "Convert a JSON date time into seconds-since-epoch."
            return time.mktime(time.strptime(json_dt, '%Y-%m-%dT%H:%M:%SZ'))
        projects.sort(key=lambda v: date_to_epoch(v[1]['modified']), reverse=True)
        for project_id, project_info in projects:
            print('{0:>14}: {1}'.format(project_id, project_info['name']))
            id = int(project_id)   # check to see whether there will be a non-int
            
    def test_project_name(self):
        id = "1884515736058"
        print self.refine_obj.get_project_name(id)
    def test_columns(self):
        id = "1884515736058"
        proj = self.refine_obj.open_project(id)
        models = proj.get_models()
        cols = proj.columns
        pprint(models)
        print models.keys()
        print cols
    def test_iterate_rows(self):
        id = "1884515736058"
        proj = self.refine_obj.open_project(id)
        cols_to_extract = ['etext_id', 'title', 'name', 'fb_id', 'fb_id_judgement', 'wikipedia_title']

        response = proj.get_rows(limit=10)
        print "response.total: ", response.total
        for i, row in enumerate(islice(response.rows,10)):
            print i, row.flagged, row.starred, row.index,
            print i, [row[c] for c in cols_to_extract]
        


class FreebaseToOpenLibraryMappingTest(unittest.TestCase):
    def setUp(self):
        pass
    def test_OpenLib_setup(self):
        pass

class ISBNSeedTest(unittest.TestCase):
    def test_isbnseed(self):
        gutenberg_ids = ['2701']
        for (g_id, val) in izip(gutenberg_ids, gutenberg_ol_fb_mappings(gutenberg_ids)):
            print g_id, val
   
def suite():
    
    testcases = []
    suites = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(testcase) for testcase in testcases])
    suites.addTest(ISBNSeedTest('test_isbnseed')) 
    #suites.addTest(SettingsTest('test_dev_me_alignment'))  # give option to test this alignment
    return suites


if __name__ == '__main__':
    
    #walk through and parse catalogs
    #walk_through_catalog(fname='/Users/raymondyee/D/Document/Gluejar/gutenberg/catalog_texts.rdf',max=100)
    #walk_through_catalog(fname='/Users/raymondyee/D/Document/Gluejar/gutenberg/catalog_files.rdf',max=1000)
    
    #load_texts_to_db(max=10)
    #load_files_to_db(max=None)
    #load_wikipedia_external_links_into_db(None)
    #map_wikipedia_links_to_freebase_ids(None, page_size=10)

    # in between:  here we have to do some manual work in Google Refine

    #map_refine_fb_links_to_openlibrary_work_ids(max=None)
    #compute_ol_title_from_work_id(max=1000)
    
    #export_gutenberg_to_ol_mapping(fname="gutenberg_openlibrary.json")
    #import_gutenberg_json(fname="gutenberg_openlibrary.json")

    print surfacing_seed_isbn()
    
    #unittest.main()

    suites = suite()
    #suites = unittest.defaultTestLoader.loadTestsFromModule(__import__('__main__'))
    #unittest.TextTestRunner().run(suites)
    

        
    