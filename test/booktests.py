from regluit.core import librarything, bookloader, models, tasks
from collections import OrderedDict
from itertools import izip, islice
import django

from django.db.models import Q, F
from regluit.core import bookloader
import warnings
import datetime
from regluit.experimental import bookdata
from datetime import datetime
import json

import logging
logger = logging.getLogger(__name__)

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
    not_loaded_books = [b for (b, ed) in izip(books, editions) if ed is None]
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
    
               
def load_penguin_moby_dick():
    seed_isbn = '9780142000083'
    ed = bookloader.add_by_isbn(seed_isbn)
    if ed.new:
        ed = tasks.populate_edition.delay(ed.isbn_13)

def load_gutenberg_moby_dick():
    title = "Moby Dick"
    ol_work_id = "/works/OL102749W"
    gutenberg_etext_id = 2701
    epub_url = "http://www.gutenberg.org/cache/epub/2701/pg2701.epub"
    license = 'http://www.gutenberg.org/license'
    lang = 'en'
    format = 'epub'
    publication_date = datetime(2001,7,1)
    seed_isbn = '9780142000083' # http://www.amazon.com/Moby-Dick-Whale-Penguin-Classics-Deluxe/dp/0142000086
    
    ebook = bookloader.load_gutenberg_edition(title, gutenberg_etext_id, ol_work_id, seed_isbn,
                                              epub_url, format, license, lang, publication_date)
    return ebook

def load_gutenberg_books(fname="/Users/raymondyee/D/Document/Gluejar/Gluejar.github/regluit/experimental/gutenberg/g_seed_isbn.json",
                         max_num=None):
    
    headers = ()
    f = open(fname)
    records = json.load(f)
    f.close()
    
    for (i, record) in enumerate(islice(records,max_num)):
        if record['format'] == 'application/epub+zip':
            record['format'] = 'epub'
        elif record['format'] == 'application/pdf':
            record['format'] = 'pdf'
        if record['seed_isbn'] is not None:
            ebook = bookloader.load_gutenberg_edition(**record)
            logger.info("%d loaded ebook %s %s", i, ebook, record)
        else:
            logger.info("%d null seed_isbn: ebook %s", i, ebook)

def cluster_status(max_num=None):
    """Look at the current Work, Edition instances to figure out what needs to be fixed"""
    results = OrderedDict([
        ('number of Works', models.Work.objects.count()),
        ('number of Works w/o Identifier', models.Work.objects.filter(identifiers__isnull=True).count()),
        ('number of Editions', models.Edition.objects.count()),
        ('number of Editions with ISBN', models.Edition.objects.filter(identifiers__type='isbn').count()),
        ('number of Editions without ISBNs', models.Edition.objects.exclude(identifiers__type='isbn').count()),
        ('number of Edition that have both Google Books id and ISBNs',
             models.Edition.objects.filter(identifiers__type='isbn').filter(identifiers__type='goog').count()),
        ('number of Editions with Google Books IDs but not ISBNs',
             models.Edition.objects.filter(identifiers__type='goog').exclude(identifiers__type='isbn').count()),
        ])
    
    # models.Identifier.objects.filter(type='isbn').values_list('value', 'edition__id', 'edition__work__id', 'edition__work__language').count()
    # 4 classes -- Edition have ISBN or not & ISBN is recognized or not by LT
    # a) ISBN recognized by LT, b) ISBN not recognized by LT, c) no ISBN at all
    
    # [w._meta.get_all_related_objects() for w in works_no_ids] -- try to figure out whether any related objects before deleting
    
    # Are there Edition without ISBNs?  Look up the corresponding ISBNs from Google Books and Are they all singletons?
    
    # identify Editions that should be merged (e.g., if one Edition has a Google Books ID and another Edition has one with
    # an ISBN tied to that Google Books ID)


    from collections import defaultdict
    import shutil
    import time
    from collections import namedtuple
    
    # let's form a key to map all the Editions into
    # (lt_work_id (or None), lang, ISBN (if lt_work_id is None or None if we don't know it), ed_id (or None) )
    
    work_clusters = defaultdict(set)
    current_map = defaultdict(set)
    
    backup = '/Users/raymondyee/D/Document/Gluejar/Gluejar.github/regluit/experimental/lt_data_back.json'
    fname = '/Users/raymondyee/D/Document/Gluejar/Gluejar.github/regluit/experimental/lt_data.json'
    
    EdInfo = namedtuple('EdInfo', ['isbn', 'ed_id', 'ed_title', 'work_id', 'lang'])
    
    shutil.copy(fname, backup)
        
    lt = bookdata.LibraryThing(fname)

    try:
        input_file = open(fname, "r")
        success = lt.load()
        print "success: %s" % (success)
        input_file.close()
    except Exception, e:
        print e
    
    for (i, (isbn, ed_id, ed_title, work_id, lang)) in enumerate(
        islice(models.Identifier.objects.filter(type='isbn').values_list('value', 'edition__id',
                'edition__title', 'edition__work__id', 'edition__work__language'), max_num)):
        
        lt_work_id = lt.thingisbn(isbn, return_work_id=True)
        key = (lt_work_id, lang, isbn if lt_work_id is None else None, None)
        print i, isbn, lt_work_id, key
        work_clusters[key].add(EdInfo(isbn=isbn, ed_id=ed_id, ed_title=ed_title, work_id=work_id, lang=lang))
        current_map[work_id].add(key)
    
    lt.save()
    
    # Now add the Editions without any ISBNs
    print "editions w/o isbn"
    for (i, (ed_id, ed_title, work_id, lang)) in enumerate(
        islice(models.Edition.objects.exclude(identifiers__type='isbn').values_list('id',
                'title', 'work__id', 'work__language'), None)):
        
        key = (None, lang, None, ed_id)
        print i, ed_id, ed_title, key
        work_clusters[key].add(EdInfo(isbn=None, ed_id=ed_id, ed_title=ed_title, work_id=work_id, lang=lang))
        current_map[work_id].add(key)

    print "number of clusters", len(work_clusters)
    
    s = {'work_clusters':work_clusters, 'current_map':current_map, 'results':results}
    
    #
    print "new clusters that map over more than one existing Work", \
    [(k, len(set(([e.work_id for e in v])))) for (k,v) in s['work_clusters'].items() if len(set(([e.work_id for e in v]))) <> 1 ]
    
    m = current_map
    print "existing Works that contain editions from more than 1 new cluster", \
        sorted([k for (k,v) in m.items() if len(v) > 1])
    
    return s

def all_editions():
    pass
    

        
        