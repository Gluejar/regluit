import csv
import re
import requests
import logging
import sys

from regluit.core.models import Work, Edition, Author, PublisherName, Identifier, Subject
from regluit.core.isbn import ISBN
from regluit.core.bookloader import add_by_isbn_from_google
from regluit.api.crosswalks import inv_relator_contrib
from regluit.bisac.models import BisacHeading

logger = logging.getLogger(__name__)

def UnicodeDictReader(utf8_data, **kwargs):
    csv_reader = csv.DictReader(utf8_data, **kwargs)
    for row in csv_reader:
        yield {key: unicode(value, 'utf-8') for key, value in row.iteritems()}

def get_authors(book):
    authors=[]
    for i in range(1,3):
        fname=u'Author{}First'.format(i)
        lname=u'Author{}Last'.format(i)
        role=u'Author{}Role'.format(i)
        authname = u'{} {}'.format(book[fname].encode('utf-8'),book[lname])
        if authname != u' ':
            role = book[role] if book[role]!= u' ' else 'A01'
            authors.append((authname,role))
        else:
            break
    authlist = book["AuthorsList"].replace(' and ', ', ').split(', ')
    if len(authlist)>3:
        for authname in authlist[3:]:
            authors.append((authname, 'A01'))
    return authors

def get_subjects(book):
    subjects=[]
    for i in range(1,3):
        key=u'BISACCode{}'.format(i)
        if book[key] != '':
            try:
                bisac=BisacHeading.objects.get(notation=book[key])
                subjects.append(bisac)
            except BisacHeading.DoesNotExist:
                logger.warning( "Please add BISAC {}".format(book[key]))
    return subjects

def add_subject(subject_name, work, authority=''):
    try:
        subject= Subject.objects.get(name=subject_name)
    except Subject.DoesNotExist:
        subject=Subject.objects.create(name=subject_name, authority=authority)
    subject.works.add(work)

def get_cover(book):
    url = book['URL']
    if "10.3998" in url:
        # code for umich books; can generalize, of course!
        idmatch= re.search( r'([^/]+)\.(\d+\.\d+\.\d+)', url)
        if idmatch:
            book_id = idmatch.group(2)
            if idmatch.group(1) == 'ohp':
                cover_url = "http://quod.lib.umich.edu/o/ohp/images/{}.jpg".format(book_id)
            elif idmatch.group(1) == 'ump':
                cover_url = "http://quod.lib.umich.edu/u/ump/images/{}.jpg".format(book_id)
            else:
                cover_url = "http://quod.lib.umich.edu/d/dculture/images/{}.jpg".format(book_id)
            cover = requests.head(cover_url)
            if cover.status_code<400:
                return cover_url
            else:
                logger.warning( "bad cover: {} for: {}".format(cover_url, url))
            
def get_isbns(book):
    isbns = []
    edition = None
    for code in ['eISBN','PaperISBN','ClothISBN']:
        if book[code] not in ('','N/A'):
            values = book[code].split(',')
            for value in values:
                isbn = ISBN(value).to_string()
                if isbn:
                    isbns.append(isbn)
    for isbn in isbns :
        if not edition:
            edition = Edition.get_by_isbn(isbn)
    return (isbns, edition )


def _out(*args, **kwargs):

    sys.stdout.write(*args, **kwargs)
    sys.stdout.flush()

def load_from_books(books):
    ''' books is an iterator of book dicts.
        each book must have attributes
        eISBN, ClothISBN, PaperISBN, Publisher, FullTitle, Title, Subtitle, AuthorsList, 
        Author1Last, Author1First, Author1Role, Author2Last, Author2First, Author2Role, Author3Last, 
        Author3First, Author3Role, AuthorBio, TableOfContents, Excerpt, DescriptionLong, 
        DescriptionBrief, BISACCode1, BISACCode2, BISACCode3, CopyrightYear, ePublicationDate, 
        eListPrice, ListPriceCurrencyType, List Price in USD (paper ISBN), eTerritoryRights, 
        SubjectListMARC, , Book-level DOI, URL,	License
        '''

    # Goal: get or create an Edition and Work for each given book

    for (i, book) in enumerate(books):

        # try first to get an Edition already in DB with by one of the ISBNs in book
        (isbns, edition) = get_isbns(book)
        title=book['FullTitle']
        authors = get_authors(book)

        # if matching by ISBN doesn't work, then create a Work and Edition 
        # with a title and the first ISBN
        if not edition and len(isbns):
            work = Work(title=title)
            work.save()
            edition= Edition(title=title, work=work) 
            edition.save()
            Identifier.set(type='isbn', value=isbns[0], edition=edition, work=work)

        work=edition.work

        # at this point, work and edition exist

        if book.get('URL'):
            Identifier.set(type='http', value=book['URL'], edition=edition, work=work)

        # make sure each isbn is represented by an Edition
        # also associate authors, publication date, cover, publisher
        for isbn in isbns:
            edition = add_by_isbn_from_google(isbn)
            if not edition:
                edition= Edition(title=title, work=work)
                edition.save()
                Identifier.set(type='isbn', value=isbn, edition=edition, work=work)

            if isbn == '9780472116713':
                print ('for 9780472116713, edition_id is {}'.format(edition.id))

            edition.authors.clear()
            for (author, role) in authors:
                edition.add_author(author, inv_relator_contrib.get(role, 'aut'))
            edition.publication_date = book['CopyrightYear']
            edition.cover_image = get_cover(book)
            edition.set_publisher(book['Publisher'])
            edition.save()

        # possibly replace work.description 
        description = book['DescriptionBrief']
        if len(description)>len (work.description):
            work.description = description

        # add a bisac subject (and ancestors) to work
        for bisacsh in get_subjects(book):
            while bisacsh:
                add_subject(bisacsh.full_label, work, authority="bisacsh")
                bisacsh = bisacsh.parent

        logging.info(u'loaded work {}'.format(work.title))
        loading_ok = loaded_book_ok(book, work, edition)
        try:
            _out("{} {} {}\n".format(i, title, loading_ok))
        except Exception as e:
            _out("{} {}\n".format(i, title, str(e) ))
    

def loaded_book_ok(book, work, edition):

    isbns = get_isbns(book)[0]

    if (work is None) or (edition is None):
        return False

    try:
        url_id = Identifier.objects.get(type='http', value=book['URL'])
        if url_id is None:
            print ("url_id problem: work.id {}, url: {}".format(work.id, book['URL']))
            return False
    except Exception as e:
        _out(str(e))
        return False
        
    # isbns 
    # looking at work_isbns too narrow
    # work_isbns = set([isbn.value for isbn in Identifier.objects.filter(type='isbn', work=work)])
    # if not (set(isbns) <= work_isbns):
    #     print ("isbn problem: work.id {}, work_isbns: {} isbns: {}".format(work.id, work_isbns, isbns))
    #     return False

    # isbns
    for isbn in isbns:
        if Identifier.objects.filter(type='isbn', value=isbn).count() <> 1:
            print ("isbn problem: work.id {}, isbn: {}".format(work.id, isbn))
            return False

    return True
