import logging

import json
from itertools import islice

import regluit
from regluit.core import models
from regluit.core.bookloader import add_by_isbn

logger = logging.getLogger(__name__)

def load_doab_edition(title, doab_id, seed_isbn, url, format, rights, 
                      provider='Directory of Open Access Books'):
    
    # can we find doab_id as an identifier? 
    # doab work or edition id
    
    from regluit.core import tasks
    
    try:
        work = models.Identifier.objects.get(type='doab',value=doab_id).work
    except models.Identifier.DoesNotExist: # try to find an Edition with the seed_isbn and use that work to hang off of
        sister_edition = add_by_isbn(seed_isbn)
        if sister_edition.new:
            # add related editions asynchronously
            tasks.populate_edition.delay(sister_edition.isbn_13)
        work = sister_edition.work
        # attach the olwk identifier to this work if it's not none.
        if doab_id is not None:
            work_id = models.Identifier.get_or_add(type='doab',value=doab_id, 
                                                   work=work,
                                                   edition=sister_edition)

    # Now pull out any existing DOAB editions tied to the work with the proper DOAB ID
    try:
        edition = models.Identifier.objects.get( type='doab', value=doab_id).edition    
    except models.Identifier.DoesNotExist:
        edition = models.Edition()
        edition.title = title
        edition.work = work
        
        edition.save()
        edition_id = models.Identifier.get_or_add(type='doab',value=doab_id, 
                                                  edition=edition, work=work)
        
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
    ebook.provider = provider
    ebook.url =  url
    ebook.rights = rights
        
    # is an Ebook instantiable without a corresponding Edition? (No, I think)
    
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
        