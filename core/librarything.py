import csv
import HTMLParser
import httplib
import logging
import re
from datetime import datetime

import mechanize
import requests

from regluit.core import models

logger = logging.getLogger(__name__)

class LibraryThingException(Exception):
    pass

class LibraryThing(object):
    """
    This class retrieves and parses the CSV representation of a LibraryThing user's library.
    """
    url = "https://www.librarything.com"
    csv_file_url = "https://www.librarything.com/export-csv"

    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        self.csv_handle = None

    def retrieve_csv(self):
        br = mechanize.Browser()
        br.open(LibraryThing.url)
        # select form#2
        br.select_form(nr=1)
        br["formusername"] = self.username
        br["formpassword"] = self.password
        br.submit()
        self.csv_handle = br.open(LibraryThing.csv_file_url)
        return self.csv_handle

    def parse_csv(self):
        h = HTMLParser.HTMLParser()
        reader = csv.DictReader(self.csv_handle)
        # There are more fields to be parsed out.  Note that there is a
        # second author column to handle
        for (i, row) in enumerate(reader):
            # ISBNs are written like '[123456789x]' in the CSV, suggesting possibility of a list
            m = re.match(r'^\[(.*)\]$', row["'ISBNs'"])
            if m:
                isbn = m.group(1).split()
            else:
                isbn = []
            yield {
                'title':h.unescape(row["'TITLE'"]),
                'author':h.unescape(row["'AUTHOR (first, last)'"]),
                'isbn':isbn,
                'comment':row["'COMMENT'"],
                'tags':row["'TAGS'"],
                'collections':row["'COLLECTIONS'"],
                'reviews':h.unescape(row["'REVIEWS'"])
            }
    def viewstyle_1(self, rows):

        for (i, row) in enumerate(rows):
            book_data = {}
            cols = row.xpath('td')
            # cover
            book_data["cover"] = {
                "cover_id":cols[0].attrib["id"],
                "image": {
                    "width":cols[0].xpath('.//img')[0].attrib['width'],
                    "src": cols[0].xpath('.//img')[0].attrib['src']
                }
            }
            # title
            book_data["title"] = {
                "href":cols[1].xpath('.//a')[0].attrib['href'],
                "title":cols[1].xpath('.//a')[0].text
            }

            # extract work_id and book_id from href
            try:
                (book_data["work_id"], book_data["book_id"]) = re.match(
                    "^/work/(.*)/book/(.*)$",
                    book_data["title"]["href"]
                ).groups()
            except:
                (book_data["work_id"], book_data["book_id"]) = (None, None)

            # author -- what if there is more than 1?  or none?
            try:
                book_data["author"] = {
                    "display_name":cols[2].xpath('.//a')[0].text,
                    "href":cols[2].xpath('.//a')[0].attrib['href'],
                    "name":cols[2].xpath('div')[0].text
                }
            except:
                book_data["author"] = None

            # date
            book_data["date"] = cols[3].xpath('span')[0].text

            # tags: grab tags that are not empty strings
            tag_links = cols[4].xpath('.//a')
            book_data["tags"] = filter(lambda x: x is not None, [a.text for a in tag_links])

            # rating -- count # of stars
            book_data["rating"] = len(cols[5].xpath('.//img[@alt="*"]'))

            # entry date
            book_data["entry_date"] = datetime.date(
                datetime.strptime(cols[6].xpath('span')[0].text, "%b %d, %Y")
            )

            yield book_data

    def viewstyle_5(self, rows):
        # implement this view to get at the ISBNs
        for (i, row) in enumerate(rows):
            book_data = {}
            cols = row.xpath('td')

            # title
            book_data["title"] = {"href":cols[0].xpath('.//a')[0].attrib['href'],
                                  "title":cols[0].xpath('.//a')[0].text}

            # extract work_id and book_id from href
            try:
                (book_data["work_id"], book_data["book_id"]) = re.match(
                    "^/work/(.*)/book/(.*)$",
                    book_data["title"]["href"]
                ).groups()
            except:
                (book_data["work_id"], book_data["book_id"]) = (None, None)

            # tags
            tag_links = cols[1].xpath('.//a')
            book_data["tags"] = filter(lambda x: x is not None, [a.text for a in tag_links])

            # lc classification
            try:
                book_data["lc_call_number"] = cols[2].xpath('.//span')[0].text
            except Exception, e:
                logger.info("no lc call number for: %s %s", book_data["title"], e)
                book_data["lc_call_number"] = None

            # subject

            subjects = cols[3].xpath('.//div[@class="subjectLine"]')
            book_data["subjects"] = [{'href':s.xpath('a')[0].attrib['href'],
                                      'text':s.xpath('a')[0].text} for s in subjects]

            # isbn
            try:
                book_data["isbn"] = cols[4].xpath('.//span')[0].text
                # check for &nbsp
                if book_data["isbn"] == u'\xA0':
                    book_data["isbn"] = None
            except Exception, e:
                book_data["isbn"] = None

            yield book_data


    def parse_user_catalog(self, view_style=1):
        from lxml import html

        # we can vary viewstyle to get different info

        IMPLEMENTED_STYLES = [1, 5]
        COLLECTION = 2 # set to get All Collections

        if view_style not in IMPLEMENTED_STYLES:
            raise NotImplementedError()
        style_parser = getattr(self, "viewstyle_%s" % view_style)
        next_page = True
        offset = 0
        cookies = None

        # go to the front page of LibraryThing first to pick up relevant session-like cookies
        r = requests.get("https://www.librarything.com/")
        cookies = r.cookies

        while next_page:
            url = "https://www.librarything.com/catalog_bottom.php?view=%s&viewstyle=%d&collection=%d&offset=%d" % (
                self.username, view_style, COLLECTION, offset
            )
            logger.info("url: %s", url)
            if cookies is None:
                r = requests.get(url)
            else:
                r = requests.get(url, cookies=cookies)

            if r.status_code != httplib.OK:
                raise LibraryThingException("Error accessing %s: status %s" % (url, r.status_code))
            etree = html.fromstring(r.content)
            cookies = r.cookies  # retain the cookies

            # look for a page bar
            # try to grab the total number of books
            # 1 - 50 of 82
            try:
                count_text = etree.xpath('//td[@class="pbGroup"]')[0].text
                total = int(re.search(r'(\d+)$', count_text).group(1))
                logger.info('total: %d', total)
            except Exception, e:
                # assume for now that if we can't grab this text,
                # there is no page bar and no books
                logger.info('Exception {0}'.format(e))
                total = 0

            # to do paging we can either look for a next link or just increase the offset
            # by the number of rows.
            # Let's try the latter
            # possible_next_link = etree.xpath('//a[@class="pageShuttleButton"]')[0]

            rows_xpath = '//table[@id="lt_catalog_list"]/tbody/tr'

            # deal with page 1 first and then working on paging through the collection
            rows = etree.xpath(rows_xpath)

            i = -1 # have to account for the problem of style_parser(rows) returning nothing

            for (i, row) in enumerate(style_parser(rows)):
                yield row

            # page size = 50, first page offset = 0, second page offset = 50
            # -- if total = 50 no need to go

            offset += i + 1
            if offset >= total:
                next_page = False

def load_librarything_into_wishlist(user, lt_username, max_books=None):
    """
    Load a specified LibraryThing shelf (by default:  all the books
    from the LibraryThing account associated with user)
    """

    from regluit.core import bookloader
    from regluit.core import tasks
    from itertools import islice

    logger.info("Entering into load_librarything_into_wishlist")
    lt = LibraryThing(lt_username)


    for (i, book) in enumerate(islice(lt.parse_user_catalog(view_style=5), max_books)):
        isbn = book["isbn"]  # grab the first one
        logger.info("%d %s %s", i, book["title"]["title"], isbn)
        try:
            if not isbn:
                continue
            edition = bookloader.add_by_isbn(isbn)
            if not edition:
                continue
            # add the librarything ids to the db since we know them now
            identifier = models.Identifier.get_or_add(
                type='thng',
                value=book['book_id'],
                edition=edition,
                work=edition.work
            )
            identifier = models.Identifier.get_or_add(
                type='ltwk',
                value=book['work_id'],
                work=edition.work
            )
            if book['lc_call_number']:
                identifier = models.Identifier.get_or_add(
                    type='lccn',
                    value=book['lc_call_number'],
                    edition=edition,
                    work=edition.work
                )
            user.wishlist.add_work(edition.work, 'librarything', notify=True)
            if edition.new:
                tasks.populate_edition.delay(edition.isbn_13)
            logger.info("Work with isbn %s added to wishlist.", isbn)
        except Exception, e:
            logger.info("error adding ISBN %s: %s", isbn, e)
