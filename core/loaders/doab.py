#!/usr/bin/env python
# encoding: utf-8
import datetime
import json
import logging
import re

import requests

from django.db.models import Q

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from oaipmh.client import Client
from oaipmh.error import IdDoesNotExistError
from oaipmh.metadata import MetadataRegistry, oai_dc_reader

from regluit.core import bookloader, cc
from regluit.core import models, tasks
from regluit.core.bookloader import merge_works
from regluit.core.isbn import ISBN
from regluit.core.loaders.utils import type_for_url
from regluit.core.validation import identifier_cleaner, valid_subject

from . import scrape_language
from .doab_utils import doab_lang_to_iso_639_1, online_to_download, url_to_provider

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

    cover_file_name = '/doab/%s/cover' % (doab_id)

    # if we don't want to redo and the cover exists, return the URL of the cover

    if not redo and default_storage.exists(cover_file_name):
        return (default_storage.url(cover_file_name), False)

    # download cover image to cover_file
    url = "http://www.doabooks.org/doab?func=cover&rid={0}".format(doab_id)
    try:
        r = requests.get(url, allow_redirects=False) # requests doesn't handle ftp redirects.
        if r.status_code == 302:
            redirurl = r.headers['Location']
            if redirurl.startswith(u'ftp'):
                springerftp = SPRINGER_COVER.match(redirurl)
                if springerftp:
                    redirurl = SPRINGER_IMAGE.format(springerftp.groups(1))
                    r = requests.get(redirurl)
            else:
                r = requests.get(url)
        else:
            r = requests.get(url)
        cover_file = ContentFile(r.content)
        content_type = r.headers.get('content-type', '')
        if u'text/html' in content_type:
            logger.warning('Cover return html for doab_id={}: {}'.format(doab_id, e))
            return (None, False)
        cover_file.content_type = content_type
            

        default_storage.save(cover_file_name, cover_file)
        return (default_storage.url(cover_file_name), True)
    except Exception, e:
        # if there is a problem, return None for cover URL
        logger.warning('Failed to make cover image for doab_id={}: {}'.format(doab_id, e))
        return (None, False)

def update_cover_doab(doab_id, edition, store_cover=True, redo=True):
    """
    update the cover url for work with doab_id
    if store_cover is True, use the cover from our own storage
    """
    if store_cover:
        (cover_url, new_cover) = store_doab_cover(doab_id, redo=redo)
    else:
        cover_url = "http://www.doabooks.org/doab?func=cover&rid={0}".format(doab_id)

    if cover_url is not None:
        edition.cover_image = cover_url
        edition.save()
        return cover_url
    return None

def attach_more_doab_metadata(edition, description, subjects,
                              publication_date, publisher_name=None, language=None, authors=u''):

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
    if not work.description:
        work.description = description

    # update subjects
    for s in subjects:
        if valid_subject(s):
            models.Subject.set_by_name(s, work=work)

    # set reading level of work if it's empty; doab is for adults.
    if not work.age_level:
        work.age_level = '18-'

    if language and language != 'xx':
        work.language = language
    work.save()

    if authors and authors == authors: # test for authors != NaN
        authlist = creator_list(authors)
        if edition.authors.all().count() < len(authlist):
            edition.authors.clear()
            if authlist is not None:
                for [rel, auth] in authlist:
                    edition.add_author(auth, rel)

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
                      language, isbns,
                      provider, **kwargs):

    """
    load a record from doabooks.org represented by input parameters and return an ebook
    """
    logger.info('load doab {} {} {} {} {}'.format(doab_id, format, rights, language, provider))
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
    elif len(ebooks) == 1:
        ebook = ebooks[0]
        doab_identifer = models.Identifier.get_or_add(type='doab', value=doab_id,
                                                      work=ebook.edition.work)
        if not ebook.rights:
            ebook.rights = rights
            ebook.save()
        
        # update the cover id
        cover_url = update_cover_doab(doab_id, ebook.edition, redo=False)

        # attach more metadata
        attach_more_doab_metadata(
            ebook.edition,
            description=unlist(kwargs.get('description')),
            subjects=kwargs.get('subject'),
            publication_date=unlist(kwargs.get('date')),
            publisher_name=unlist(kwargs.get('publisher')),
            language=language,
            authors=kwargs.get('creator'),
        )
        # make sure all isbns are added
        add_all_isbns(isbns, ebook.edition.work, language=language, title=title)
        return ebook.edition

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
            edition = work.editions.all()[0]
        else:
            edition = models.Edition(work=work, title=title)
            edition.save()

    # make the edition the selected_edition of the work
    work.selected_edition = edition
    work.save()

    if format in ('pdf', 'epub', 'mobi', 'html', 'online') and rights:
        ebook = models.Ebook()
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
ed = re.compile(r'\([^\)]*(dir.|[Eeé]ds?.|org.|coord.|Editor|a cura di|archivist)[^\)]*\)', flags=re.U)
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
    elif len(parts) == 2:
        return u'{} {}'.format(parts[1].strip(), parts[0].strip())
    else:
        if parts[1].strip() in ('der', 'van', 'von', 'de', 'ter'):
            return u'{} {} {}'.format(parts[2].strip(), parts[1].strip(), parts[0].strip())
        #print auth
        #print re.search(namelist,auth).group(0)
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

def creator_list(creators):
    auths = []
    for auth in creators:
        auths.append(creator(auth))
    return auths

DOAB_OAIURL = 'https://www.doabooks.org/oai'
DOAB_PATT = re.compile(r'[\./]doabooks\.org/doab\?.*rid:(\d{1,8}).*')
mdregistry = MetadataRegistry()
mdregistry.registerReader('oai_dc', oai_dc_reader)
doab_client = Client(DOAB_OAIURL, mdregistry)
isbn_cleaner = identifier_cleaner('isbn', quiet=True)
ISBNSEP = re.compile(r'[/]+')

def add_by_doab(doab_id, record=None):
    try:
        record = record if record else doab_client.getRecord(
            metadataPrefix='oai_dc',
            identifier='oai:doab-books:{}'.format(doab_id)
        )
        metadata = record[1].getMap()
        isbns = []
        url = None
        for ident in metadata.pop('identifier', []):
            if ident.startswith('ISBN: '):
                isbn_strings = ISBNSEP.split(ident[6:].strip())
                for isbn_string in isbn_strings:
                    isbn = isbn_cleaner(isbn_string)
                    if isbn:
                        isbns.append(isbn)
            elif ident.find('doabooks.org') >= 0:
                # should already know the doab_id
                continue
            else:
                url = ident
        language = doab_lang_to_iso_639_1(unlist(metadata.pop('language', None)))
        urls = online_to_download(url)
        edition = None
        title = unlist(metadata.pop('title', None))
        license = cc.license_from_cc_url(unlist(metadata.pop('rights', None)))
        for dl_url in urls:
            format = type_for_url(dl_url)
            if 'format' in metadata:
                del metadata['format']
            edition = load_doab_edition(
                title,
                doab_id,
                dl_url,
                format,
                license,
                language,
                isbns,
                url_to_provider(dl_url) if dl_url else None,
                **metadata
            )
        else:
            if 'format' in metadata:
                del metadata['format']
            edition = load_doab_edition(
                title,
                doab_id,
                '',
                '',
                license,
                language,
                isbns,
                None,
                **metadata
            )
        return edition
    except IdDoesNotExistError:
        return None


def getdoab(url):
    id_match = DOAB_PATT.search(url)
    if id_match:
        return id_match.group(1)
    return False

def load_doab_oai(from_year=None, limit=100000):
    '''
    use oai feed to get oai updates
    '''
    if from_year:
        from_ = datetime.datetime(year=from_year, month=1, day=1)
    else: 
        # last 15 days
        from_ = datetime.datetime.now() - datetime.timedelta(days=15)
    doab_ids = []
    for record in doab_client.listRecords(metadataPrefix='oai_dc', from_=from_):
        if not record[1]:
            continue
        item_type = unlist(record[1].getMap().get('type', None))
        if item_type != 'book':
            continue
        idents = record[1].getMap()['identifier']
        if idents:
            for ident in idents:
                doab = getdoab(ident)
                if doab:
                    doab_ids.append(doab)
                    e = add_by_doab(doab, record=record)
                    title = e.title if e else None
                    logger.info(u'updated:\t{}\t{}'.format(doab, title))
        if len(doab_ids) > limit:
            break
