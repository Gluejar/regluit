"""
external library imports
"""
import json
import logging
import re
from datetime import timedelta
from xml.etree import ElementTree
from urlparse import (urljoin, urlparse)

import requests


# django imports

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import IntegrityError
from django.forms import ValidationError

from django_comments.models import Comment
from github3 import (login, GitHub)
from github3.repos.release import Release

from django.utils.timezone import now
from gitenberg.metadata.pandata import Pandata

# regluit imports

import regluit
import regluit.core.isbn
from regluit.core.validation import test_file
from regluit.marc.models import inverse_marc_rels

from . import cc
from . import models
from .parameters import WORK_IDENTIFIERS
from .validation import identifier_cleaner, unreverse_name

logger = logging.getLogger(__name__)
request_log = logging.getLogger("requests")
request_log.setLevel(logging.WARNING)

def add_by_oclc(isbn, work=None):
    # this is indirection in case we have a data source other than google
    return add_by_oclc_from_google(isbn)


def add_by_oclc_from_google(oclc):
    if oclc:
        logger.info(u"adding book by oclc %s", oclc)
    else:
        return None
    try:
        return models.Identifier.objects.get(type='oclc', value=oclc).edition
    except:
        url = "https://www.googleapis.com/books/v1/volumes"
        try:
            results = _get_json(url, {"q": '"OCLC%s"' % oclc})
        except LookupFailure, e:
            logger.exception(u"lookup failure for %s", oclc)
            return None
        if not results.has_key('items') or not results['items']:
            logger.warn(u"no google hits for %s", oclc)
            return None

        try:
            e = add_by_googlebooks_id(results['items'][0]['id'], results=results['items'][0])
            models.Identifier(type='oclc', value=oclc, edition=e, work=e.work).save()
            return e
        except LookupFailure, e:
            logger.exception(u"failed to add edition for %s", oclc)
        except IntegrityError, e:
            logger.exception(u"google books data for %s didn't fit our db", oclc)
        return None

def valid_isbn(isbn):
    try:
        return identifier_cleaner('isbn')(isbn)
    except:
        logger.exception(u"invalid isbn: %s", isbn)
        return None

def add_by_isbn(isbn, work=None, language='xx', title=''):
    if not isbn:
        return None
    try:
        e = add_by_isbn_from_google(isbn, work=work)
    except LookupFailure:
        logger.exception(u"failed google lookup for %s", isbn)
        # try again some other time
        return None
    if e:
        if e.work.language == 'xx' and language != 'xx':
            e.work.language == language
            e.work.save()
            logger.info('changed language for {} to {}'.format(isbn, language))
        return e

    logger.info(u"null came back from add_by_isbn_from_google: %s", isbn)

    # if there's a a title, we want to create stub editions and
    # works, even if google doesn't know about it # but if it's not valid,
    # forget it!

    if work:
        title = work.title if work.title else title
        if not title:
            return None
    if not title:
        return None

    isbn = valid_isbn(isbn)
    if not isbn:
        return None

    if not language or language == 'xx': # don't add unknown language
        # we don't know the language  ->'xx'
        work = models.Work(title=title, language='xx')
        work.save()
    elif not work:
        work = models.Work(title=title, language=language)
        work.save()
    e = models.Edition(title=title, work=work)
    e.save()
    e.new = True
    models.Identifier(type='isbn', value=isbn, work=work, edition=e).save()
    return e

def get_google_isbn_results(isbn):
    url = "https://www.googleapis.com/books/v1/volumes"
    try:
        results = _get_json(url, {"q": "isbn:%s" % isbn})
    except LookupFailure:
        logger.exception(u"lookup failure for %s", isbn)
        return None
    if not results.has_key('items') or not results['items']:
        logger.warn(u"no google hits for %s", isbn)
        return None
    return results

def add_ebooks(item, edition):
    access_info = item.get('accessInfo')
    if access_info:
        epub = access_info.get('epub')
        if epub and epub.get('downloadLink'):
            ebook = models.Ebook(edition=edition, format='epub',
                                 url=epub.get('downloadLink'),
                                 provider='Google Books')
            try:
                ebook.save()
            except IntegrityError:
                pass


        pdf = access_info.get('pdf')
        if pdf and pdf.get('downloadLink'):
            ebook = models.Ebook(edition=edition, format='pdf',
                                 url=pdf.get('downloadLink', None),
                                 provider='Google Books')
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
        isbn = edition.identifiers.filter(type='isbn')[0].value
    except (models.Identifier.DoesNotExist, IndexError):
        return edition

    # do a Google Books lookup on the isbn associated with the edition
    # (there should be either 0 or 1 isbns associated
    # with an edition because of integrity constraint in Identifier)

    # if we get some data about this isbn back from Google, update the edition data accordingly
    results = get_google_isbn_results(isbn)
    if not results:
        return edition
    item = results['items'][0]
    googlebooks_id = item['id']
    d = item['volumeInfo']
    if d.has_key('title'):
        title = d['title']
    else:
        title = ''
    if not title:
        # need a title to make an edition record; some crap records in GB.
        # use title from parent if available
        title = edition.work.title

    # check for language change
    language = d['language']
    # allow variants in main language (e.g., 'zh-tw')
    if len(language) > 5:
        language = language[0:5]

    # if the language of the edition no longer matches that of the parent work,
    # attach edition to the
    if edition.work.language != language:
        logger.info(u"reconnecting %s since it is %s instead of %s",
            googlebooks_id, language, edition.work.language)
        old_work = edition.work

        new_work = models.Work(title=title, language=language)
        new_work.save()
        edition.work = new_work
        edition.save()
        for identifier in edition.identifiers.all():
            logger.info(u"moving identifier %s", identifier.value)
            identifier.work = new_work
            identifier.save()
        if old_work and old_work.editions.count() == 0:
            #a dangling work; make sure nothing else is attached!
            merge_works(new_work, old_work)

    # update the edition
    edition.title = title
    edition.publication_date = d.get('publishedDate', '')
    edition.set_publisher(d.get('publisher'))
    edition.save()

    # create identifier if needed
    models.Identifier.get_or_add(
        type='goog',
        value=googlebooks_id,
        edition=edition,
        work=edition.work
    )

    for a in d.get('authors', []):
        edition.add_author(a)

    add_ebooks(item, edition)

    return edition

def get_isbn_item(items, isbn):
    # handle case where google sends back several items
    for item in items:
        volumeInfo = item.get('volumeInfo', {})
        industryIdentifiers = volumeInfo.get('industryIdentifiers', [])
        for ident in industryIdentifiers:
            if ident['identifier'] == isbn:
                return item
    else:
        return None # no items
    return item

def add_by_isbn_from_google(isbn, work=None):
    """add a book to the UnglueIt database from google based on ISBN. The work parameter
    is optional, and if not supplied the edition will be associated with
    a stub work.
    """
    if not isbn:
        return None
    if len(isbn) == 10:
        isbn = regluit.core.isbn.convert_10_to_13(isbn)


    # check if we already have this isbn
    edition = get_edition_by_id(type='isbn', value=isbn)
    if edition:
        edition.new = False
        return edition

    logger.info(u"adding new book by isbn %s", isbn)
    results = get_google_isbn_results(isbn)
    if results and 'items' in results:
        item = get_isbn_item(results['items'], isbn)
        if not item:
            logger.exception(u"no items for %s", isbn)
            return None
        try:
            return add_by_googlebooks_id(
                item['id'],
                work=work,
                results=item,
                isbn=isbn
            )
        except LookupFailure, e:
            logger.exception(u"failed to add edition for %s", isbn)
        except IntegrityError, e:
            logger.exception(u"google books data for %s didn't fit our db", isbn)
        return None
    return None

def get_work_by_id(type, value):
    if value:
        try:
            return models.Identifier.objects.get(type=type, value=value).work
        except models.Identifier.DoesNotExist:
            return None

def get_edition_by_id(type, value):
    if value:
        try:
            return models.Identifier.objects.get(type=type, value=value).edition
        except models.Identifier.DoesNotExist:
            return None


def add_by_googlebooks_id(googlebooks_id, work=None, results=None, isbn=None):
    """add a book to the UnglueIt database based on the GoogleBooks ID. The
    work parameter is optional, and if not supplied the edition will be
    associated with a stub work. isbn can be passed because sometimes passed data won't include it

    """
    isbn = valid_isbn(isbn)

    # don't ping google again if we already know about the edition
    try:
        edition = models.Identifier.objects.get(type='goog', value=googlebooks_id).edition
        edition.new = False
        if isbn:
            # check that the isbn is in db; if not, then there are two isbns for the edition
            try:
                models.Identifier.objects.get(type='isbn', value=isbn).edition
                # not going to worry about isbn_edition != edition
            except models.Identifier.DoesNotExist:
                models.Identifier.objects.create(
                    type='isbn',
                    value=isbn,
                    edition=edition,
                    work=edition.work
                )
        return edition
    except models.Identifier.DoesNotExist:
        pass

    # if google has been queried by caller, don't call again
    if results:
        item = results
    else:
        logger.info(u"loading metadata from google for %s", googlebooks_id)
        url = "https://www.googleapis.com/books/v1/volumes/%s" % googlebooks_id
        item = _get_json(url)
    d = item['volumeInfo']

    if d.has_key('title'):
        title = d['title']
    else:
        title = ''
    if not title:
        # need a title to make an edition record; some crap records in GB. 
        # use title from parent if available
        if work:
            title = work.title
        else:
            return None

    # don't add the edition to a work with a different language
    # https://www.pivotaltracker.com/story/show/17234433
    language = d['language']
    if len(language) > 5:
        language = language[0:5]
    if work and work.language != language:
        logger.info(u"not connecting %s since it is %s instead of %s",
                    googlebooks_id, language, work.language)
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
        work = get_work_by_id(type='isbn', value=isbn)
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
        logger.warning(u" whoa nellie, somebody else created an edition while we were working.")
        if work.new:
            work.delete()
        return e
    except models.Identifier.DoesNotExist:
        pass

    # because this is a new google id, we have to create a new edition
    e = models.Edition(work=work)
    e.title = title
    e.publication_date = d.get('publishedDate', '')
    e.set_publisher(d.get('publisher'))
    e.save()
    e.new = True

    # create identifier where needed
    models.Identifier(type='goog', value=googlebooks_id, edition=e, work=work).save()
    if isbn:
        models.Identifier.get_or_add(type='isbn', value=isbn, edition=e, work=work)

    for a in d.get('authors', []):
        a, created = models.Author.objects.get_or_create(name=a)
        e.add_author(a)

    add_ebooks(item, e)

    return e


def relate_isbn(isbn, cluster_size=1):
    """add a book by isbn and then see if there's an existing work to add it to so as to make a
    cluster bigger than cluster_size.
    """
    logger.info(u"finding a related work for %s", isbn)

    edition = add_by_isbn(isbn)
    if edition is None:
        return None
    if edition.work is None:
        logger.info(u"didn't add related to null work")
        return None
    if edition.work.editions.count() > cluster_size:
        return edition.work
    for other_isbn in thingisbn(isbn):
        # 979's come back as 13
        logger.debug(u"other_isbn: %s", other_isbn)
        if len(other_isbn) == 10:
            other_isbn = regluit.core.isbn.convert_10_to_13(other_isbn)
        related_edition = add_by_isbn(other_isbn, work=edition.work)
        if related_edition:
            related_language = related_edition.work.language
            if edition.work.language == related_language:
                if related_edition.work is None:
                    related_edition.work = edition.work
                    related_edition.save()
                elif related_edition.work_id != edition.work_id:
                    logger.debug(u"merge_works path 1 %s %s", edition.work_id, related_edition.work_id)
                    merge_works(related_edition.work, edition.work)
                if related_edition.work.editions.count() > cluster_size:
                    return related_edition.work
    return edition.work

def add_related(isbn):
    """add all books related to a particular ISBN to the UnglueIt database.
    The initial seed ISBN will be added if it's not already there.
    """
    # make sure the seed edition is there
    logger.info(u"adding related editions for %s", isbn)

    new_editions = []

    edition = add_by_isbn(isbn)
    if edition is None:
        return new_editions
    if edition.work is None:
        logger.warning(u"didn't add related to null work")
        return new_editions
    # this is the work everything will hang off
    work = edition.work
    other_editions = {}
    for other_isbn in thingisbn(isbn):
        # 979's come back as 13
        logger.debug(u"other_isbn: %s", other_isbn)
        if len(other_isbn) == 10:
            other_isbn = regluit.core.isbn.convert_10_to_13(other_isbn)
        related_edition = add_by_isbn(other_isbn, work=work)

        if related_edition:
            related_language = related_edition.work.language
            if edition.work.language == related_language:
                new_editions.append(related_edition)
                if related_edition.work is None:
                    related_edition.work = work
                    related_edition.save()
                elif related_edition.work_id != work.id:
                    logger.debug(u"merge_works path 1 %s %s", work.id, related_edition.work_id)
                    work = merge_works(work, related_edition.work)
            else:
                if other_editions.has_key(related_language):
                    other_editions[related_language].append(related_edition)
                else:
                    other_editions[related_language] = [related_edition]

    # group the other language editions together
    for lang_group in other_editions.itervalues():
        logger.debug(u"lang_group (ed, work): %s", [(ed.id, ed.work_id) for ed in lang_group])
        if len(lang_group) > 1:
            lang_edition = lang_group[0]
            logger.debug(u"lang_edition.id: %s", lang_edition.id)
            # compute the distinct set of works to merge into lang_edition.work
            works_to_merge = set([ed.work for ed in lang_group[1:]]) - set([lang_edition.work])
            for w in works_to_merge:
                logger.debug(u"merge_works path 2 %s %s", lang_edition.work_id, w.id)
                merged_work = merge_works(lang_edition.work, w)
        models.WorkRelation.objects.get_or_create(
            to_work=lang_group[0].work,
            from_work=work,
            relation='translation'
        )

    return new_editions

def thingisbn(isbn):
    """given an ISBN return a list of related edition ISBNs, according to
    Library Thing. (takes isbn_10 or isbn_13, returns isbn_10, except for 979 isbns,
    which come back as isbn_13')
    """
    logger.info(u"looking up %s at ThingISBN", isbn)
    url = "https://www.librarything.com/api/thingISBN/%s" % isbn
    xml = requests.get(url, headers={"User-Agent": settings.USER_AGENT}).content
    try:
        doc = ElementTree.fromstring(xml)
        return [e.text for e in doc.findall('isbn')]
    except SyntaxError:
        # LibraryThing down
        return []


def merge_works(w1, w2, user=None):
    """will merge the second work (w2) into the first (w1)
    """
    logger.info(u"merging work %s into %s", w2.id, w1.id)
    # don't merge if the works are the same or at least one of the works has no id
    #(for example, when w2 has already been deleted)
    if w1 is None or w2 is None or w1.id == w2.id or w1.id is None or w2.id is None:
        return w1

    #don't merge if the works are related.
    if w2 in w1.works_related_to.all() or w1 in w2.works_related_to.all():
        return w1
    
    # check if one of the works is a series with parts (that have their own isbn)
    if w1.works_related_from.filter(relation='part'):
        models.WorkRelation.objects.get_or_create(to_work=w2, from_work=w1, relation='part')
        return w1
    if w2.works_related_from.filter(relation='part'):
        models.WorkRelation.objects.get_or_create(to_work=w1, from_work=w2, relation='part')
        return w1
        
        
    if w2.selected_edition is not None and w1.selected_edition is None:
        #the merge should be reversed
        temp = w1
        w1 = w2
        w2 = temp
    models.WasWork(was=w2.pk, work=w1, user=user).save()
    for ww in models.WasWork.objects.filter(work=w2):
        ww.work = w1
        ww.save()
    if w2.description and not w1.description:
        w1.description = w2.description
    if w2.featured and not w1.featured:
        w1.featured = w2.featured
    if w2.is_free and not w1.is_free:
        w1.is_free = True
    if w2.age_level and not w1.age_level:
        w1.age_level = w2.age_level
    w1.save()
    for wishlist in models.Wishlist.objects.filter(works__in=[w2]):
        w2source = wishlist.work_source(w2)
        wishlist.remove_work(w2)
        wishlist.add_work(w1, w2source)
    for userprofile in w2.contributors.all():
        userprofile.works.remove(w2)
        userprofile.works.add(w1)
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
    for claim in w2.claim.all():
        claim.work = w1
        claim.dont_notify = True
        claim.save()
    for offer in w2.offers.all():
        offer.work = w1
        offer.save()
    for acq in w2.acqs.all():
        acq.work = w1
        acq.save()
    for hold in w2.holds.all():
        hold.work = w1
        hold.save()
    for landing in w2.landings.all():
        landing.object_id = w1.id
        landing.save()
    for subject in w2.subjects.all():
        if subject not in w1.subjects.all():
            w1.subjects.add(subject)
    for work_relation in w2.works_related_to.all():
        work_relation.to_work = w1
        work_relation.save()
    for work_relation in w2.works_related_from.all():
        work_relation.from_work = w1
        work_relation.save()
    w2.delete(cascade=False)
    return w1

def detach_edition(e):
    """
    will detach edition from its work, creating a new stub work. if remerge=true, will see if
    there's another work to attach to
    """
    logger.info(u"splitting edition %s from %s", e, e.work)
    w = models.Work(title=e.title, language=e.work.language)
    w.save()

    for identifier in e.identifiers.all():
        identifier.work = w
        identifier.save()

    e.work = w
    e.save()

SPAM_STRINGS = ["GeneralBooksClub.com", "AkashaPublishing.Com"]
def despam_description(description):
    """ a lot of descriptions from openlibrary have free-book promotion text;
    this removes some of it."""
    for spam in SPAM_STRINGS:
        if description.find(spam) > -1:
            return ""
    pieces = description.split("1stWorldLibrary.ORG -")
    if len(pieces) > 1:
        return pieces[1]
    pieces = description.split("a million books for free.")
    if len(pieces) > 1:
        return pieces[1]
    return description

def add_openlibrary(work, hard_refresh=False):
    if (not hard_refresh) and work.openlibrary_lookup is not None:
        # don't hit OL if we've visited in the past month or so
        if now()- work.openlibrary_lookup < timedelta(days=30):
            return
    work.openlibrary_lookup = now()
    work.save()

    # find the first ISBN match in OpenLibrary
    logger.info(u"looking up openlibrary data for work %s", work.id)

    e = None # openlibrary edition json
    w = None # openlibrary work json

    # get the 1st openlibrary match by isbn that has an associated work
    url = "https://openlibrary.org/api/books"
    params = {"format": "json", "jscmd": "details"}
    subjects = []
    for edition in work.editions.all():
        isbn_key = "ISBN:%s" % edition.isbn_13
        params['bibkeys'] = isbn_key
        try:
            e = _get_json(url, params, type='ol')
        except LookupFailure:
            logger.exception(u"OL lookup failed for  %s", isbn_key)
            e = {}
        if e.has_key(isbn_key):
            if e[isbn_key].has_key('details'):
                if e[isbn_key]['details'].has_key('oclc_numbers'):
                    for oclcnum in e[isbn_key]['details']['oclc_numbers']:
                        models.Identifier.get_or_add(
                            type='oclc',
                            value=oclcnum,
                            work=work,
                            edition=edition
                        )
                if e[isbn_key]['details'].has_key('identifiers'):
                    ids = e[isbn_key]['details']['identifiers']
                    if ids.has_key('goodreads'):
                        models.Identifier.get_or_add(
                            type='gdrd',
                            value=ids['goodreads'][0],
                            work=work, edition=edition
                        )
                    if ids.has_key('librarything'):
                        models.Identifier.get_or_add(
                            type='ltwk',
                            value=ids['librarything'][0],
                            work=work
                        )
                    if ids.has_key('google'):
                        models.Identifier.get_or_add(
                            type='goog',
                            value=ids['google'][0],
                            work=work
                        )
                    if ids.has_key('project_gutenberg'):
                        models.Identifier.get_or_add(
                            type='gute',
                            value=ids['project_gutenberg'][0],
                            work=work
                        )
                if e[isbn_key]['details'].has_key('works'):
                    work_key = e[isbn_key]['details']['works'].pop(0)['key']
                    logger.info(u"got openlibrary work %s for isbn %s", work_key, isbn_key)
                    models.Identifier.get_or_add(type='olwk', value=work_key, work=work)
                    try:
                        w = _get_json("https://openlibrary.org" + work_key, type='ol')
                        if w.has_key('description'):
                            description = w['description']
                            if isinstance(description, dict):
                                if description.has_key('value'):
                                    description = description['value']
                            description = despam_description(description)
                            if not work.description or \
                                   work.description.startswith('{') or \
                                   len(description) > len(work.description):
                                work.description = description
                                work.save()
                        if w.has_key('subjects') and len(w['subjects']) > len(subjects):
                            subjects = w['subjects']
                    except LookupFailure:
                        logger.exception(u"OL lookup failed for  %s", work_key)
    if not subjects:
        logger.warn(u"unable to find work %s at openlibrary", work.id)
        return

    # add the subjects to the Work
    for s in subjects:
        logger.info(u"adding subject %s to work %s", s, work.id)
        subject = models.Subject.set_by_name(s, work=work)

    work.save()


def _get_json(url, params={}, type='gb'):
    # TODO: should X-Forwarded-For change based on the request from client?
    headers = {'User-Agent': settings.USER_AGENT,
               'Accept': 'application/json',
               'X-Forwarded-For': '69.174.114.214'}
    if type == 'gb':
        params['key'] = settings.GOOGLE_BOOKS_API_KEY
        params['country'] = 'us'
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return json.loads(response.content)
    else:
        logger.error(u"unexpected HTTP response: %s", response)
        if response.content:
            logger.error(u"response content: %s", response.content)
        raise LookupFailure("GET failed: url=%s and params=%s" % (url, params))


def load_gutenberg_edition(title, gutenberg_etext_id, ol_work_id, seed_isbn, url,
                           format, license, lang, publication_date):
    ''' let's start with instantiating the relevant Work and Edition if they don't already exist'''

    try:
        work = models.Identifier.objects.get(type='olwk', value=ol_work_id).work
    except models.Identifier.DoesNotExist:
        # try to find an Edition with the seed_isbn and use that work to hang off of
        sister_edition = add_by_isbn(seed_isbn)
        if sister_edition.new:
            # add related editions asynchronously
            regluit.core.tasks.populate_edition.delay(sister_edition.isbn_13)
        work = sister_edition.work
        # attach the olwk identifier to this work if it's not none.
        if ol_work_id is not None:
            models.Identifier.get_or_add(type='olwk', value=ol_work_id, work=work)

    # Now pull out any existing Gutenberg editions tied to the work with the proper Gutenberg ID
    try:
        edition = models.Identifier.objects.get(type='gtbg', value=gutenberg_etext_id).edition
    except models.Identifier.DoesNotExist:
        edition = models.Edition()
        edition.title = title
        edition.work = work

        edition.save()
        models.Identifier.get_or_add(
            type='gtbg',
            value=gutenberg_etext_id,
            edition=edition, work=work
        )

    # check to see whether the Edition hasn't already been loaded first
    # search by url
    ebooks = models.Ebook.objects.filter(url=url)

    # format: what's the controlled vocab?  -- from Google -- alternative would be mimetype

    if ebooks:
        ebook = ebooks[0]
    else: # need to create new ebook
        ebook = models.Ebook()

    if len(ebooks) > 1:
        logger.warning(u"There is more than one Ebook matching url {0}".format(url))


    ebook.format = format
    ebook.provider = 'Project Gutenberg'
    ebook.url = url
    ebook.rights = license

    # is an Ebook instantiable without a corresponding Edition? (No, I think)

    ebook.edition = edition
    ebook.save()

    return ebook

class LookupFailure(Exception):
    pass

IDTABLE = [('librarything', 'ltwk'), ('goodreads', 'gdrd'), ('openlibrary', 'olwk'),
           ('gutenberg', 'gtbg'), ('isbn', 'isbn'), ('oclc', 'oclc'),
           ('googlebooks', 'goog'), ('doi', 'doi'), ('http', 'http'), ('edition_id', 'edid'),
          ]

def load_from_yaml(yaml_url, test_mode=False):
    """
    This really should be called 'load_from_github_yaml'

    if mock_ebook is True, don't construct list of ebooks from a release -- rather use an epub
    """
    all_metadata = Pandata(yaml_url)
    loader = GithubLoader(yaml_url)
    for metadata in all_metadata.get_edition_list():
        edition = loader.load_from_pandata(metadata)
        loader.load_ebooks(metadata, edition, test_mode)
    return edition.work_id if edition else None

def edition_for_ident(id_type, id_value):
    #print 'returning edition for {}: {}'.format(id_type, id_value)
    for ident in models.Identifier.objects.filter(type=id_type, value=id_value):
        return ident.edition if ident.edition else ident.work.editions[0]

def edition_for_etype(etype, metadata, default=None):
    '''
    assumes the metadata contains the isbn_etype attributes, and that the editions have been created.
    etype is 'epub', 'pdf', etc.
    '''
    isbn = metadata.identifiers.get('isbn_{}'.format(etype), None)
    if not isbn:
        isbn = metadata.identifiers.get('isbn_electronic', None)
    if isbn:
        return edition_for_ident('isbn', isbn)
    else:
        if default:
            return default
        # just return some edition
        for key in metadata.identifiers.keys():
            return edition_for_ident(key, metadata.identifiers[key])
        for key in metadata.edition_identifiers.keys():
            return edition_for_ident(key, metadata.identifiers[key])

def load_ebookfile(url, etype):
    '''
    return a ContentFile if a new ebook has been loaded
    '''
    ebfs = models.EbookFile.objects.filter(source=url)
    if ebfs:
        return None
    try:
        r = requests.get(url)
        contentfile = ContentFile(r.content)
        test_file(contentfile, etype)
        return contentfile
    except IOError, e:
        logger.error(u'could not open {}'.format(url))
    except ValidationError, e:
        logger.error(u'downloaded {} was not a valid {}'.format(url, etype))

class BasePandataLoader(object):
    def __init__(self, url):
        self.base_url = url

    def load_from_pandata(self, metadata, work=None):
        ''' metadata is a Pandata object'''

        #find an work to associate
        edition = None
        has_ed_id = False
        if metadata.url:
            new_ids = [('http', 'http', metadata.url)]
        else:
            new_ids = []
        for (identifier, id_code) in IDTABLE:
            # note that the work chosen is the last associated
            value = metadata.edition_identifiers.get(identifier, None)
            value = identifier_cleaner(id_code)(value)
            if not value:
                value = metadata.identifiers.get(identifier, None)
            if value:
                if id_code not in WORK_IDENTIFIERS:
                    has_ed_id = True
                value = value[0] if isinstance(value, list) else value
                try:
                    id = models.Identifier.objects.get(type=id_code, value=value)
                    if work and id.work and id.work_id is not work.id:
                        # dangerous! merge newer into older
                        if work.id < id.work_id:
                            work = merge_works(work, id.work)
                        else:
                            work = merge_works(id.work, work)
                    else:
                        work = id.work
                    if id.edition and not edition:
                        edition = id.edition
                except models.Identifier.DoesNotExist:
                    if id_code != 'edid' or not has_ed_id:  #last in loop
                        # only need to create edid if there is no edition id for the edition
                        new_ids.append((identifier, id_code, value))

        if not work:
            work = models.Work.objects.create(title=metadata.title, language=metadata.language)
        if not edition:
            if metadata.edition_note:
                (note, created) = models.EditionNote.objects.get_or_create(note=metadata.edition_note)
            else:
                note = None
            edition = models.Edition.objects.create(
                title=metadata.title,
                work=work,
                note=note,
            )
        for (identifier, id_code, value) in new_ids:
            models.Identifier.set(
                type=id_code,
                value=value,
                edition=edition if id_code not in WORK_IDENTIFIERS else None,
                work=work,
            )
        if metadata.publisher: #always believe yaml
            edition.set_publisher(metadata.publisher)

        if metadata.publication_date: #always believe yaml
            edition.publication_date = metadata.publication_date

        #be careful about overwriting the work description
        if metadata.description and len(metadata.description) > len(work.description):
            # don't over-write reasonably long descriptions
            if len(work.description) < 500:
                work.description = metadata.description

        if metadata.creator and not edition.authors.count():
            edition.authors.clear()
            for key in metadata.creator.keys():
                creators = metadata.creator[key]
                rel_code = inverse_marc_rels.get(key, None)
                if not rel_code:
                    rel_code = inverse_marc_rels.get(key.rstrip('s'), 'auth')
                creators = creators if isinstance(creators, list) else [creators]
                for creator in creators:
                    edition.add_author(unreverse_name(creator.get('agent_name', '')), relation=rel_code)
        for yaml_subject in metadata.subjects: #always add yaml subjects (don't clear)
            if isinstance(yaml_subject, tuple):
                (authority, heading) = yaml_subject
            elif isinstance(yaml_subject, str) or isinstance(yaml_subject, unicode) :
                (authority, heading) = ('', yaml_subject)
            else:
                continue
            subject = models.Subject.set_by_name(heading, work=work, authority=authority)

        # the default edition uses the first cover in covers.
        for cover in metadata.covers:
            if cover.get('image_path', False):
                edition.cover_image = urljoin(self.base_url, cover['image_path'])
                break
            elif cover.get('image_url', False):
                edition.cover_image = cover['image_url']
                break
        work.save()
        edition.save()
        return edition

    def load_ebooks(self, metadata, edition, test_mode=False, user=None):
        default_edition = edition
        license = cc.license_from_cc_url(metadata.rights_url)
        for key in ['epub', 'pdf', 'mobi']:
            url = metadata.metadata.get('download_url_{}'.format(key), None)
            if url:
                edition = edition_for_etype(key, metadata, default=default_edition)
                if edition:
                    contentfile = load_ebookfile(url, key)
                    if contentfile:
                        contentfile_name = '/loaded/ebook_{}.{}'.format(edition.id, key)
                        path = default_storage.save(contentfile_name, contentfile)
                        ebf = models.EbookFile.objects.create(
                            format=key,
                            edition=edition,
                            source=url,
                        )
                        ebf.file.save(contentfile_name, contentfile)
                        ebf.file.close()
                        ebook = models.Ebook.objects.create(
                            url=ebf.file.url,
                            provider='Unglue.it',
                            rights=license,
                            format=key,
                            edition=edition,
                            filesize=contentfile.size,
                            active=False,
                            user=user,
                        )
                        ebf.ebook = ebook
                        ebf.save()


class GithubLoader(BasePandataLoader):
    def load_ebooks(self, metadata, edition, test_mode=False):
        # create Ebook for any ebook in the corresponding GitHub release
        # assuming yaml_url of form (from GitHub, though not necessarily GITenberg)
        # https://github.com/GITenberg/Adventures-of-Huckleberry-Finn_76/raw/master/metadata.yaml

        url_path = urlparse(self.base_url).path.split("/")
        (repo_owner, repo_name) = (url_path[1], url_path[2])
        repo_tag = metadata._version
        # allow for there not to be a token in the settings
        try:
            token = settings.GITHUB_PUBLIC_TOKEN
        except:
            token = None

        if metadata._version and not metadata._version.startswith('0.0.'):
            # use GitHub API to compute the ebooks in release until we're in test mode
            if test_mode:
                # not using ebook_name in this code
                ebooks_in_release = [('epub', 'book.epub')]
            else:
                ebooks_in_release = ebooks_in_github_release(repo_owner, repo_name, repo_tag, token=token)

            for (ebook_format, ebook_name) in ebooks_in_release:
                (book_name_prefix, _) = re.search(r'(.*)\.([^\.]*)$', ebook_name).groups()
                (ebook, created) = models.Ebook.objects.get_or_create(
                    url=git_download_from_yaml_url(
                        self.base_url,
                        metadata._version,
                        edition_name=book_name_prefix,
                        format_=ebook_format
                    ),
                    provider='Github',
                    rights=cc.match_license(metadata.rights),
                    format=ebook_format,
                    edition=edition,
                    )
                ebook.set_version(metadata._version)


def git_download_from_yaml_url(yaml_url, version, edition_name='book', format_='epub'):
    '''
     go from https://github.com/GITenberg/Adventures-of-Huckleberry-Finn_76/raw/master/metadata.yaml
     to https://github.com/GITenberg/Adventures-of-Huckleberry-Finn_76/releases/download/v0.0.3/Adventures-of-Huckleberry-Finn.epub
    '''
    if yaml_url.endswith('raw/master/metadata.yaml'):
        repo_url = yaml_url[0:-24]
        #print (repo_url,version,edition_name)
        ebook_url = repo_url + 'releases/download/' + version + '/' + edition_name + '.' + format_
        return ebook_url


def release_from_tag(repo, tag_name):
    """Get a release by tag name.
    release_from_tag() returns a release with specified tag
    while release() returns a release with specified release id
    :param str tag_name: (required) name of tag
    :returns: :class:`Release <github3.repos.release.Release>`
    """
    # release_from_tag adapted from
    # https://github.com/sigmavirus24/github3.py/blob/38de787e465bffc63da73d23dc51f50d86dc903d/github3/repos/repo.py#L1781-L1793

    url = repo._build_url('releases', 'tags', tag_name,
                          base_url=repo._api)
    json_obj = repo._json(repo._get(url), 200)
    return Release(json_obj, repo) if json_obj else None

def ebooks_in_github_release(repo_owner, repo_name, tag, token=None):
    """
    returns a list of (book_type, book_name) for a given GitHub release (specified by
    owner, name, tag).  token is a GitHub authorization token -- useful for accessing
    higher rate limit in the GitHub API
    """

    # map mimetype to file extension
    EBOOK_FORMATS = dict([(v, k) for (k, v) in settings.CONTENT_TYPES.items()])

    if token is not None:
        gh = login(token=token)
    else:
        # anonymous access
        gh = GitHub()

    repo = gh.repository(repo_owner, repo_name)
    release = release_from_tag(repo, tag)

    return [(EBOOK_FORMATS.get(asset.content_type), asset.name)
            for asset in release.assets()
            if EBOOK_FORMATS.get(asset.content_type) is not None]

def add_from_bookdatas(bookdatas):
    ''' bookdatas  are iterators of scrapers '''
    editions = []
    for bookdata in bookdatas:
        edition = work = None
        loader = BasePandataLoader(bookdata.base)
        pandata = Pandata()
        pandata.metadata = bookdata.metadata
        for metadata in pandata.get_edition_list():
            edition = loader.load_from_pandata(metadata, work)
            work = edition.work
        loader.load_ebooks(pandata, edition)
        if edition:
            editions.append(edition)
    return editions
