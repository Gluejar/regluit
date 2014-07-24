import logging
import json
from itertools import islice

import requests

from django.db.models import (Q, F)

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

import regluit
from regluit.core import models
from regluit.core import bookloader
from regluit.core.bookloader import add_by_isbn

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
    
def attach_more_doab_metadata(ebook, description, subjects,
                              publication_date, publisher_name=None):
    
    """
    for given ebook, attach description, subjects, publication date to
    corresponding Edition and Work
    """
    # if edition doesn't have a publication date, update it
    edition = ebook.edition
    edition_to_save = False
    
    if not edition.publication_date:
        edition.publication_date = publication_date
        edition_to_save = True
    
    # TO DO: insert publisher name properly
    # PublisherName.name is not unique at the moment (contrary to what I thought)
    # if edition.publisher_name is empty, set it
    #if not edition.publisher_name:
    #    edition.publisher_name = models.PublisherName.objects.get_or_create(name=publisher_name)[0]
    #    edition_to_save = True
        
    if edition_to_save:
        edition.save()
        
    # attach description to work if it's not empty
    work = edition.work
    if not work.description:
        work.description = description
        work.save()
        
    # update subjects
    work.subjects.add(*[models.Subject.objects.get_or_create(name=s)[0] for s in subjects])
            
    return ebook

def load_doab_edition(title, doab_id, seed_isbn, url, format, rights,
                      language, isbns,
                      provider, **kwargs):
    
    """
    load a record from doabooks.org represented by input parameters and return an ebook
    """
    from regluit.core import tasks

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
    
    if len(ebooks) > 1:
        raise Exception("There is more than one Ebook matching url {0}".format(url))    
    elif len(ebooks) == 1:  
        ebook = ebooks[0]
        doab_identifer = models.Identifier.get_or_add(type='doab',value=doab_id, 
                                               work=ebook.edition.work)
        # update the cover id 
        cover_url = update_cover_doab(doab_id)
        
        # attach more metadata
        attach_more_doab_metadata(ebook, 
                                  description=kwargs.get('description'),
                                  subjects=kwargs.get('subject'),
                                  publication_date=kwargs.get('date'),
                                  publisher_name=kwargs.get('publisher'))
        
        return ebook
    
    # remaining case --> need to create a new Ebook 
    assert len(ebooks) == 0
            
    # make sure we have isbns to work with before creating ebook
    if len(isbns) == 0:
        return None
    
    ebook = models.Ebook()
    ebook.format = format
    ebook.provider = provider
    ebook.url =  url
    ebook.rights = rights

    # we still need to find the right Edition/Work to tie Ebook to...
    
    # look for the Edition with which to associate ebook.
    # loop through the isbns to see whether we get one that is not None
        
    for isbn in isbns:
        edition = bookloader.add_by_isbn(isbn)
        if edition is not None: break        
    
    if edition is not None:
        # if this is a new edition, then add related editions asynchronously
        if getattr(edition,'new', False):
            tasks.populate_edition.delay(edition.isbn_13)
            
        # QUESTION:  Is this good enough?
        # what's going to happen to edition.work if there's merging   
        doab_identifer = models.Identifier.get_or_add(type='doab',value=doab_id, 
                                work=edition.work)

    # we need to create Edition(s) de novo    
    else: 
        # if there is a Work with doab_id already, attach any new Edition(s)
        try:
            work = models.Identifier.objects.get(type='doab',value=doab_id).work
        except models.Identifier.DoesNotExist:
            work = models.Work(language=language,title=title)
            work.save()
            doab_identifer = models.Identifier.get_or_add(type='doab',value=doab_id, 
                                               work=work)
            
        
        # create Edition(s) for each of the isbn from the input info
        editions = []
        for isbn in isbns:
            edition = models.Edition(title=title, work=work)
            edition.save()
            
            isbn_id = models.Identifier.get_or_add(type='isbn',value=isbn,work=work)
            
            editions.append(edition)
  
        # if work has any ebooks already, attach the ebook to the corresponding edition
        # otherwise pick the first one
        # pick the first edition as the one to tie ebook to 
        editions_with_ebooks = models.Edition.objects.filter(Q(work__id=work.id) & \
                                                      Q(ebooks__isnull=False)).distinct()
        if editions_with_ebooks:
            edition = editions_with_ebooks[0]
        else:
            edition = editions[0]
        
    # make the edition the selected_edition of the work
    work = edition.work
    work.selected_edition = edition
    work.save()
    
    # tie the edition to ebook
    ebook.edition = edition
    ebook.save()
    
    # update the cover id (could be done separately)
    cover_url = update_cover_doab(doab_id)
    
    # attach more metadata
    attach_more_doab_metadata(ebook, 
                              description=kwargs.get('description'),
                              subjects=kwargs.get('subject'),
                              publication_date=kwargs.get('date'),
                              publisher_name=kwargs.get('publisher'))    
    return ebook


def load_doab_records(fname, limit=None, async=True):
    
    from regluit.core import (doab, tasks)
    success_count = 0
    
    records = json.load(open(fname))

    for (i, book) in enumerate(islice(records,limit)):
        d = dict(book)
        if d['format'] == 'pdf':
            try:
                if async:
                    task_id = tasks.load_doab_edition.delay(**dict(book))
                    
                    ct = models.CeleryTask()
                    ct.task_id = task_id
                    ct.function_name = "load_doab_edition"
                    ct.user = None
                    ct.description = "Loading DOAB %s " % (dict(book)['doab_id'])
                    ct.save()
                    
                else:
                    edition = load_doab_edition(**dict(book))
                success_count += 1 
            except Exception, e:
                logger.warning(e)
            
    logger.info("Number of books successfully uploaded: " + str(success_count))
        