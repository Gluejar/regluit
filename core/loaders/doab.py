import logging
import json
from itertools import islice

import requests

from django.db.models import (Q, F)

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

import regluit
from regluit.core import models, tasks
from regluit.core import bookloader
from regluit.core.bookloader import add_by_isbn, merge_works

logger = logging.getLogger(__name__)

def store_doab_cover(doab_id, redo=False):
    
    """
    returns tuple: 1) cover URL, 2) whether newly created (boolean)
    """
    
    cover_file_name= '/doab/%s/cover' % (doab_id)
    
    # if we don't want to redo and the cover exists, return the URL of the cover
    
    if not redo and default_storage.exists(cover_file_name):
        return (default_storage.url(cover_file_name), False)
        
    # download cover image to cover_file
    url = "http://www.doabooks.org/doab?func=cover&rid={0}".format(doab_id)
    try:
        r = requests.get(url)
        cover_file = ContentFile(r.content)
        cover_file.content_type = r.headers.get('content-type', '')

        path = default_storage.save(cover_file_name, cover_file)    
        return (default_storage.url(cover_file_name), True)
    except Exception, e:
        # if there is a problem, return None for cover URL
        return (None, False)

def update_cover_doab(doab_id, store_cover=True):
    """
    update the cover url for work with doab_id
    if store_cover is True, use the cover from our own storage
    """
    work = models.Identifier.objects.get(type='doab', value=doab_id).work
    edition = work.preferred_edition
    
    if store_cover:
        (cover_url, new_cover) = store_doab_cover(doab_id)
    else:
        cover_url = "http://www.doabooks.org/doab?func=cover&rid={0}".format(doab_id)

    if cover_url is not None:
        edition.cover_image = cover_url
        edition.save()
        return cover_url
    else:
        return None
    
def attach_more_doab_metadata(edition, description, subjects,
                              publication_date, publisher_name=None, language=None):
    
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
        if bookloader.valid_subject(s):
            work.subjects.add(models.Subject.objects.get_or_create(name=s)[0])
    
    # set reading level of work if it's empty; doab is for adults.
    if not work.age_level:
        work.age_level = '18-'
        
    if language:
        work.language = language
    work.save()
               
    return edition

def add_all_isbns(isbns, work, language=None, title=None):
    for isbn in isbns:
        first_edition = None
        edition = bookloader.add_by_isbn(isbn, work, language=language, title=title)
        if edition:
            first_edition = first_edition if first_edition else edition 
            if work and (edition.work.id != work.id): 
                if work.created < edition.work.created:
                    merge_works(work, edition.work)
                else:
                    merge_works(edition.work, work)
            else:
                work = edition.work
    return first_edition

def load_doab_edition(title, doab_id, url, format, rights,
                      language, isbns,
                      provider, **kwargs):
    
    """
    load a record from doabooks.org represented by input parameters and return an ebook
    """
    if language and isinstance(language, list):
        language = language[0]
        
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
        doab_identifer = models.Identifier.get_or_add(type='doab',value=doab_id, 
                                               work=ebook.edition.work)
        # update the cover id 
        cover_url = update_cover_doab(doab_id)
        
        # attach more metadata
        attach_more_doab_metadata(ebook.edition, 
                                  description=kwargs.get('description'),
                                  subjects=kwargs.get('subject'),
                                  publication_date=kwargs.get('date'),
                                  publisher_name=kwargs.get('publisher'),
                                  language=language)
        # make sure all isbns are added
        add_all_isbns(isbns, None, language=language, title=title)
        return ebook
    
    # remaining case --> no ebook, load record, create ebook if there is one.
    assert len(ebooks) == 0
            

    # we need to find the right Edition/Work to tie Ebook to...
        
    # look for the Edition with which to associate ebook.
    # loop through the isbns to see whether we get one that is not None
    work = None
    edition = add_all_isbns(isbns, None, language=language, title=title)
    if edition:
        edition.refresh_from_db()
        work = edition.work

    if doab_id and not work:
        # make sure there's not already a doab_id
        idents = models.Identifier.objects.filter(type='doab', value=doab_id)
        for ident in idents:
            edition = ident.work.preferred_edition
            break
    
    if edition is not None:
        # if this is a new edition, then add related editions asynchronously
        if getattr(edition,'new', False):
            tasks.populate_edition.delay(edition.isbn_13)
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
    
    if format in ('pdf', 'epub', 'mobi'):
        ebook = models.Ebook()
        ebook.format = format
        ebook.provider = provider
        ebook.url =  url
        ebook.rights = rights
        # tie the edition to ebook
        ebook.edition = edition
        ebook.save()
    
    # update the cover id (could be done separately)
    cover_url = update_cover_doab(doab_id)
    
    # attach more metadata
    attach_more_doab_metadata(edition, 
                              description=kwargs.get('description'),
                              subjects=kwargs.get('subject'),
                              publication_date=kwargs.get('date'),
                              publisher_name=kwargs.get('publisher'))    
    return ebook


def load_doab_records(fname, limit=None):
    
    success_count = 0
    ebook_count = 0
    
    records = json.load(open(fname))

    for (i, book) in enumerate(islice(records,limit)):
        d = dict(book)
        try:
            ebook = load_doab_edition(**dict(book))
            success_count += 1 
            if ebook:
                ebook_count +=1
        except Exception, e:
            logger.error(e)
            
    logger.info("Number of records processed: " + str(success_count))
    logger.info("Number of ebooks processed: " + str(ebook_count))
        