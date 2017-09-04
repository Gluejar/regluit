#!/usr/bin/env python
# encoding: utf-8
import logging
import json
import re

from itertools import islice

import requests

from django.db.models import (Q, F)

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

import regluit
from regluit.core import models, tasks
from regluit.core import bookloader
from regluit.core.bookloader import add_by_isbn, merge_works
from regluit.core.isbn import ISBN

logger = logging.getLogger(__name__)

springercover = re.compile(r'ftp.+springer\.de.+(\d{13}\.jpg)$', flags=re.U)

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
        r = requests.get(url, allow_redirects=False) # requests doesn't handle ftp redirects.
        if r.status_code == 302:
            redirurl = r.headers['Location']
            if redirurl.startswith(u'ftp'):
                springerftp = springercover.match(redirurl)
                if springerftp:
                    redirurl = u'https://images.springer.com/sgw/books/medium/{}.jpg'.format(springerftp.groups(1))
                    r = requests.get(redirurl)
        else:
            r = requests.get(url)    
        cover_file = ContentFile(r.content)
        cover_file.content_type = r.headers.get('content-type', '')

        path = default_storage.save(cover_file_name, cover_file)    
        return (default_storage.url(cover_file_name), True)
    except Exception, e:
        # if there is a problem, return None for cover URL
        logger.warning('Failed to make cover image for doab_id={}: {}'.format(doab_id, e))
        return (None, False)

def update_cover_doab(doab_id, edition, store_cover=True):
    """
    update the cover url for work with doab_id
    if store_cover is True, use the cover from our own storage
    """
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
        if bookloader.valid_subject(s):
            work.subjects.add(models.Subject.objects.get_or_create(name=s)[0])
    
    # set reading level of work if it's empty; doab is for adults.
    if not work.age_level:
        work.age_level = '18-'
        
    if language:
        work.language = language
    work.save()
    
    if authors and authors == authors: # test for authors != NaN
        authlist = creator_list(authors)
        if edition.authors.all().count() < len(authlist):
            edition.authors.clear()
            if authlist is not None:
                for [rel,auth] in authlist:
                    edition.add_author(auth, rel)
               
    return edition

def add_all_isbns(isbns, work, language=None, title=None):
    first_edition = None
    for isbn in isbns:
        first_edition = None
        edition = bookloader.add_by_isbn(isbn, work, language=language, title=title)
        if edition:
            first_edition = first_edition if first_edition else edition 
            if work and (edition.work.id != work.id): 
                if work.created < edition.work.created:
                    work = merge_works(work, edition.work)
                else:
                    work = merge_works(edition.work, work)
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
        cover_url = update_cover_doab(doab_id, ebook.edition)
        
        # attach more metadata
        attach_more_doab_metadata(ebook.edition, 
                                  description=kwargs.get('description'),
                                  subjects=kwargs.get('subject'),
                                  publication_date=kwargs.get('date'),
                                  publisher_name=kwargs.get('publisher'),
                                  language=language,
                                  authors=kwargs.get('authors'),)
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
            work = edition.work
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
    cover_url = update_cover_doab(doab_id, edition)
    
    # attach more metadata
    attach_more_doab_metadata(edition, 
                              description=kwargs.get('description'),
                              subjects=kwargs.get('subject'),
                              publication_date=kwargs.get('date'),
                              publisher_name=kwargs.get('publisher'),
                              authors=kwargs.get('authors'),)    
    return ebook


def load_doab_records(fname, limit=None):
    
    success_count = 0
    ebook_count = 0
    
    records = json.load(open(fname))

    for (i, book) in enumerate(islice(records,limit)):
        d = dict(book)
        d['isbns'] = split_isbns(d['isbns_raw']) # use stricter isbn string parsing.
        try:
            ebook = load_doab_edition(**d)
            success_count += 1 
            if ebook:
                ebook_count +=1
        except Exception, e:
            logger.error(e)
            logger.error(book)
            
    logger.info("Number of records processed: " + str(success_count))
    logger.info("Number of ebooks processed: " + str(ebook_count))

"""
#tools to parse the author lists in doab.csv
from pandas import DataFrame
url = "http://www.doabooks.org/doab?func=csv"
df_csv = DataFrame.from_csv(url)

out=[]
for val in df_csv.values:
    isbn = split_isbns(val[0])
    if isbn:
        auths = []
        if val[2] == val[2] and val[-2] == val[-2]: # test for NaN auths and licenses
            auths = creator_list(val[2])
            out.append(( isbn[0], auths))
open("/Users/eric/doab_auths.json","w+").write(json.dumps(out,indent=2, separators=(',', ': ')))
"""
    
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
        return u'{} {}'.format(parts[1].strip(),parts[0].strip())
    else:
        if parts[1].strip() in ('der','van', 'von', 'de', 'ter'):
            return u'{} {} {}'.format(parts[2].strip(),parts[1].strip(),parts[0].strip())
        #print auth
        #print re.search(namelist,auth).group(0)
        return u'{} {}, {}'.format(parts[2].strip(),parts[0].strip(),parts[1].strip())
    

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

def split_auths(auths):
    if ';' in auths or '/' in auths:
        return namesep2.split(auths)
    else:
        nl = namelist.match(auths.strip())
        if nl:
            if nl.group(3).endswith(' de') \
                or ' de ' in nl.group(3) \
                or nl.group(3).endswith(' da') \
                or nl.group(1).endswith(' Jr.') \
                or ' e ' in nl.group(1):
                return [auths]
            else:
                return namesep.split(auths)
        else :
            return [auths]

def split_isbns(isbns):
    result = []
    for isbn in isbnsep.split(isbns):
        isbn = ISBN(isbn)
        if isbn.valid:
            result.append(isbn.to_string())
    return result

def creator_list(creators):
    auths = []
    if re.search(edlist, creators):
        for auth in split_auths(edlist.sub(u'', creators)):
            if auth:
                auths.append(creator(auth, editor=True))
    else:
        for auth in split_auths(unicode(creators)):
            if auth:
                auths.append(creator(auth))
    return auths

def load_doab_auths(fname, limit=None):
    doab_auths = json.load(open(fname))
    recnum = 0
    failed = 0
    for [isbnraw, authlist] in doab_auths:
        isbn = ISBN(isbnraw).to_string()
        try:
            work = models.Identifier.objects.get(type='isbn',value=isbn).work
        except models.Identifier.DoesNotExist:
            print 'isbn = {} not found'.format(isbnraw)
            failed += 1
        if work.preferred_edition.authors.all().count() < len(authlist):
            work.preferred_edition.authors.clear()
            if authlist is None:
                print "null authlist; isbn={}".format(isbn)
                continue
            for [rel,auth] in authlist:
                work.preferred_edition.add_author(auth, rel)
        recnum +=1
        if limit and recnum > limit:
            break          
    logger.info("Number of records processed: " + str(recnum))
    logger.info("Number of missing isbns: " + str(failed))
        