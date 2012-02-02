from regluit.core import librarything, bookloader, models, tasks
import itertools
import django

from django.db.models import Q, F
from regluit.core import bookloader
import warnings
import datetime

def ry_lt_books():
    """return parsing of rdhyee's LibraryThing collection"""
    lt = librarything.LibraryThing('rdhyee')
    books = lt.parse_user_catalog(view_style=5)
    return books

def editions_for_lt(books):
    """return the Editions that correspond to the list of LibraryThing books"""
    editions = [bookloader.add_by_isbn(b["isbn"]) for b in books]
    return editions

def ry_lt_not_loaded():
    """Calculate which of the books on rdhyee's librarything list don't yield Editions"""
    books = list(ry_lt_books())
    editions = editions_for_lt(books)
    not_loaded_books = [b for (b, ed) in itertools.izip(books, editions) if ed is None]
    return not_loaded_books

def ry_wish_list_equal_loadable_lt_books():
    """returnwhether the set of works in the user's wishlist is the same as the works in a user's loadable editions from LT"""
    editions = editions_for_lt(ry_lt_books())
    # assume only one user -- and that we have run a LT book loading process for that user
    ry = django.contrib.auth.models.User.objects.all()[0]
    return set([ed.work for ed in filter(None, editions)]) == set(ry.wishlist.works.all())

def clear_works_editions_ebooks():
    models.Ebook.objects.all().delete()
    models.Work.objects.all().delete()
    models.Edition.objects.all().delete()
    
def load_gutenberg_edition(title, gutenberg_etext_id, ol_work_id, seed_isbn, url, format, license, lang, publication_date):
    
    # let's start with instantiating the relevant Work and Edition if they don't already exist
    
    try:
        work = models.Identifier.objects.get(type='olwk',value=ol_work_id).work
    except models.Identifier.DoesNotExist: # try to find an Edition with the seed_isbn and use that work to hang off of
        sister_edition = bookloader.add_by_isbn(seed_isbn)
        if sister_edition.new:
            # add related editions asynchronously
            tasks.populate_edition.delay(sister_edition)
        work = sister_edition.work
        # attach the olwk identifier to this work
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
               
def load_penguin_moby_dick():
    seed_isbn = '9780142000083'
    ed = bookloader.add_by_isbn(seed_isbn)
    if ed.new:
        ed = tasks.populate_edition.delay(ed)

def load_moby_dick():
    """Let's try this out for Moby Dick"""
    
    title = "Moby Dick"
    ol_work_id = "/works/OL102749W"
    gutenberg_etext_id = 2701
    epub_url = "http://www.gutenberg.org/cache/epub/2701/pg2701.epub"
    license = 'http://www.gutenberg.org/license'
    lang = 'en'
    format = 'epub'
    publication_date = datetime.datetime(2001,7,1)
    seed_isbn = '9780142000083' # http://www.amazon.com/Moby-Dick-Whale-Penguin-Classics-Deluxe/dp/0142000086
    
    ebook = load_gutenberg_edition(title, gutenberg_etext_id, ol_work_id, seed_isbn, epub_url, format, license, lang, publication_date)
    return ebook
            