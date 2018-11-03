import csv
import logging
import re
import time
import unicodedata
import urlparse

from bs4 import BeautifulSoup
import requests

from django.conf import settings
from django.core.files.base import ContentFile

from regluit.api.crosswalks import inv_relator_contrib
from regluit.bisac.models import BisacHeading
from regluit.core.bookloader import add_by_isbn_from_google, merge_works
from regluit.core.isbn import ISBN
from regluit.core.models import (
    Ebook, EbookFile, Edition, Identifier, path_for_file, Subject, Work,
)

logger = logging.getLogger(__name__)

def UnicodeDictReader(utf8_data, **kwargs):
    csv_reader = csv.DictReader(utf8_data, **kwargs)
    for row in csv_reader:
        yield {key: unicode(value, 'utf-8') for key, value in row.iteritems()}

def utf8_general_ci_norm(s):
    """
    Normalize a la MySQL utf8_general_ci collation
    (As of 2016.05.24, we're using the utf8_general_ci collation for author names)

    https://stackoverflow.com/questions/1036454/what-are-the-diffrences-between-utf8-general-ci-and-utf8-unicode-ci/1036459#1036459

    * converts to Unicode normalization form D for canonical decomposition
    * removes any combining characters
    * converts to upper case

    """

    s1 = unicodedata.normalize('NFD', s)
    return ''.join(c for c in s1 if not unicodedata.combining(c)).upper()

def get_soup(url):
    response = requests.get(url, headers={"User-Agent": settings.USER_AGENT})
    if response.status_code == 200:
        return BeautifulSoup(response.content, 'lxml')
    return None

def get_authors(book):
    authors = []
    if book.get('AuthorsList', ''):
        #UMich
        for i in range(1, 3):
            fname = u'Author{}First'.format(i)
            lname = u'Author{}Last'.format(i)
            role = u'Author{}Role'.format(i)
            authname = u'{} {}'.format(book[fname], book[lname])
            if authname != u' ':
                role = book[role] if book[role].strip() else 'A01'
                authors.append((authname, role))
            else:
                break
        authlist = book["AuthorsList"].replace(' and ', ', ').split(', ')
        if len(authlist) > 3:
            for authname in authlist[3:]:
                authors.append((authname, 'A01'))
    else:
        #OBP
        for i in range(1, 6):
            fname = book.get(u'Contributor {} first name'.format(i), '')
            lname = book.get(u'Contributor {} surname'.format(i), '')
            role = book.get(u'ONIX Role Code (List 17){}'.format(i), '')
            authname = u'{} {}'.format(fname, lname)
            if authname != u' ':
                role = role if role.strip() else 'A01'
                authors.append((authname, role))
            else:
                break
    return authors

def get_subjects(book):
    subjects = []
    for i in range(1, 5):
        key = u'BISACCode{}'.format(i)  #UMich dialect
        key2 = u'BISAC subject code {}'.format(i) #OBP dialect
        code = book.get(key, '')
        code = code if code else book.get(key2, '')
        if code != '':
            try:
                bisac = BisacHeading.objects.get(notation=code)
                subjects.append(bisac)
            except BisacHeading.DoesNotExist:
                logger.warning("Please add BISAC {}".format(code))
    return subjects

def add_subject(subject_name, work, authority=''):
    try:
        subject = Subject.objects.get(name=subject_name)
    except Subject.DoesNotExist:
        subject = Subject.objects.create(name=subject_name, authority=authority)
    subject.works.add(work)

def get_title(book):
    title = book.get('FullTitle', '') #UMICH
    if title:
        return title
    title = book.get('Title', '') #OBP
    sub = book.get('Subtitle', '')
    if sub:
        return u'{}: {}'.format(title, sub)
    return title

def get_cover(book):
    cover_url = book.get('Cover URL', '') #OBP
    if cover_url:
        return cover_url
    url = book['URL']
    if "10.3998" in url:
        # code for umich books; can generalize, of course!
        idmatch = re.search(r'([^/]+)\.(\d+\.\d+\.\d+)', url)
        if idmatch:
            book_id = idmatch.group(2)
            if idmatch.group(1) == 'ohp':
                cover_url = "http://quod.lib.umich.edu/o/ohp/images/{}.jpg".format(book_id)
            elif idmatch.group(1) == 'ump':
                cover_url = "http://quod.lib.umich.edu/u/ump/images/{}.jpg".format(book_id)
            else:
                cover_url = "http://quod.lib.umich.edu/d/dculture/images/{}.jpg".format(book_id)
            cover = requests.head(cover_url)
            if cover.status_code < 400:
                return cover_url
            else:
                logger.warning("bad cover: {} for: {}".format(cover_url, url))

def get_isbns(book):
    isbns = []
    edition = None
    #'ISBN 1' is OBP, others are UMICH
    for code in ['eISBN', 'ISBN 3', 'PaperISBN', 'ISBN 2', 'ClothISBN',
                 'ISBN 1', 'ISBN 4', 'ISBN 5'
                ]:
        if book.get(code, '') not in ('', 'N/A'):
            values = book[code].split(',')
            for value in values:
                isbn = ISBN(value).to_string()
                if isbn:
                    isbns.append(isbn)
    for isbn in isbns:
        if not edition:
            edition = Edition.get_by_isbn(isbn)
    return (isbns, edition)

def get_pubdate(book):
    value = book.get('CopyrightYear', '') #UMICH
    if value:
        return value
    value = book.get('publication year', '') #OBP
    sub = book.get('publication month', '')
    sub2 = book.get('publication day', '')
    if sub2:
        return u'{}-{}-{}'.format(value, sub, sub2)
    elif sub:
        return u'{}-{}'.format(value, sub, sub2)
    return value

def get_publisher(book):
    value = book.get('Publisher', '')
    if value:
        return value
    if book.get('DOI prefix', '') == '10.11647':
        return "Open Book Publishers"

def get_url(book):
    url = book.get('URL', '')
    url = url if url else u'https://doi.org/{}/{}'.format(
        book.get('DOI prefix', ''),
        book.get('DOI suffix', '')
    )
    return url

def get_description(book):
    value = book.get('DescriptionBrief', '')
    value = value if value else book.get('Plain Text Blurb', '')
    return value

def get_language(book):
    value = book.get('ISO Language Code', '')
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
        if not isbns:
            continue
        title = get_title(book)
        authors = get_authors(book)

        # if matching by ISBN doesn't work, then create a Work and Edition
        # with a title and the first ISBN
        if not edition:
            work = Work(title=title)
            work.save()
            edition = Edition(title=title, work=work)
            edition.save()
            Identifier.set(type='isbn', value=isbns[0], edition=edition, work=work)

        work = edition.work

        # at this point, work and edition exist
        url = get_url(book)
        if url:
            Identifier.set(type='http', value=url, edition=edition, work=work)

        # make sure each isbn is represented by an Edition
        # also associate authors, publication date, cover, publisher
        for isbn in isbns:
            edition = add_by_isbn_from_google(isbn, work=work)
            if edition and edition.work != work:
                work = merge_works(work, edition.work)
            if not edition:
                edition = Edition(title=title, work=work)
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
        if len(description) > len(work.description):
            work.description = description
            work.save()

        # set language
        lang = get_language(book)
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
            logger.info(u"{} {} {}\n".format(i, title, loading_ok))
        except Exception as e:
            logger.info(u"{} {} {}\n".format(i, title, str(e)))

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
            logger.info("url_id problem: work.id {}, url: {}".format(work.id, get_url(book)))
            return False
    except Exception as e:
        logger.info(str(e))
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
                logger.info(e)
                return False

            # authors
            # print set([ed.name for ed in edition_for_isbn.authors.all()])

            if (
                    set([utf8_general_ci_norm(author[0]) for author in authors]) !=
                    set([utf8_general_ci_norm(ed.name) for ed in edition_for_isbn.authors.all()])
            ):
                logger.info("problem with authors")
                return False

            try:
                edition_for_isbn.publication_date = get_pubdate(book)
                edition_for_isbn.cover_image = get_cover(book)
                edition_for_isbn.set_publisher(get_publisher(book))
            except:
                return False

    # work description
    description = get_description(book)
    if not ((work.description == description) or (len(description) < len(work.description))):
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

ID_URLPATTERNS = {
    'goog': re.compile(r'[\./]google\.com/books\?.*id=(?P<id>[a-zA-Z0-9\-_]{12})'),
    'olwk': re.compile(r'[\./]openlibrary\.org(?P<id>/works/OL\d{1,8}W)'),
    'doab': re.compile(r'([\./]doabooks\.org/doab\?.*rid:|=oai:doab-books:)(?P<id>\d{1,8})'),
    'gdrd': re.compile(r'[\./]goodreads\.com/book/show/(?P<id>\d{1,8})'),
    'ltwk': re.compile(r'[\./]librarything\.com/work/(?P<id>\d{1,8})'),
    'oclc': re.compile(r'\.worldcat\.org/.*oclc/(?P<id>\d{8,12})'),
    'doi': re.compile(r'[\./]doi\.org/(?P<id>10\.\d+/\S+)'),
    'gtbg': re.compile(r'[\./]gutenberg\.org/ebooks/(?P<id>\d{1,6})'),
    'glue': re.compile(r'[\./]unglue\.it/work/(?P<id>\d{1,7})'),
    'oapn': re.compile(r'[\./]oapen\.org/download\?.*docid=(?P<id>\d{1,8})'),
}

def ids_from_urls(url):
    ids = {}
    for ident in ID_URLPATTERNS.keys():
        id_match = ID_URLPATTERNS[ident].search(url)
        if id_match:
            ids[ident] = id_match.group('id')
    return ids

DROPBOX_DL = re.compile(r'"(https://dl.dropboxusercontent.com/content_link/[^"]+)"')

def dl_online(ebook):
    if ebook.format != 'online':
        pass
    elif ebook.url.find(u'dropbox.com/s/') >= 0:
        if ebook.url.find(u'dl=0') >= 0:
            dl_url = ebook.url.replace(u'dl=0', u'dl=1')
            return make_dl_ebook(dl_url, ebook)
        response = requests.get(ebook.url, headers={"User-Agent": settings.USER_AGENT})
        if response.status_code == 200:
            match_dl = DROPBOX_DL.search(response.content)
            if match_dl:
                return make_dl_ebook(match_dl.group(1), ebook)
            else:
                logger.warning('couldn\'t get {}'.format(ebook.url))
        else:
            logger.warning('couldn\'t get dl for {}'.format(ebook.url))

    elif ebook.url.find(u'jbe-platform.com/content/books/') >= 0:
        doc = get_soup(ebook.url)
        if doc:
            obj = doc.select_one('div.fulltexticoncontainer-PDF a')
            if obj:
                dl_url = urlparse.urljoin(ebook.url, obj['href'])
                return make_dl_ebook(dl_url, ebook)
            else:
                logger.warning('couldn\'t get dl_url for {}'.format(ebook.url))
        else:
            logger.warning('couldn\'t get soup for {}'.format(ebook.url))

    return None, False

def make_dl_ebook(url, ebook):
    if EbookFile.objects.filter(source=ebook.url):
        return EbookFile.objects.filter(source=ebook.url)[0], False
    response = requests.get(url, headers={"User-Agent": settings.USER_AGENT})
    if response.status_code == 200:
        filesize = int(response.headers.get("Content-Length", 0))
        filesize = filesize if filesize else None
        format = type_for_url(url, content_type=response.headers.get('content-type'))
        if format != 'online':
            new_ebf = EbookFile.objects.create(
                edition=ebook.edition,
                format=format,
                source=ebook.url,
            )
            new_ebf.file.save(path_for_file(new_ebf, None), ContentFile(response.content))
            new_ebf.save()
            new_ebook = Ebook.objects.create(
                edition=ebook.edition,
                format=format,
                provider='Unglue.it',
                url=new_ebf.file.url,
                rights=ebook.rights,
                filesize=filesize,
                version_label=ebook.version_label,
                version_iter=ebook.version_iter,
            )
            new_ebf.ebook = new_ebook
            new_ebf.save()
            return new_ebf, True
        else:
            logger.warning('download format for {} is not ebook'.format(url))
    else:
        logger.warning('couldn\'t get {}'.format(url))
    return None, False

def type_for_url(url, content_type=None):
    if not url:
        return ''
    if url.find('books.openedition.org') >= 0:
        return 'online'
    if Ebook.objects.filter(url=url):
        return Ebook.objects.filter(url=url)[0].format
    ct = content_type if content_type else contenttyper.calc_type(url)
    if re.search("pdf", ct):
        return "pdf"
    elif re.search("octet-stream", ct) and re.search("pdf", url, flags=re.I):
        return "pdf"
    elif re.search("octet-stream", ct) and re.search("epub", url, flags=re.I):
        return "epub"
    elif re.search("text/plain", ct):
        return "text"
    elif re.search("text/html", ct):
        if url.find('oapen.org/view') >= 0:
            return "html"
        return "online"
    elif re.search("epub", ct):
        return "epub"
    elif re.search("mobi", ct):
        return "mobi"
    return "other"

class ContentTyper(object):
    """ """
    def __init__(self):
        self.last_call = dict()

    def content_type(self, url):
        try:
            r = requests.head(url)
            return r.headers.get('content-type', '')
        except:
            return ''

    def calc_type(self, url):
        delay = 1
        # is there a delay associated with the url
        netloc = urlparse.urlparse(url).netloc

        # wait if necessary
        last_call = self.last_call.get(netloc)
        if last_call is not None:
            now = time.time()
            min_time_next_call = last_call + delay
            if min_time_next_call > now:
                time.sleep(min_time_next_call-now)

        self.last_call[netloc] = time.time()

        # compute the content-type
        return self.content_type(url)

contenttyper = ContentTyper()
