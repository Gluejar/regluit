import csv
import re
import requests
import logging

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

def add_subject(subject_name,work, authority=''):
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


def load_from_books(books):
    ''' books is an iterator of book dicts.
        each book mus have attributes
        eISBN, ClothISBN, PaperISBN, Publisher, FullTitle, Title, Subtitle, AuthorsList, 
        Author1Last, Author1First, Author1Role, Author2Last, Author2First, Author2Role, Author3Last, 
        Author3First, Author3Role, AuthorBio, TableOfContents, Excerpt, DescriptionLong, 
        DescriptionBrief, BISACCode1, BISACCode2, BISACCode3, CopyrightYear, ePublicationDate, 
        eListPrice, ListPriceCurrencyType, List Price in USD (paper ISBN), eTerritoryRights, 
        SubjectListMARC, , Book-level DOI, URL,	License
        '''

    for book in books:
        (isbns, edition) = get_isbns(book)
        title=book['FullTitle']
        authors = get_authors(book)
        if not edition and len(isbns):
            work = Work(title=title)
            work.save()
            edition= Edition(title=title, work=work) 
            edition.save()
            Identifier.set(type='isbn', value=isbns[0], edition=edition, work=work)
        work=edition.work
        Identifier.set(type='http', value=book['URL'], edition=edition, work=work)
        for isbn in isbns:
            edition= add_by_isbn_from_google(isbn)
            if not edition:
                edition= Edition(title=title, work=work)
                edition.save()
                Identifier.set(type='isbn', value=isbn, edition=edition, work=work)
            edition.authors.clear()
            for (author,role) in authors:
                edition.add_author(author, inv_relator_contrib.get(role, 'aut'))
            edition.publication_date = book['CopyrightYear']
            edition.cover_image = get_cover(book)
            edition.set_publisher(book['Publisher'])
            edition.save()
        description = book['DescriptionBrief']
        if len(description)>len (work.description):
            work.description = description
        for bisacsh in get_subjects(book):
            while bisacsh:
                add_subject(bisacsh.full_label, work, authority="bisacsh")
                bisacsh = bisacsh.parent
        logging.info(u'loaded work {}'.format(work.title))
