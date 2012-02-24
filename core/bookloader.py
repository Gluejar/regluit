import json
import logging
import datetime

import requests
from xml.etree import ElementTree
from itertools import izip, islice

from django.db.models import Q
from django.conf import settings
from django.db import IntegrityError
from django.contrib.comments.models import Comment

import regluit
from regluit.core import models
import regluit.core.isbn


logger = logging.getLogger(__name__)


def add_by_oclc(isbn, work=None):
    # this is indirection in case we have a data source other than google
    return add_by_oclc_from_google(isbn)


def add_by_oclc_from_google(oclc):
    if oclc:
        logger.info("adding book by oclc %s" , oclc)
    else:
        return None
    try:
        return models.Identifier.objects.get(type='oclc', value=oclc).edition
    except:
        url = "https://www.googleapis.com/books/v1/volumes"
        try:
            results = _get_json(url, {"q": '"OCLC%s"' % oclc})
        except LookupFailure, e:
            logger.exception("lookup failure for %s", oclc)
            return None
        if not results.has_key('items') or len(results['items']) == 0:
            logger.warn("no google hits for %s" , oclc)
            return None
    
        try:
            e = add_by_googlebooks_id(results['items'][0]['id'], results=results['items'][0])
            models.Identifier(type='oclc', value=oclc, edition=e, work=e.work).save()
            return e
        except LookupFailure, e:
            logger.exception("failed to add edition for %s", oclc)
        except IntegrityError, e:
            logger.exception("google books data for %s didn't fit our db", oclc)
        return None

def add_by_isbn(isbn, work=None):
    if not isbn:
        return None
    try:
        e = add_by_isbn_from_google(isbn, work=work)
    except LookupFailure:
        logger.exception("failed google lookup for %s", isbn)
        # try again some other time
        return None
    if e:
        return e
    
    logger.info("null came back from add_by_isbn_from_google: %s", isbn)

    if not work or not work.title:
        return None

    # if there's a work with a title, we want to create stub editions and 
    # works, even if google doesn't know about it # but if it's not valid, 
    # forget it!

    try:
        isbn = regluit.core.isbn.ISBN(isbn)
    except:
        logger.exception("invalid isbn: %s", isbn)
        return None
    if not isbn.valid:
        return None
    isbn = isbn.to_string()
    
    # we don't know the language  ->'xx'
    w = models.Work(title=work.title, language='xx')
    w.save()
    e = models.Edition(title=work.title,work=w)
    e.save()
    e.new = True
    models.Identifier(type='isbn', value=isbn, work=w, edition=e).save()
    return e

def get_google_isbn_results(isbn):
    url = "https://www.googleapis.com/books/v1/volumes"
    try:
        results = _get_json(url, {"q": "isbn:%s" % isbn})
    except LookupFailure:
        logger.exception("lookup failure for %s", isbn)
        return None
    if not results.has_key('items') or len(results['items']) == 0:
        logger.warn("no google hits for %s" , isbn)
        return None
    else:
        return results
        
def add_ebooks(item, edition):
    access_info = item.get('accessInfo')
    if access_info:
        edition.public_domain = access_info.get('publicDomain', None)
        epub = access_info.get('epub')
        if epub and epub.get('downloadLink'):
            ebook = models.Ebook(edition=edition, format='epub',
                                 url=epub.get('downloadLink'),
                                 provider='google')
            try:
                ebook.save()
            except IntegrityError:
                pass
                
            
        pdf = access_info.get('pdf')
        if pdf and pdf.get('downloadLink'):
            ebook = models.Ebook(edition=edition, format='pdf',
                                 url=pdf.get('downloadLink', None),
                                 provider='google')
            try:
                ebook.save()
            except IntegrityError:
                pass


def update_edition(edition):
    """
    attempt to update data associated with input edition and return that updated edition
    """

    # if there is no ISBN associated with edition, just return the input edition
    try:
        isbn=edition.identifiers.filter(type='isbn')[0].value
    except models.Identifier.DoesNotExist:
        return edition

    # do a Google Books lookup on the isbn associated with the edition (there should be either 0 or 1 isbns associated
    # with an edition because of integrity constraint in Identifier)
    
    # if we get some data about this isbn back from Google, update the edition data accordingly
    results=get_google_isbn_results(isbn)
    if not results:
        return edition
    item=results['items'][0]
    googlebooks_id=item['id']
    d = item['volumeInfo']
    if d.has_key('title'):
        title = d['title']
    else:
        title=''
    if len(title)==0:
        # need a title to make an edition record; some crap records in GB. use title from parent if available
        title=edition.work.title

    # check for language change
    language = d['language']
    # don't track variants in main language (e.g., traditional vs simplified Chinese)
    if len(language)>2:
        language= language[0:2]
    
    # if the language of the edition no longer matches that of the parent work, attach edition to the    
    if edition.work.language != language:
        logger.info("reconnecting %s since it is %s instead of %s" %(googlebooks_id, language, edition.work.language))
        old_work=edition.work
        
        new_work = models.Work(title=title, language=language)
        new_work.save()
        edition.work = new_work
        edition.save()
        for identifier in edition.identifiers.all():
            logger.info("moving identifier %s" % identifier.value)
            identifier.work=new_work
            identifier.save()
        if old_work.editions.count()==0:
            #a dangling work; make sure nothing else is attached!
            merge_works(new_work,old_work)    
    
    # update the edition
    edition.title = title
    edition.description = d.get('description')
    edition.publisher = d.get('publisher')
    edition.publication_date = d.get('publishedDate', '')
    edition.save()
    
    # create identifier if needed
    models.Identifier.get_or_add(type='goog',value=googlebooks_id,edition=edition,work=edition.work)

    for a in d.get('authors', []):
        a, created = models.Author.objects.get_or_create(name=a)
        a.editions.add(edition)
    
    add_ebooks(item, edition)
            
    return edition

    
def add_by_isbn_from_google(isbn, work=None):
    """add a book to the UnglueIt database from google based on ISBN. The work parameter
    is optional, and if not supplied the edition will be associated with
    a stub work.
    """
    if not isbn:
        return None
    if len(isbn)==10:
        isbn = regluit.core.isbn.convert_10_to_13(isbn)
    
    logger.info("adding book by isbn %s", isbn)

    # check if we already have this isbn
    edition = get_edition_by_id(type='isbn',value=isbn)
    if edition:
        edition.new = False
        return edition

    results=get_google_isbn_results(isbn)
    if results:
        try:
            return add_by_googlebooks_id(results['items'][0]['id'], work=work, results=results['items'][0], isbn=isbn)
        except LookupFailure, e:
            logger.exception("failed to add edition for %s", isbn)
        except IntegrityError, e:
            logger.exception("google books data for %s didn't fit our db", isbn)
        return None
    else:
        return None
        
def get_work_by_id(type,value):
    if value:
        try:
            return models.Identifier.objects.get(type=type,value=value).work
        except models.Identifier.DoesNotExist:
            return None

def get_edition_by_id(type,value):
    if value:
        try:
            return models.Identifier.objects.get(type=type,value=value).edition
        except models.Identifier.DoesNotExist:
            return None


def add_by_googlebooks_id(googlebooks_id, work=None, results=None, isbn=None):
    """add a book to the UnglueIt database based on the GoogleBooks ID. The
    work parameter is optional, and if not supplied the edition will be 
    associated with a stub work. isbn can be passed because sometimes passed data won't include it 
    
    """
    # don't ping google again if we already know about the edition
    try:
        edition = models.Identifier.objects.get(type='goog', value=googlebooks_id).edition
        edition.new = False
        return edition
    except models.Identifier.DoesNotExist:
        pass
    
    # if google has been queried by caller, don't call again
    if results:
        item =results
    else:
        logger.info("loading metadata from google for %s", googlebooks_id)
        url = "https://www.googleapis.com/books/v1/volumes/%s" % googlebooks_id
        item  = _get_json(url)
    d = item['volumeInfo']
    
    if d.has_key('title'):
        title = d['title']
    else:
        title=''
    if len(title)==0:
        # need a title to make an edition record; some crap records in GB. use title from parent if available
        if work:
            title=work.title
        else:
            return None

    # don't add the edition to a work with a different language
    # https://www.pivotaltracker.com/story/show/17234433
    language = d['language']
    if len(language)>2:
        language= language[0:2]
    if work and work.language != language:
        logger.info("not connecting %s since it is %s instead of %s" %
                (googlebooks_id, language, work.language))
        work = None
    # isbn = None
    if not isbn: 
        for i in d.get('industryIdentifiers', []):
            if i['type'] == 'ISBN_10' and not isbn:
                isbn = regluit.core.isbn.convert_10_to_13(i['identifier'])
            elif i['type'] == 'ISBN_13':
                isbn = i['identifier']

    # now check to see if there's an existing Work
    if work:
        work.new = False
    if isbn and not work:
        work = get_work_by_id(type='isbn',value=isbn)
        if work:
            work.new = False
    if not work:
        work = models.Work.objects.create(title=title, language=language)
        work.new = True
        work.save()


    # going off to google can take some time, so we want to make sure this edition has not
    # been created in another thread while we were waiting
    try:
        e = models.Identifier.objects.get(type='goog', value=googlebooks_id).edition
        e.new = False
        # whoa nellie, somebody else created an edition while we were working.
        if work.new:
            work.delete()
        return e
    except models.Identifier.DoesNotExist:
        pass
    
    
    # because this is a new google id, we have to create a new edition
    e = models.Edition(work=work)
    e.title = title
    e.description = d.get('description')
    e.publisher = d.get('publisher')
    e.publication_date = d.get('publishedDate', '')
    e.save()
    e.new = True
    
    # create identifier where needed
    models.Identifier(type='goog',value=googlebooks_id,edition=e,work=work).save()
    if isbn:
        models.Identifier.get_or_add(type='isbn',value=isbn,edition=e,work=work)

    for a in d.get('authors', []):
        a, created = models.Author.objects.get_or_create(name=a)
        a.editions.add(e)

    add_ebooks(item, e)
            
    return e


def add_related(isbn):
    """add all books related to a particular ISBN to the UnglueIt database.
    The initial seed ISBN will be added if it's not already there.
    """
    # make sure the seed edition is there
    logger.info("adding related editions for %s", isbn)
    
    new_editions = []

    edition = add_by_isbn(isbn)
    if edition is None:
        return new_editions

    # this is the work everything will hang off
    work = edition.work
    other_editions = {}
    for other_isbn in thingisbn(isbn):
        # 979's come back as 13
        logger.debug("other_isbn: %s", other_isbn)
        if len(other_isbn)==10:
            other_isbn = regluit.core.isbn.convert_10_to_13(other_isbn)
        related_edition = add_by_isbn(other_isbn, work=work)

        if related_edition:
            related_language = related_edition.work.language
            if edition.work.language == related_language:
                new_editions.append(related_edition)
                if related_edition.work != edition.work:
                    logger.debug("merge_works path 1 %s %s", edition.work.id, related_edition.work.id )
                    merge_works(edition.work, related_edition.work)
            else:
                if other_editions.has_key(related_language):
                    other_editions[related_language].append(related_edition)
                else:
                    other_editions[related_language]=[related_edition]

    # group the other language editions together
    for lang_group in other_editions.itervalues():
        logger.debug("lang_group (ed, work): %s", [(ed.id, ed.work.id) for ed in lang_group])
        if len(lang_group)>1:
            lang_edition = lang_group[0]
            logger.debug("lang_edition.id: %s", lang_edition.id)
            # compute the distinct set of works to merge into lang_edition.work
            works_to_merge = set([ed.work for ed in lang_group[1:]]) - set([lang_edition.work])
            for w in works_to_merge:
                logger.debug("merge_works path 2 %s %s", lang_edition.work.id, w.id )
                merge_works(lang_edition.work, w)
        
    return new_editions
    

def thingisbn(isbn):
    """given an ISBN return a list of related edition ISBNs, according to 
    Library Thing. (takes isbn_10 or isbn_13, returns isbn_10, except for 979 isbns, which come back as isbn_13')
    """
    logger.info("looking up %s at ThingISBN" , isbn)
    url = "http://www.librarything.com/api/thingISBN/%s" % isbn
    xml = requests.get(url, headers={"User-Agent": settings.USER_AGENT}).content
    doc = ElementTree.fromstring(xml)
    return [e.text for e in doc.findall('isbn')]


def merge_works(w1, w2):
    """will merge the second work (w2) into the first (w1)
    """
    logger.info("merging work %s into %s", w2, w1)
    # don't merge if the works are the same or at least one of the works has no id (for example, when w2 has already been deleted)
    if w1 == w2 or w1.id is None or w2.id is None:
        return
    
    for identifier in w2.identifiers.all():
        identifier.work = w1
        identifier.save()
    for comment in Comment.objects.for_model(w2):
        comment.object_pk = w1.pk
        comment.save()
    for edition in w2.editions.all():
        edition.work = w1
        edition.save()
    for campaign in w2.campaigns.all():
        campaign.work = w1
        campaign.save()
    for wishlist in models.Wishlist.objects.filter(works__in=[w2]):
        w2source = wishlist.work_source(w2)
        wishlist.remove_work(w2)
        wishlist.add_work(w1, w2source)

    models.WasWork(was=w2.pk,work=w1).save()
    for ww in models.WasWork.objects.filter(work = w2):
        ww.work = w1
        ww.save()
        
    w2.delete()


def add_openlibrary(work):
    if work.openlibrary_lookup is not None:
        # don't hit OL if we've visited in the past month or so
        if datetime.datetime.now()- work.openlibrary_lookup < datetime.timedelta(days=30):
             return
    work.openlibrary_lookup = datetime.datetime.now()
    work.save()

    # find the first ISBN match in OpenLibrary
    logger.info("looking up openlibrary data for work %s", work.id)
    found = False
    e = None # openlibrary edition json
    w = None # openlibrary work json

    # get the 1st openlibrary match by isbn that has an associated work
    url = "http://openlibrary.org/api/books"
    params = {"format": "json", "jscmd": "details"}
    for edition in work.editions.all():
        isbn_key = "ISBN:%s" % edition.isbn_13
        params['bibkeys'] = isbn_key
        try:
            e = _get_json(url, params, type='ol')
        except LookupFailure:
            logger.exception("OL lookup failed for  %s", isbn_key)
            e = {}
        if e.has_key(isbn_key) and e[isbn_key]['details'].has_key('works'):
            work_key = e[isbn_key]['details']['works'].pop(0)['key']
            logger.info("got openlibrary work %s for isbn %s", work_key, isbn_key)
            try:
                w = _get_json("http://openlibrary.org" + work_key,type='ol')
                if w.has_key('subjects'):
                    found = True
                    break
            except LookupFailure:
                logger.exception("OL lookup failed for  %s", work_key)
    if not found:
        logger.warn("unable to find work %s at openlibrary", work.id)
        return 

    # add the subjects to the Work
    for s in w.get('subjects',  []):
        logger.info("adding subject %s to work %s", s, work.id)
        subject, created = models.Subject.objects.get_or_create(name=s)
        work.subjects.add(subject)
    work.save()

    models.Identifier.get_or_add(type='olwk',value=w['key'],work=work)
    if e[isbn_key]['details'].has_key('identifiers'):
        ids = e[isbn_key]['details']['identifiers']
        if ids.has_key('goodreads'):
            models.Identifier.get_or_add(type='gdrd',value=ids['goodreads'][0],work=work,edition=edition)
        if ids.has_key('librarything'):
            models.Identifier.get_or_add(type='ltwk',value=ids['librarything'][0],work=work)
    # TODO: add authors here once they are moved from Edition to Work


def _get_json(url, params={}, type='gb'):
    # TODO: should X-Forwarded-For change based on the request from client?
    headers = {'User-Agent': settings.USER_AGENT, 
               'Accept': 'application/json',
               'X-Forwarded-For': '69.174.114.214'}
    if type == 'gb':
        params['key'] = settings.GOOGLE_BOOKS_API_KEY
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return json.loads(response.content)
    else:
        logger.error("unexpected HTTP response: %s" % response)
        if response.content:
            logger.error("response content: %s" % response.content)
        raise LookupFailure("GET failed: url=%s and params=%s" % (url, params))


def load_gutenberg_edition(title, gutenberg_etext_id, ol_work_id, seed_isbn, url, format, license, lang, publication_date):
    
    # let's start with instantiating the relevant Work and Edition if they don't already exist
    
    try:
        work = models.Identifier.objects.get(type='olwk',value=ol_work_id).work
    except models.Identifier.DoesNotExist: # try to find an Edition with the seed_isbn and use that work to hang off of
        sister_edition = add_by_isbn(seed_isbn)
        if sister_edition.new:
            # add related editions asynchronously
            regluit.core.tasks.populate_edition.delay(sister_edition.isbn_13)
        work = sister_edition.work
        # attach the olwk identifier to this work if it's not none.
        if ol_work_id is not None:
            work_id = models.Identifier.get_or_add(type='olwk',value=ol_work_id, work=work)

    # Now pull out any existing Gutenberg editions tied to the work with the proper Gutenberg ID
    try:
        edition = models.Identifier.objects.get( type='gtbg', value=gutenberg_etext_id ).edition    
    except models.Identifier.DoesNotExist:
        edition = models.Edition()
        edition.title = title
        edition.work = work
        
        edition.save()
        edition_id = models.Identifier.get_or_add(type='gtbg',value=gutenberg_etext_id, edition=edition, work=work)
        
    # check to see whether the Edition hasn't already been loaded first
    # search by url
    ebooks = models.Ebook.objects.filter(url=url)
    
    # format: what's the controlled vocab?  -- from Google -- alternative would be mimetype
    
    if len(ebooks):  
        ebook = ebooks[0]
    elif len(ebooks) == 0: # need to create new ebook
        ebook = models.Ebook()

    if len(ebooks) > 1:
        warnings.warn("There is more than one Ebook matching url {0}".format(url))
        
        
    ebook.format = format
    ebook.provider = 'gutenberg'
    ebook.url =  url
    ebook.rights = license
        
    # is an Ebook instantiable without a corresponding Edition? (No, I think)
    
    ebook.edition = edition
    ebook.save()
    
    return ebook

def add_missing_isbn_to_editions(max_num=None, confirm=False):
    """For each of the editions with Google Books ids, do a lookup and attach ISBNs.  Set confirm to True to check db changes made correctly"""
    logger.info("Number of editions with Google Books IDs but not ISBNs (before): %d", 
        models.Edition.objects.filter(identifiers__type='goog').exclude(identifiers__type='isbn').count())
    
    from regluit.experimental import bookdata
    
    gb = bookdata.GoogleBooks(key=settings.GOOGLE_BOOKS_API_KEY)
    
    new_isbns = []
    google_id_not_found = []
    no_isbn_found = []
    editions_to_merge = []
    exceptions = []
    
    
    for (i, ed) in enumerate(islice(models.Edition.objects.filter(identifiers__type='goog').exclude(identifiers__type='isbn'), max_num)):
        try:
            g_id = ed.identifiers.get(type='goog').value
        except Exception, e:
            # we might get an exception if there is, for example, more than one Google id attached to this Edition
            logger.exception("add_missing_isbn_to_editions for edition.id %s: %s", ed.id, e)
            exceptions.append((ed.id, e))
            continue
        
        # try to get ISBN from Google Books
        try:
            vol_id = gb.volumeid(g_id)
            if vol_id is None:
                google_id_not_found.append((ed.id, g_id))
                logger.debug("g_id not found: %s", g_id)
            else:
                isbn = vol_id.get('isbn')
                logger.info("g_id, isbn: %s %s", g_id, isbn)
                if isbn is not None:
                    # check to see whether the isbn is actually already in the db but attached to another Edition
                    existing_isbn_ids = models.Identifier.objects.filter(type='isbn', value=isbn)
                    if len(existing_isbn_ids):
                        # don't try to merge editions right now, just note the need to merge
                        ed2 = existing_isbn_ids[0].edition
                        editions_to_merge.append((ed.id, g_id, isbn, ed2.id))
                    else:
                        new_id = models.Identifier(type='isbn', value=isbn, edition=ed, work=ed.work)
                        new_id.save()
                        new_isbns.append((ed.id, g_id, isbn))
                else:
                    no_isbn_found.append((ed.id, g_id, None))
        except Exception, e:
            logger.exception("add_missing_isbn_to_editions for edition.id %s: %s", ed.id, e)
            exceptions.append((ed.id, g_id, None, e))
            
    logger.info("Number of editions with Google Books IDs but not ISBNs (after): %d", 
        models.Edition.objects.filter(identifiers__type='goog').exclude(identifiers__type='isbn').count())     
    
    ok = None
    
    if confirm:
        ok = True
        for (ed_id, g_id, isbn) in new_isbns:
            if models.Edition.objects.get(id=ed_id).identifiers.get(type='isbn').value != isbn:
                ok = False
                break
            
    return {
        'new_isbns': new_isbns,
        'no_isbn_found': no_isbn_found,
        'editions_to_merge': editions_to_merge, 
        'exceptions': exceptions,
        'confirm': ok
    }


class LookupFailure(Exception):
    pass
