import logging

import json
from itertools import islice

import regluit
from regluit.core import models
from regluit.core.bookloader import add_by_isbn

logger = logging.getLogger(__name__)

def load_doab_edition(title, doab_id, seed_isbn, url, format, rights,
                      language, isbns,
                      provider='Directory of Open Access Books', **kwargs):
    

    from django.db.models import (Q, F)
    
    from regluit.core import tasks
    from regluit.core import (models, bookloader)
   
    # check to see whether the Edition hasn't already been loaded first
    # search by url
    ebooks = models.Ebook.objects.filter(url=url)
       
    # 1 match
    # > 1 match
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
            doab_identifer = models.Identifier.get_or_add(type='doab',value=doab_id, 
                                               work=work)
            work.save()
        
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
        
    # tie the edition to ebook
    
    ebook.edition = edition
    ebook.save()
    
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
        