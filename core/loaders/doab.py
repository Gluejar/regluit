#!/usr/bin/env python
# encoding: utf-8
import datetime
import logging
import re

import requests

from io import BytesIO
from PIL import Image, UnidentifiedImageError

from django.conf import settings
from django.db.models import Q

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from oaipmh.client import Client
from oaipmh.error import IdDoesNotExistError, NoRecordsMatchError
from oaipmh.metadata import MetadataRegistry

from regluit.core import bookloader, cc
from regluit.core import models, tasks
from regluit.core.bookloader import merge_works
from regluit.core.models.loader import type_for_url
from regluit.core.validation import identifier_cleaner, valid_subject, explode_bics

from . import scrape_language
from .doab_utils import (
    doab_lang_to_iso_639_1, doab_cover, doab_reader, online_to_download, STOREPROVIDERS)

logger = logging.getLogger(__name__)

def unlist(alist):
    if not alist:
        return None
    return alist[0]

SPRINGER_COVER = re.compile(r'ftp.+springer\.de.+(\d{13}\.jpg)$', flags=re.U)
SPRINGER_IMAGE = u'https://images.springer.com/sgw/books/medium/{}.jpg'
def store_doab_cover(doab_id, redo=False):

    """
    returns tuple: 1) cover URL, 2) whether newly created (boolean)
    """
    if not doab_id:
        return (None, False)    

    cover_file_name = '/doab/%s' % doab_id

    # if we don't want to redo and the cover exists, return the URL of the cover

    if not redo and default_storage.exists(cover_file_name):
        return (default_storage.url(cover_file_name), False)

    # download cover image to cover_file
    url = doab_cover(doab_id)
    headers = {"User-Agent": settings.USER_AGENT}
    if not url:
        return (None, False)
    try:
        r = requests.get(url, allow_redirects=False, headers=headers) # requests doesn't handle ftp redirects.
        if r.status_code == 302:
            redirurl = r.headers['Location']
            if redirurl.startswith(u'ftp'):
                springerftp = SPRINGER_COVER.match(redirurl)
                if springerftp:
                    redirurl = SPRINGER_IMAGE.format(springerftp.groups(1))
                    r = requests.get(redirurl, headers=headers)
            else:
                r = requests.get(url, headers=headers)
        if not r.content:
            logger.warning('No image content for doab_id=%s: %s', doab_id, e)
            return (None, False)
            
        #test that cover is good
        image_bytes = BytesIO(r.content)
        try:
            image = Image.open(image_bytes)
        except UnidentifiedImageError:
            warning(f'No image found for {doab_id}')
            return (None, False)

        cover_file = ContentFile(r.content)
        content_type = r.headers.get('content-type', '')
        if not 'image/' in content_type:
            logger.warning('Non-image returned for doab_id=%s', doab_id)
            return (None, False)
        cover_file.content_type = content_type

        

        default_storage.save(cover_file_name, cover_file)
        return (default_storage.url(cover_file_name), True)
    except Exception as e:
        # if there is a problem, return None for cover URL
        logger.warning('Failed to make cover image for doab_id=%s: %s', doab_id, e)
        return (None, False)

def update_cover_doab(doab_id, edition, store_cover=True, redo=True):
    """
    update the cover url for work with doab_id
    if store_cover is True, use the cover from our own storage
    """
    if store_cover:
        (cover_url, new_cover) = store_doab_cover(doab_id, redo=redo)
    else:
        cover_url = doab_cover(doab_id)

    if cover_url is not None:
        edition.cover_image = cover_url
        edition.save()
        good = edition.cover_image_small() and edition.cover_image_thumbnail()
        if not good:
            # oh well
            logger.warning("Couldn't make thumbnails for %s using %s", doab_id, cover_url)
            edition.cover_image = None
            edition.save()
        return cover_url
    return None

def attach_more_doab_metadata(edition, description, subjects,
                              publication_date, publisher_name=None, language=None,
                              dois=None, authors=None, editors=None):

    """
    for given edition, attach description, subjects, publication date to
    corresponding Edition and Work
    """
    # if edition doesn't have a publication date, update it
    if not edition.publication_date:
        edition.publication_date = publication_date

    # if edition.publisher_name is empty, set it
    if not edition.publisher_name:
        edition.set_publisher(publisher_name)

    edition.save()

    # attach description to work if it's not empty
    work = edition.work
    if description and not work.description:
        work.description = description.replace('\r\n', '\n')

    # update subjects
    subjects = explode_bics(subjects)
    for s in subjects:
        if valid_subject(s):
            models.Subject.set_by_name(s, work=work)

    # set reading level of work if it's empty; doab is for adults.
    if not work.age_level:
        work.age_level = '18-'

    if language and language != 'xx':
        work.language = language
    work.save()

    if authors or editors:
        authlist = creator_list(authors, editors)
        if edition.authors.all().count() < len(authlist):
            edition.authors.clear()
            if authlist is not None:
                for [rel, auth] in authlist:
                    edition.add_author(auth, rel)

    for doi in dois if dois else []:
        if not edition.work.doi:
            models.Identifier.set('doi', doi, work=edition.work)
            break
    return edition

def add_all_isbns(isbns, work, language=None, title=None):
    first_edition = None
    for isbn in isbns:
        edition = bookloader.add_by_isbn(isbn, work, language=language, title=title)
        if edition:
            first_edition = first_edition if first_edition else edition
            if work and (edition.work_id != work.id):
                if work.doab and edition.work.doab and work.doab != edition.work.doab:
                    if work.created < edition.work.created:
                        work = merge_works(work, edition.work)
                    else:
                        work = merge_works(edition.work, work)
            else:
                work = edition.work
    return work, first_edition

def load_doab_edition(title, doab_id, url, format, rights,
                      language, isbns, provider, dois=None, **kwargs):
    """
    load a record from doabooks.org represented by input parameters and return an ebook
    """
    logger.info('load doab %s %s %s %s %s', doab_id, format, rights, language, provider)
    url = url.strip()
    if language and isinstance(language, list):
        language = language[0]
    if language == 'xx' and format == 'online':
        language = scrape_language(url)
    # check to see whether the Edition hasn't already been loaded first
    # search by url
    ebooks = models.Ebook.objects.filter(url=url)

    # 1 match
    # > 1 matches
    # 0 match

    # simplest case -- if match (1 or more), we could check whether any
    # ebook.edition.work has a doab id matching given doab_id

    # put a migration to force Ebook.url to be unique id

    # if yes, then return one of the Edition(s) whose work is doab_id
    # if no, then
    ebook = None
    if len(ebooks) > 1:
        raise Exception("There is more than one Ebook matching url {0}".format(url))
    if len(ebooks) == 1:
        ebook = ebooks[0]
        if not ebook.edition.work.doab or ebook.edition.work.doab == doab_id:
            models.Identifier.get_or_add(type='doab', value=doab_id, work=ebook.edition.work)

            if not ebook.rights:
                ebook.rights = rights
                ebook.save()

            # update the cover id
            update_cover_doab(doab_id, ebook.edition, redo=False)

            # attach more metadata
            attach_more_doab_metadata(
                ebook.edition,
                description=unlist(kwargs.get('description')),
                subjects=kwargs.get('subject'),
                publication_date=unlist(kwargs.get('date')),
                publisher_name=unlist(kwargs.get('publisher')),
                language=language,
                authors=kwargs.get('creator'),
                dois=dois,
            )
            # make sure all isbns are added
            add_all_isbns(isbns, ebook.edition.work, language=language, title=title)
            return ebook.edition
        # don't add a second doab to an existing Work
        return None
    # remaining case --> no ebook, load record, create ebook if there is one.
    assert not ebooks


    # we need to find the right Edition/Work to tie Ebook to...

    # look for the Edition with which to associate ebook.
    # loop through the isbns to see whether we get one that is not None

    work, edition = add_all_isbns(isbns, None, language=language, title=title)
    if doab_id and not work:
        # make sure there's not already a doab_id
        idents = models.Identifier.objects.filter(type='doab', value=doab_id)
        for ident in idents:
            edition = ident.work.preferred_edition
            work = edition.work
            break

    if edition is not None:
        # if this is a new edition, then add related editions SYNCHRONOUSLY
        if getattr(edition, 'new', False):
            tasks.populate_edition(edition.isbn_13)
        edition.refresh_from_db()
        doab_identifer = models.Identifier.get_or_add(type='doab', value=doab_id,
                                                      work=edition.work)

    # we need to create Edition(s) de novo
    else:
        # if there is a Work with doab_id already, attach any new Edition(s)
        try:
            work = models.Identifier.objects.get(type='doab', value=doab_id).work
        except models.Identifier.DoesNotExist:
            if language:
                work = models.Work(language=language, title=title, age_level='18-')
            else:
                work = models.Work(language='xx', title=title, age_level='18-')
            work.save()
            doab_identifer = models.Identifier.get_or_add(type='doab', value=doab_id,
                                                          work=work)

        # if work has any ebooks already, attach the ebook to the corresponding edition
        # otherwise pick the first one
        # pick the first edition as the one to tie ebook to
        editions_with_ebooks = models.Edition.objects.filter(Q(work__id=work.id) & \
                                                      Q(ebooks__isnull=False)).distinct()
        if editions_with_ebooks:
            edition = editions_with_ebooks[0]
        elif work.editions.all():
            edition = work.editions.first()
        else:
            edition = models.Edition(work=work, title=title)
            edition.save()

    # make the edition the selected_edition of the work
    work.selected_edition = edition
    work.save()

    if format in ('pdf', 'epub', 'html', 'online') and rights:
        ebook = models.Ebook()
        if format == 'online' and provider in STOREPROVIDERS:
            ebook.format = 'bookstore'
        else:
            ebook.format = format
        ebook.provider = provider
        ebook.url = url
        ebook.rights = rights
        # tie the edition to ebook
        ebook.edition = edition
        if format == "online":
            ebook.active = False
        ebook.save()

    # update the cover id (could be done separately)
    cover_url = update_cover_doab(doab_id, edition, redo=False)

    # attach more metadata
    attach_more_doab_metadata(
        edition,
        description=unlist(kwargs.get('description')),
        subjects=kwargs.get('subject'),
        publication_date=unlist(kwargs.get('date')),
        publisher_name=unlist(kwargs.get('publisher')),
        authors=kwargs.get('creator'),
        editors=kwargs.get('editor'),
        dois=dois,
    )
    if rights:
        for ebook in edition.ebooks.all():
            if not ebook.rights:
                ebook.rights = rights
                ebook.save()

    return edition

#
#tools to parse the author lists in doab.csv
#

au = re.compile(r'\(Authors?\)', flags=re.U)
ed = re.compile(r'\([^\)]*(dir.|[Eeé]ds?.|org.|coord.|Editor|a cura di|archivist)[^\)]*\)',
                flags=re.U)
tr = re.compile(r'\([^\)]*([Tt]rans.|tr.|translated by)[^\)]*\)', flags=re.U)
ai = re.compile(r'\([^\)]*(Introduction|Foreword)[^\)]*\)', flags=re.U)
ds = re.compile(r'\([^\)]*(designer)[^\)]*\)', flags=re.U)
cm = re.compile(r'\([^\)]*(comp.)[^\)]*\)', flags=re.U)
namelist = re.compile(r'([^,]+ [^, ]+)(, | and )([^,]+ [^, ]+)', flags=re.U)
namesep = re.compile(r', | and ', flags=re.U)
namesep2 = re.compile(r';|/| and ', flags=re.U)
isbnsep = re.compile(r'[ ,/;\t\.]+|Paper: *|Cloth: *|eISBN: *|Hardcover: *', flags=re.U)
edlist = re.compile(r'([eE]dited by| a cura di|editors)', flags=re.U)

def fnf(auth):
    if len(auth) > 60:
        return auth #probably corp name
    parts = re.sub(r' +', u' ', auth).split(u',')
    if len(parts) == 1:
        return  parts[0].strip()
    if len(parts) == 2:
        return u'{} {}'.format(parts[1].strip(), parts[0].strip())
    if parts[1].strip() in ('der', 'van', 'von', 'de', 'ter'):
        return u'{} {} {}'.format(parts[2].strip(), parts[1].strip(), parts[0].strip())
    return u'{} {}, {}'.format(parts[2].strip(), parts[0].strip(), parts[1].strip())


def creator(auth, editor=False):
    auth = auth.strip()
    if auth in (u'', u'and'):
        return None
    if re.search(ed, auth) or editor:
        return [u'edt', fnf(ed.sub(u'', auth))]
    if re.search(tr, auth):
        return [u'trl', fnf(tr.sub(u'', auth))]
    if re.search(ai, auth):
        return [u'aui', fnf(ai.sub(u'', auth))]
    if re.search(ds, auth):
        return [u'dsr', fnf(ds.sub(u'', auth))]
    if re.search(cm, auth):
        return [u'com', fnf(cm.sub(u'', auth))]

    auth = au.sub('', auth)
    return ['aut', fnf(auth)]

def creator_list(creators, editors):
    auths = []
    if creators:
        for auth in creators:
            auths.append(creator(auth))
    if editors:
        for auth in editors:
            auths.append(creator(auth, editor=True))
    return auths

DOAB_OAIURL = 'https://directory.doabooks.org/oai/request'
DOAB_PATT = re.compile(r'oai:directory\.doabooks\.org:(.*)')
mdregistry = MetadataRegistry()
mdregistry.registerReader('oai_dc', doab_reader)
doab_client = Client(DOAB_OAIURL, mdregistry)
isbn_cleaner = identifier_cleaner('isbn', quiet=True)
doi_cleaner = identifier_cleaner('doi', quiet=True)
ISBNSEP = re.compile(r'[/;]+')

def add_by_doab(doab_id, record=None):
    try:
        record = record if record else doab_client.getRecord(
            metadataPrefix='oai_dc',
            identifier='oai:directory.doabooks.org:{}'.format(doab_id)
        )
        if not record[1]:
            logger.error('No content in record %s', record)
            return None
        metadata = record[1].getMap()
        isbns = []
        dois = []
        urls = []
        for ident in metadata.pop('isbn', []):
            isbn_strings = ISBNSEP.split(ident[6:].strip())
            for isbn_string in isbn_strings:
                isbn = isbn_cleaner(isbn_string)
                if isbn:
                    isbns.append(isbn)
        for ident in metadata.pop('doi', []):
            ident = doi_cleaner(ident)
            if ident:
                dois.append(ident)
        for ident in metadata.pop('identifier', []):
            if ident.find('doabooks.org') >= 0:
                # should already know the doab_id
                continue
            if ident.startswith('http'):
                urls.append(ident)
        language = doab_lang_to_iso_639_1(unlist(metadata.pop('language', None)))
        xurls = []
        for url in urls:
            xurls += online_to_download(url)
        urls = xurls
        edition = None
        title = unlist(metadata.pop('title', None))
        license = cc.license_from_cc_url(unlist(metadata.pop('rights', None)))
        for dl_url in urls:
            format = type_for_url(dl_url)
            if 'format' in metadata:
                del metadata['format']
            added_edition = load_doab_edition(
                title,
                doab_id,
                dl_url,
                format,
                license,
                language,
                isbns,
                models.Ebook.infer_provider(dl_url) if dl_url else None,
                dois=dois,
                **metadata
            )
            edition = added_edition if added_edition else edition
        return edition
    except IdDoesNotExistError as e:
        logger.error(e)
        return None


def getdoab(url):
    id_match = DOAB_PATT.search(url)
    if id_match:
        return id_match.group(1)
    return False


def get_doab_record(doab_id):
    record_id = 'oai:directory.doabooks.org:%s' % doab_id
    try:
        return doab_client.getRecord(metadataPrefix='oai_dc', identifier=record_id)
    except IdDoesNotExistError:
        return None

def load_doab_oai(from_date, until_date, limit=100):
    '''
    use oai feed to get oai updates
    '''
    start = datetime.datetime.now()
    if from_date:
        from_ = from_date
    else:
        # last 15 days
        from_ = datetime.datetime.now() - datetime.timedelta(days=15)
    num_doabs = 0
    new_doabs = 0
    lasttime = datetime.datetime(2000, 1, 1)
    try:
        for record in doab_client.listRecords(metadataPrefix='oai_dc', from_=from_,
                                              until=until_date):
            if not record[1]:
                continue
            item_type = unlist(record[1].getMap().get('type', None))
            if item_type != 'book':
                continue
            ident = record[0].identifier()
            datestamp = record[0].datestamp()
            lasttime = datestamp if datestamp > lasttime else lasttime
            doab = getdoab(ident)
            if doab:
                num_doabs += 1
                e = add_by_doab(doab, record=record)
                if not e:
                    logger.error('null edition for doab #%s', doab)
                    continue
                if e.created > start:
                    new_doabs += 1
                title = e.title if e else None
                logger.info(u'updated:\t%s\t%s', doab, title)
            if num_doabs >= limit:
                break
    except NoRecordsMatchError:
        pass
    return num_doabs, new_doabs, lasttime
    