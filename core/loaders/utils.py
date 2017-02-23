import csv
import re
import requests
import logging
import sys
import unicodedata

from regluit.core.models import Work, Edition, Author, PublisherName, Identifier, Subject
from regluit.core.isbn import ISBN
from regluit.core.bookloader import add_by_isbn_from_google, merge_works
from regluit.api.crosswalks import inv_relator_contrib
from regluit.bisac.models import BisacHeading

logger = logging.getLogger(__name__)

def UnicodeDictReader(utf8_data, **kwargs):
    csv_reader = csv.DictReader(utf8_data, **kwargs)
    for row in csv_reader:
        yield {key: unicode(value, 'utf-8') for key, value in row.iteritems()}

def utf8_general_ci_norm(s):
    """
    Normalize a la MySQL utf8_general_ci collation
    (As of 2016.05.24, we're using the utf8_general_ci collation for author names)
    
    http://stackoverflow.com/questions/1036454/what-are-the-diffrences-between-utf8-general-ci-and-utf8-unicode-ci/1036459#1036459

    * converts to Unicode normalization form D for canonical decomposition
    * removes any combining characters
    * converts to upper case

    """

    s1 = unicodedata.normalize('NFD', s)
    return ''.join(c for c in s1 if not unicodedata.combining(c)).upper()

def get_authors(book):
    authors=[]
    if book.get('AuthorsList',''):
        #UMich
        for i in range(1,3):
            fname=u'Author{}First'.format(i)
            lname=u'Author{}Last'.format(i)
            role=u'Author{}Role'.format(i)
            authname = u'{} {}'.format(book[fname],book[lname])
            if authname != u' ':
                role = book[role] if book[role].strip() else 'A01'
                authors.append((authname,role))
            else:
                break
        authlist = book["AuthorsList"].replace(' and ', ', ').split(', ')
        if len(authlist)>3:
            for authname in authlist[3:]:
                authors.append((authname, 'A01'))
    else:
        #OBP
        for i in range(1,6):
            fname= book.get(u'Contributor {} first name'.format(i), '')
            lname= book.get(u'Contributor {} surname'.format(i), '')
            role= book.get(u'ONIX Role Code (List 17){}'.format(i), '')
            authname = u'{} {}'.format(fname,lname)
            if authname != u' ':
                role = role if role.strip() else 'A01'
                authors.append((authname,role))
            else:
                break
    return authors

def get_subjects(book):
    subjects=[]
    for i in range(1,5):
        key = u'BISACCode{}'.format(i)  #UMich dialect
        key2 = u'BISAC subject code {}'.format(i) #OBP dialect
        code = book.get(key,'')
        code = code if code else book.get(key2,'')
        if code != '':
            try:
                bisac=BisacHeading.objects.get(notation=code)
                subjects.append(bisac)
            except BisacHeading.DoesNotExist:
                logger.warning( "Please add BISAC {}".format(code))
    return subjects

def add_subject(subject_name, work, authority=''):
    try:
        subject= Subject.objects.get(name=subject_name)
    except Subject.DoesNotExist:
        subject=Subject.objects.create(name=subject_name, authority=authority)
    subject.works.add(work)

def get_title(book):
    title = book.get('FullTitle','') #UMICH
    if title:
        return title
    title = book.get('Title','') #OBP
    sub = book.get('Subtitle','')
    if sub:
        return u'{}: {}'.format(title,sub)
    else:
        return title
        
def get_cover(book):
    cover_url =  book.get('Cover URL','') #OBP
    if cover_url:
        return cover_url
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
    #'ISBN 1' is OBP, others are UMICH
    for code in ['eISBN', 'ISBN 3','PaperISBN', 'ISBN 2', 'ClothISBN', 'ISBN 1', 'ISBN 4', 'ISBN 5']:
        if book.get(code, '') not in ('','N/A'):
            values = book[code].split(',')
            for value in values:
                isbn = ISBN(value).to_string()
                if isbn:
                    isbns.append(isbn)
    for isbn in isbns :
        if not edition:
            edition = Edition.get_by_isbn(isbn)
    return (isbns, edition )

def get_pubdate(book):
    value = book.get('CopyrightYear','') #UMICH
    if value:
        return value
    value = book.get('publication year','') #OBP
    sub = book.get('publication month','')
    sub2 = book.get('publication day','')
    if sub2:
        return u'{}-{}-{}'.format(value,sub,sub2)
    elif sub:
        return u'{}-{}'.format(value,sub,sub2)
    else:
        return value
        
def get_publisher(book):
    value = book.get('Publisher','')
    if value:
        return value
    if book.get('DOI prefix','')=='10.11647':
        return "Open Book Publishers"
        
def get_url(book):
    url = book.get('URL','')
    url = url if url else u'https://doi.org/{}/{}'.format( book.get('DOI prefix',''),book.get('DOI suffix',''))
    return url

def get_description(book):
    value = book.get('DescriptionBrief','')
    value = value if value else book.get('Plain Text Blurb','')
    return value

def get_language(book):
    value = book.get('ISO Language Code','')
    return value

        
def load_from_books(books):
    ''' books is an iterator of book dicts.
        each book must have attributes
        (umich dialect)
        eISBN, ClothISBN, PaperISBN, Publisher, FullTitle, Title, Subtitle, AuthorsList, 
        Author1Last, Author1First, Author1Role, Author2Last, Author2First, Author2Role, Author3Last, 
        Author3First, Author3Role, AuthorBio, TableOfContents, Excerpt, DescriptionLong, 
        DescriptionBrief, BISACCode1, BISACCode2, BISACCode3, CopyrightYear, ePublicationDate, 
        eListPrice, ListPriceCurrencyType, List Price in USD (paper ISBN), eTerritoryRights, 
        SubjectListMARC, , Book-level DOI, URL,	License
        
        '''

    # Goal: get or create an Edition and Work for each given book

    results = []

    for (i, book) in enumerate(books):

        # try first to get an Edition already in DB with by one of the ISBNs in book
        (isbns, edition) = get_isbns(book)
        if len(isbns)==0:
            continue
        title=get_title(book)
        authors = get_authors(book)

        # if matching by ISBN doesn't work, then create a Work and Edition 
        # with a title and the first ISBN
        if not edition:
            work = Work(title=title)
            work.save()
            edition= Edition(title=title, work=work) 
            edition.save()
            Identifier.set(type='isbn', value=isbns[0], edition=edition, work=work)

        work=edition.work

        # at this point, work and edition exist
        url = get_url(book)
        if url:
            Identifier.set(type='http', value=url, edition=edition, work=work)

        # make sure each isbn is represented by an Edition
        # also associate authors, publication date, cover, publisher
        for isbn in isbns:
            edition = add_by_isbn_from_google(isbn, work=work)
            if edition and edition.work != work:
                merge_works(work, edition.work)
                work = work if work.pk is not None else edition.work
                edition.work=work # because integrity errors if not
            if not edition:
                edition= Edition(title=title, work=work)
                edition.save()
                Identifier.set(type='isbn', value=isbn, edition=edition, work=work)

            edition.authors.clear()
            for (author, role) in authors:
                edition.add_author(author, inv_relator_contrib.get(role, 'aut'))
            edition.publication_date = get_pubdate(book)
            edition.cover_image = get_cover(book)
            edition.save()
            edition.set_publisher(get_publisher(book))

        # possibly replace work.description 
        description = get_description(book)
        if len(description)>len (work.description):
            work.description = description
            work.save()
        
        # set language
        lang= get_language(book)
        if lang:
            work.language = lang
            work.save()
        
        # add a bisac subject (and ancestors) to work
        for bisacsh in get_subjects(book):
            while bisacsh:
                add_subject(bisacsh.full_label, work, authority="bisacsh")
                bisacsh = bisacsh.parent

        logging.info(u'loaded work {}'.format(work.title))
        loading_ok = loaded_book_ok(book, work, edition)

        results.append((book, work, edition))

        try:
            logger.info (u"{} {} {}\n".format(i, title, loading_ok))
        except Exception as e:
            logger.info (u"{} {}\n".format(i, title, str(e) ))

    return results

    
def loaded_book_ok(book, work, edition):

    isbns = get_isbns(book)[0]
    authors = get_authors(book)
    subjects = get_subjects(book)

    if (work is None) or (edition is None):
        return False

    try:
        url_id = Identifier.objects.get(type='http', value=get_url(book))
        if url_id is None:
            logger.info ("url_id problem: work.id {}, url: {}".format(work.id, get_url(book)))
            return False
    except Exception as e:
        logger.info (str(e))
        return False

    # isbns
    for isbn in isbns:
        if Identifier.objects.filter(type='isbn', value=isbn).count() <> 1:
            # print ("isbn problem: work.id {}, isbn: {}".format(work.id, isbn))
            return False
        else:
            try:
                edition_for_isbn = Identifier.objects.get(type='isbn', value=isbn).edition
            except Exception as e:
                print (e)
                return False

            # authors
            # print set([ed.name for ed in edition_for_isbn.authors.all()])

            if (set([utf8_general_ci_norm(author[0]) for author in authors]) != 
                   set([utf8_general_ci_norm(ed.name) for ed in edition_for_isbn.authors.all()])):
                print "problem with authors"
                return False

            try:
                edition_for_isbn.publication_date = get_pubdate(book)
                edition_for_isbn.cover_image = get_cover(book)
                edition_for_isbn.set_publisher(get_publisher(book))
            except:
                return False

    # work description
    description = get_description(book)
    if not ((work.description == description) or (len(description) <len (work.description))):
        return False

    # bisac

    for bisacsh in subjects:
        while bisacsh:
            try:
                subject = Subject.objects.get(name=bisacsh.full_label)
            except:
                return False
            if subject not in work.subjects.all():
                return False
            bisacsh = bisacsh.parent


    return True