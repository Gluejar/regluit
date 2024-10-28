# encoding: utf-8
#external library imports

import os
from datetime import datetime, timedelta
from decimal import Decimal as D
from math import factorial
import unittest
from urllib.parse import urlparse, parse_qs
from tempfile import NamedTemporaryFile
from time import sleep, mktime

from celery import group
import requests
import requests_mock
from pyepub import EPUB

#django imports
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.files import File as DjangoFile
from django.db import IntegrityError
from django.db import transaction
from django.http import Http404
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from django.utils.timezone import now

from django_comments.models import Comment

from regluit.payment.models import Transaction
from regluit.payment.parameters import PAYMENT_TYPE_AUTHORIZATION
from regluit.utils.localdatetime import date_today

from . import (
    bookloader,
    covers,
    isbn,
    librarything,
    models,
    parameters,
    search,
    tasks,
)
from .epub import test_epub
from .loaders.utils import (load_from_books, loaded_book_ok, )
from .models import (
    Campaign,
    Work,
    UnglueitError,
    Edition,
    RightsHolder,
    Claim,
    Ebook,
    Premium,
    Subject,
    Publisher,
    Offer,
    EbookFile,
    Acq,
    Hold,
    safe_get_work,
)
from .parameters import TESTING, LIBRARY, RESERVE
from .pdf import test_pdf
from .validation import valid_subject

TESTDIR = os.path.join(os.path.dirname(__file__), '../test/')
YAML_VERSIONFILE = os.path.join(TESTDIR, 'versiontest.yaml')
YAML_HUCKFILE = os.path.join(TESTDIR, 'raw/master/metadata.yaml')

class BookLoaderTests(TestCase):
    fixtures = ['initial_data.json', 'bookloader.json']

    def setUp(self):
        self.user = User.objects.create_user('core_test', 'test@example.org', 'core_test')
        self.client = Client()
        self.client.login(username='core_test', password='core_test')

    def test_add_by_local_yaml(self):

        noebook_id = bookloader.load_from_yaml(YAML_VERSIONFILE)
        noebook = models.Work.objects.get(id=noebook_id)
        self.assertEqual(noebook.first_ebook(), None)
        huck_id = bookloader.load_from_yaml(YAML_HUCKFILE, test_mode=True)
        huck = models.Work.objects.get(id=huck_id)
        self.assertTrue(huck.ebooks().count() > 1)


    def test_add_by_yaml(self):
        space_id = bookloader.load_from_yaml(
            'https://github.com/gitenberg-dev/metadata/raw/master/samples/pandata.yaml'
        )
        huck_id = bookloader.load_from_yaml(
            'https://github.com/GITenberg/Adventures-of-Huckleberry-Finn_76/raw/master/metadata.yaml'
        )
        space = models.Work.objects.get(id=space_id)
        huck = models.Work.objects.get(id=huck_id)

        #test ebook archiving
        num_ebf = EbookFile.objects.all().count()
        for ebook in huck.ebooks().all():
            f = ebook.get_archive()
        self.assertTrue(EbookFile.objects.all().count() > num_ebf)

    def test_add_by_isbn_mock(self):
        with requests_mock.Mocker(real_http=True) as m:
            with open(os.path.join(TESTDIR, 'gb_hamilton.json'), 'rb') as gb:
                m.get('https://www.googleapis.com/books/v1/volumes', content=gb.read())
            self.test_add_by_isbn(mocking=True)


    def test_add_by_isbn(self, mocking=False):
        if not (mocking or settings.TEST_INTEGRATION):
            return
        # edition
        edition = bookloader.add_by_isbn('9781101200858')
        self.assertEqual(edition.title, u'Alexander Hamilton')
        self.assertTrue('2005' in edition.publication_date)
        self.assertEqual(edition.publisher, u'Penguin')
        self.assertEqual(edition.isbn_10, '1101200855')
        self.assertEqual(edition.isbn_13, '9781101200858')
        self.assertTrue(edition.googlebooks_id in ('4z5eL5SGjEoC', '4iafgTEhU3QC'))

        # authors
        self.assertEqual(edition.authors.all().count(), 1)
        self.assertEqual(edition.authors.first().name, u'Ron Chernow')

        # work
        self.assertTrue(edition.work)
        self.assertTrue(edition.googlebooks_id in ('4z5eL5SGjEoC', '4iafgTEhU3QC'))
        self.assertEqual(edition.work.first_isbn_13(), '9781101200858')

        # test duplicate pubname
        ed2 = Edition.objects.create(work=edition.work)
        ed2.set_publisher(u'Penguin')

        # publisher names
        old_pub_name = edition.publisher_name
        edition.set_publisher('test publisher name')
        self.assertEqual(edition.publisher, u'test publisher name')
        pub = Publisher(name=edition.publisher_name)
        pub.save()
        self.assertEqual(edition.work.publishers().count(), 1)
        old_pub_name.publisher = pub
        old_pub_name.save()
        edition.set_publisher(u'Penguin')
        self.assertEqual(edition.publisher, u'test publisher name') # Perseus has been aliased

    def test_language_locale_mock(self):
        with requests_mock.Mocker(real_http=True) as m:
            with open(os.path.join(TESTDIR, 'gb_zhCN.json'), 'rb') as gb:
                m.get('https://www.googleapis.com/books/v1/volumes', content=gb.read())
            self.test_language_locale(mocking=True)

    def test_language_locale(self, mocking=False):
        if not (mocking or settings.TEST_INTEGRATION):
            return
        edition = bookloader.add_by_isbn('9787115401519')
        self.assertEqual(edition.work.language, u'zh-CN')

    def test_update_edition_mock(self):
        with requests_mock.Mocker(real_http=True) as m:
            with open(os.path.join(TESTDIR, 'python4da.json'), 'rb') as gb:
                m.get('https://www.googleapis.com/books/v1/volumes', content=gb.read())
            self.test_update_edition(mocking=True)

    def test_update_edition(self, mocking=False):
        if not (mocking or settings.TEST_INTEGRATION):
            return
        w = models.Work(title='silly title', language='xx')
        w.save()
        e = models.Edition(title=w.title, work=w)
        e.save()
        models.Identifier(type='isbn', value='9781449319793', work=w, edition=e).save()
        bookloader.update_edition(e)
        self.assertEqual(e.work.language, 'en')
        self.assertEqual(e.title, 'Python for Data Analysis')

    def test_double_add(self):
        edbefore = models.Edition.objects.all().count()
        autbefore = models.Author.objects.all().count()
        before = models.Work.objects.all().count()
        bookloader.add_by_isbn('0441007465') # in fixture
        self.assertEqual(models.Edition.objects.all().count(), edbefore)
        self.assertEqual(models.Author.objects.all().count(), autbefore)
        self.assertEqual(models.Work.objects.all().count(), before)

    def test_missing_isbn(self):
        e = bookloader.add_by_isbn_from_google('9781938616990') #unassigned in gluejar block
        self.assertEqual(e, None)

    def test_thingisbn_mock(self):
        with requests_mock.Mocker(real_http=True) as m:
            with open(os.path.join(TESTDIR, '9780441569595.xml'), 'rb') as lt:
                m.get('https://www.librarything.com/api/thingISBN/0441007465', content=lt.read())
            self.test_thingisbn(mocking=True)

    def test_thingisbn(self, mocking=False):
        if not (mocking or settings.TEST_INTEGRATION):
            return
        isbns = bookloader.thingisbn('0441007465') #Neuromancer
        self.assertTrue(len(isbns) > 20)
        self.assertTrue('0441007465' in isbns)
        self.assertTrue('3453313895' in isbns)

    def test_add_related(self):
        # add one edition
        #Neuromancer; editions in fixture not joined
        edition = bookloader.add_by_isbn('0441007465')
        edbefore = models.Edition.objects.count()
        before = models.Work.objects.count()
        lang = edition.work.language
        langbefore = models.Work.objects.filter(language=lang).count()
        # ask for related editions to be added using the work we just created
        with requests_mock.Mocker(real_http=True) as m:
            with open(os.path.join(TESTDIR, '9780441569595.xml'), 'rb') as lt:
                m.get('https://www.librarything.com/api/thingISBN/0441007465', content=lt.read())
            bookloader.add_related('0441007465') # should join the editions
        self.assertTrue(models.Edition.objects.count() >= edbefore)
        self.assertTrue(models.Work.objects.filter(language=lang).count() < langbefore)
        self.assertTrue(edition.work.editions.count() > 9)
        self.assertTrue(edition.work.reverse_related.count() > 0)

        # is edition.work found among the from_work of all the to_work of edition.work?
        back_point = True
        to_works = [wr.to_work for wr in edition.work.works_related_from.all()]
        for to_work in to_works:
            if edition.work_id not in [wr1.from_work.id for wr1 in to_work.works_related_to.all()]:
                back_point = False
                break
        self.assertTrue(back_point)


    def test_populate_edition(self):
        edition = bookloader.add_by_isbn('9780606301121') # A People's History Of The United States
        with requests_mock.Mocker(real_http=True) as m:
            with open(os.path.join(TESTDIR, '9780061989834.xml'), 'rb') as lt:
                m.get('https://www.librarything.com/api/thingISBN/9780606301121', content=lt.read())
            edition = tasks.populate_edition.run(edition.isbn_13)
        self.assertTrue(edition.work.editions.all().count() > 10)
        self.assertTrue(edition.work.subjects.all().count() > 8)
        self.assertTrue(edition.work.publication_date)
        edition.publication_date = None
        self.assertTrue(edition.work.publication_date)
        self.assertTrue(len(edition.work.description) > 20)
        self.assertTrue(edition.work.identifiers.filter(type='oclc')[0])


    def test_merge_works_mechanics(self):
        """Make sure then merge_works is still okay when we try to merge
        works with themselves and with deleted works"""
        before = models.Work.objects.count()
        wasbefore = models.WasWork.objects.count()
        sub1 = Subject(name='test1')
        sub1.save()
        sub2 = Subject(name='test2')
        sub2.save()
        w1 = Work(title="Work 1")
        w1.save()
        w1.subjects.add(sub1)

        w2 = Work(title="Work 2")
        w2.save()
        w2.subjects.add(sub1, sub2)

        e1 = Edition(work=w1)
        e1.save()

        e2 = Edition(work=w2)
        e2.save()

        eb1 = Ebook(edition=e2)
        eb1.save()

        e2a = Edition(work=w2)
        e2a.save()

        self.assertTrue(e1)
        self.assertTrue(e2)
        self.assertTrue(e2a)
        self.assertTrue(e1.work)
        self.assertTrue(e2.work)
        self.assertEqual(models.Work.objects.count(), before + 2)

        self.assertTrue(w2.is_free)
        self.assertFalse(w1.is_free)
        sub2 = Subject.objects.get(pk=sub2.pk)
        self.assertEqual(sub2.num_free, 1)

        w1_id = w1.id
        w2_id = w2.id

        # first try to merge work 1 into itself -- should not do anything
        bookloader.merge_works(w1, w1)
        self.assertEqual(models.Work.objects.count(), before + 2)
        
        # first try to merge related works -- should not do anything
        rel, created = models.WorkRelation.objects.get_or_create(to_work=w1, from_work=w2, relation='part')
        bookloader.merge_works(w1, w2)
        self.assertEqual(models.Work.objects.count(), before + 2)
        rel.delete()
        
        # merge the second work into the first
        bookloader.merge_works(e1.work, e2.work)
        self.assertEqual(models.Work.objects.count(), before + 1)
        self.assertEqual(models.WasWork.objects.count(), wasbefore + 1)
        self.assertEqual(w1.subjects.count(), 2)
        sub1 = Subject.objects.get(pk=sub1.pk)
        self.assertEqual(sub2.num_free, 1)
        self.assertTrue(w1.is_free)

        # getting proper view?
        anon_client = Client()
        r = anon_client.get("/work/%s/" % w1_id)
        self.assertEqual(r.status_code, 200)
        r = anon_client.get("/work/%s/" % w2_id)
        self.assertEqual(r.status_code, 200)

        # try to do it twice -- nothing should happen
        bookloader.merge_works(e1.work, e2a.work)
        r = anon_client.get("/work/%s/" % w1_id)
        self.assertEqual(r.status_code, 200)
        r = anon_client.get("/work/%s/" % w2_id)
        self.assertEqual(r.status_code, 200)

        # if the work has a selected edition, then don't touch the work.
        w3 = Work(title='work 3')
        e_pref = Edition(work=w1)
        w1.selected_edition = e_pref
        bookloader.merge_works(w3, w1)
        self.assertTrue(w1.title == 'Work 1')

    def test_merge_works(self):
        before = models.Work.objects.count()
        # add two editions and see that there are two stub works

        # for this test, use two unjoined Neuromancer works in fixture
        isbn1 = '9780441569595'
        isbn2 = '9780441012039'
        e1 = bookloader.add_by_isbn(isbn1)
        e2 = bookloader.add_by_isbn(isbn2)
        self.assertTrue(e1)
        self.assertTrue(e2)
        self.assertTrue(e1.work)
        self.assertTrue(e2.work)

        # add the stub works to a wishlist
        user = User.objects.create_user('test', 'test@example.org', 'testpass')
        user.wishlist.add_work(e1.work, 'test')
        user.wishlist.add_work(e2.work, 'test')
        manager = User.objects.create_user('manager', 'manager@example.org', 'managerpass')
        # create campaigns for the stub works
        c1 = models.Campaign.objects.create(
            name=e1.work.title,
            work=e1.work,
            description='Test Campaign 1',
            deadline=now(),
            target=D('1000.00'),
        )
        c2 = models.Campaign.objects.create(
            name=e2.work.title,
            work=e2.work,
            description='Test Campaign 2',
            deadline=now(),
            target=D('1000.00'),
        )
        c2.managers.add(manager)
        c2.save()
        self.assertEqual(c2.pk, e2.work.last_campaign().pk)
        # comment on the works
        site = Site.objects.first()
        wct = ContentType.objects.get_for_model(models.Work)
        comment1 = Comment(
            content_type=wct,
            object_pk=e1.work.pk,
            comment="test comment1",
            user=user,
            site=site
        )
        comment1.save()
        comment2 = Comment(
            content_type=wct,
            object_pk=e2.work.pk,
            comment="test comment2",
            user=user,
            site=site
        )
        comment2.save()
        comment3 = Comment(
            content_type=wct,
            object_pk=e2.work.pk,
            comment="test comment3",
            user=manager,
            site=site
        )
        comment3.save()


        # now add related edition to make sure Works get merged
        bookloader.add_related(isbn1)
        # non-zero
        self.assertGreater(models.Work.objects.count(), 0)
        w3 = models.Edition.get_by_isbn(isbn1).work

        # and that relevant Campaigns and Wishlists are updated
        c1 = Campaign.objects.get(pk=c1.pk)
        c2 = Campaign.objects.get(pk=c2.pk)

        self.assertEqual(c1.work, c2.work)
        self.assertEqual(user.wishlist.works.all().count(), 1)
        self.assertEqual(Comment.objects.for_model(w3).count(), 3)

        anon_client = Client()
        r = anon_client.get("/work/%s/" % w3.pk)
        self.assertEqual(r.status_code, 200)
        r = anon_client.get("/work/%s/" % e2.work.pk)
        self.assertEqual(r.status_code, 200)


    def test_ebook(self):
        with requests_mock.Mocker(real_http=True) as m:
            with open(os.path.join(TESTDIR, 'gb_latinlanguage.json'), 'rb') as gb:
                m.get('https://www.googleapis.com/books/v1/volumes', content=gb.read())
                edition = bookloader.add_by_oclc('1246014')
            # we've seen the public domain status of this book fluctuate -- and the OCLC
            # number can disappear. So if the ebook count is 2 then test
            #if edition is not None and edition.ebooks.count() == 2:
                self.assertEqual(edition.ebooks.count(), 2)
                #ebook_epub = edition.ebooks.first()
                ebook_epub = edition.ebooks.filter(format='epub')[0]
                self.assertEqual(ebook_epub.format, 'epub')
                self.assertEqual(parse_qs(urlparse(ebook_epub.url).query).get("id"), ['N1RfAAAAMAAJ'])
                self.assertEqual(parse_qs(urlparse(ebook_epub.url).query).get("output"), ['epub'])
                self.assertEqual(ebook_epub.provider, 'Google Books')
                self.assertEqual(ebook_epub.set_provider(), 'Google Books')
                ebook_pdf = edition.ebooks.filter(format='pdf')[0]
                self.assertEqual(ebook_pdf.format, 'pdf')
                self.assertEqual(parse_qs(urlparse(ebook_pdf.url).query).get("id"), ['N1RfAAAAMAAJ'])
                self.assertEqual(parse_qs(urlparse(ebook_pdf.url).query).get("output"), ['pdf'])
                self.assertEqual(ebook_pdf.provider, 'Google Books')

                w = edition.work
                self.assertEqual(w.first_epub().url, ebook_epub.url)
                self.assertEqual(w.first_pdf().url, ebook_pdf.url)
                self.assertEqual(w.first_epub_url(), ebook_epub.url)
                self.assertEqual(w.first_pdf_url(), ebook_pdf.url)

                ebook_pdf.url = 'https://en.wikisource.org/wiki/Frankenstein'
                self.assertEqual(ebook_pdf.set_provider(), 'Wikisource')

                self.user.wishlist.add_work(w, 'test')
                tasks.report_new_ebooks(date_today())
                r = self.client.get("/notification/")
                self.assertEqual(r.status_code, 200)

                ebook_pdf.increment()
                updated_ebook = Ebook.objects.get(pk=ebook_pdf.pk)
                #self.assertEqual(int(updated_ebook.download_count), 1)
                #self.assertEqual(int(edition.work.download_count), 1)

    def test_add_no_ebook(self):
        # this edition lacks an ebook, but we should still be able to load it
        # http://books.google.com/books?id=D-WjL_HRbNQC&printsec=frontcover#v=onepage&q&f=false
        # Social Life of Information
        with requests_mock.Mocker(real_http=True) as m:
            with open(os.path.join(TESTDIR, 'gb_sociallife.json'), 'rb') as gb:
                m.get('https://www.googleapis.com/books/v1/volumes', content=gb.read())
                e = bookloader.add_by_isbn('1578517087')
                self.assertTrue(e)

    def test_add_openlibrary(self):
        work = bookloader.add_by_isbn('0441007465').work
        bookloader.add_related('0441007465')
        bookloader.add_openlibrary(work)
        subjects = [s.name for s in work.subjects.all()]
        self.assertTrue(len(subjects) > 10)
        self.assertTrue('Science fiction' in subjects)
        self.assertTrue('/works/OL27258W' in work.identifiers.filter(type='olwk').values_list('value', flat=True))
        self.assertTrue('609' in work.identifiers.filter(type='ltwk').values_list('value', flat=True))

    def test_unicode_openlibrary(self):
        with requests_mock.Mocker(real_http=True) as m:
            with open(os.path.join(TESTDIR, 'gb_fightclub.json'), 'rb') as gb:
                m.get('https://www.googleapis.com/books/v1/volumes', content=gb.read())
            work = bookloader.add_by_isbn('9783894808358').work #fight club
            bookloader.add_openlibrary(work)
        self.assertTrue(work.description.startswith('Sie sind jung,'))

    def notest_load_gutenberg_edition(self):
        """Let's try this out for Moby Dick"""

        title = "Moby Dick"
        ol_work_id = "/works/OL102749W"
        gutenberg_etext_id = 2701
        epub_url = "https://www.gutenberg.org/cache/epub/2701/pg2701.epub"
        license = 'https://www.gutenberg.org/license'
        lang = 'en'
        format = 'epub'
        publication_date = datetime(2001, 7, 1)
        # https://www.amazon.com/Moby-Dick-Whale-Penguin-Classics-Deluxe/dp/0142000086
        seed_isbn = '9780142000083'

        ebook = bookloader.load_gutenberg_edition(
            title,
            gutenberg_etext_id,
            ol_work_id,
            seed_isbn,
            epub_url,
            format,
            license,
            lang,
            publication_date
        )
        self.assertEqual(ebook.url, epub_url)

    def tearDown(self):
        for ebf in EbookFile.objects.all():
            ebf.file.delete()

class SearchTests(TestCase):
    def test_search_mock(self):
        with requests_mock.Mocker(real_http=True) as m:
            with open(
                os.path.join(TESTDIR, 'gb_melville.json'), 'rb'
            ) as gb, open(os.path.join(TESTDIR, 'gb_melville2.json'), 'rb') as gb2:
                m.get(
                    'https://www.googleapis.com/books/v1/volumes',
                    [{'content':gb2.read()}, {'content':gb.read()}]
                )
            self.test_pagination(mocking=True)
            self.test_basic_search(mocking=True)
            self.test_googlebooks_search(mocking=True)

    def test_basic_search(self, mocking=False):
        if not (mocking or settings.TEST_INTEGRATION):
            return
        results = search.gluejar_search('melville')
        self.assertEqual(len(results), 10)

        r = results[0]
        self.assertTrue('title' in r)
        self.assertTrue('author' in r)
        self.assertTrue('description' in r)
        self.assertTrue('cover_image_thumbnail' in r)
        self.assertTrue(
            r['cover_image_thumbnail'].startswith('https')
            or r['cover_image_thumbnail'].startswith('http')
        )
        self.assertTrue('publisher' in r)
        self.assertTrue('isbn_13' in r)
        self.assertTrue('googlebooks_id' in r)

    def test_pagination(self, mocking=False):
        if not (mocking or settings.TEST_INTEGRATION):
            return
        r1 = search.gluejar_search('melville', page=1)
        r2 = search.gluejar_search('melville', page=2)
        isbns1 = set([r['isbn_13'] for r in r1])
        isbns2 = set([r['isbn_13'] for r in r2])
        self.assertTrue(isbns1 != isbns2)

    def test_googlebooks_search(self, mocking=False):
        if not (mocking or settings.TEST_INTEGRATION):
            return
        response = search.googlebooks_search('melville', '69.243.24.29', 1)
        self.assertEqual(len(response['items']), 10)


class CampaignTests(TestCase):
    fixtures = ['initial_data.json']
    def test_b2u(self):
        w = Work()
        w.save()
        this_year = datetime.now().year
        c = Campaign(
            target=D('12000.00'),
            deadline=datetime(this_year, 1, 1),
            work=w, type=2,
            cc_date_initial=datetime(this_year + 100, 1, 1),
            )
        self.assertTrue(c.set_dollar_per_day() < 0.34)
        self.assertTrue(c.dollar_per_day > 0.31)
        t = Transaction(type=1, campaign=c, approved=True, amount=D(6000.1), status="Complete")
        t.save()
        c.status = 'ACTIVE'
        c.save()
        c.update_left()
        #print(w.percent_of_goal())
        self.assertEqual(w.percent_unglued(), 3)
        self.assertTrue(w.percent_of_goal() > 49)
        ofr = Offer.objects.create(work=w, price=D(10), active=True)
        self.assertTrue(c.days_per_copy < D(32.26))
        self.assertTrue(c.days_per_copy > D(29.41))

    def test_required_fields(self):
        # a campaign must have a target, deadline and a work
        # see https://stackoverflow.com/questions/21458387/transactionmanagementerror-you-cant-execute-queries-until-the-end-of-the-atom
        with transaction.atomic():
            c = Campaign()
            self.assertRaises(IntegrityError, c.save)
        with transaction.atomic():
            c = Campaign(target=D('1000.00'))
            self.assertRaises(IntegrityError, c.save)
        with transaction.atomic():
            c = Campaign(target=D('1000.00'), deadline=datetime(2013, 1, 1))
            self.assertRaises(IntegrityError, c.save)

        w = Work()
        w.save()
        c = Campaign(target=D('1000.00'), deadline=datetime(2013, 1, 1), work=w)
        c.license = 'CC BY-NC'
        c.save()
        self.assertEqual(c.license_url, 'https://creativecommons.org/licenses/by-nc/3.0/')
        self.assertEqual(c.license_badge, '/static/images/ccbync.png')

    def test_campaign_status(self):

        # need a user to associate with a transaction
        user = User.objects.create_user('test', 'test@example.org', 'testpass')

        w = Work()
        w.save()
        w2 = Work()
        w2.save()
        # INITIALIZED
        c1 = Campaign(target=D('1000.00'), deadline=Campaign.latest_ending(), work=w)
        c1.save()
        self.assertEqual(c1.status, 'INITIALIZED')
        # ACTIVATED
        c2 = Campaign(
            target=D('1000.00'),
            deadline=datetime(2013, 1, 1),
            work=w,
            description='dummy description'
        )
        c2.save()
        self.assertEqual(c2.status, 'INITIALIZED')
        u = User.objects.create_user('claimer', 'claimer@example.org', 'claimer')
        u.save()
        rh = RightsHolder(owner=u, rights_holder_name='rights holder name')
        rh.save()
        cl = Claim(rights_holder=rh, work=w, user=u, status='active')
        cl.save()
        cl2 = Claim(rights_holder=rh, work=w2, user=u, status='active')
        cl2.save()
        c2.activate()
        self.assertEqual(c2.status, 'ACTIVE')
        # SUSPENDED
        c2.suspend(reason="for testing")
        self.assertEqual(c2.status, 'SUSPENDED')
        # RESUMING
        c2.resume(reason="for testing")
        #self.assertEqual(c2.suspended, None)
        self.assertEqual(c2.status, 'ACTIVE')
        # should not let me suspend a campaign that hasn't been initialized
        self.assertRaises(UnglueitError, c1.suspend, "for testing")
        # UNSUCCESSFUL
        c3 = Campaign(
            target=D('1000.00'),
            deadline=now() - timedelta(days=1),
            work=w2,
            description='dummy description'
        )
        c3.save()
        c3.activate()
        self.assertEqual(c3.status, 'ACTIVE')
        # at this point, since the deadline has passed,
        # the status should change and be UNSUCCESSFUL
        self.assertTrue(c3.update_status())
        self.assertEqual(c3.status, 'UNSUCCESSFUL')

        # premiums
        pr1 = Premium(type='CU', campaign=c3, amount=10, description='botsnack', limit=1)
        pr1.save()
        self.assertEqual(pr1.premium_remaining, 1)

        #cloning (note we changed c3 to w2 to make it clonable)
        c7 = c3.clone()
        self.assertEqual(c7.status, 'INITIALIZED')
        self.assertEqual(c7.premiums.first().description, 'botsnack')


        # SUCCESSFUL
        c4 = Campaign(
            target=D('1000.00'),
            deadline=now() - timedelta(days=1),
            work=w,
            description='dummy description'
        )
        c4.save()
        c4.activate()
        t = Transaction()
        t.amount = D('1234.00')
        t.type = PAYMENT_TYPE_AUTHORIZATION
        t.status = 'ACTIVE'
        t.approved = True
        t.campaign = c4
        t.user = user
        t.save()
        self.assertTrue(c4.update_status())
        self.assertEqual(c4.status, 'SUCCESSFUL')

        # WITHDRAWN
        c5 = Campaign(
            target=D('1000.00'),
            deadline=datetime(2013, 1, 1),
            work=w,
            description='dummy description'
        )
        c5.save()
        c5.activate().withdraw('testing')
        self.assertEqual(c5.status, 'WITHDRAWN')

        # testing percent-of-goal
        w2 = Work()
        w2.save()
        c6 = Campaign(
            target=D('1000.00'),
            deadline=now() + timedelta(days=1),
            work=w2,
            description='dummy description'
        )
        c6.save()
        cl = Claim(rights_holder=rh, work=w2, user=u, status='active')
        cl.save()
        c6.activate()
        t = Transaction()
        t.amount = D('234.00')
        t.type = PAYMENT_TYPE_AUTHORIZATION
        t.status = 'ACTIVE'
        t.approved = True
        t.campaign = c6
        t.user = user
        t.save()
        self.assertEqual(w2.percent_of_goal(), 23)

        self.assertEqual(c1.launchable, False)
        c1.description = "description"
        self.assertEqual(c1.launchable, True)
        c1.work.create_offers()
        self.assertEqual(c1.work.offers.count(), 2)
        self.assertEqual(c1.work.offers.filter(license=2).count(), 1)
        c1.type = 2
        c1.save()
        self.assertEqual(c1.launchable, False)
        of1 = c1.work.offers.get(license=2)
        of1.price = D(2)
        of1.active = True
        of1.save()
        self.assertEqual(c1.launchable, False)
        e1 = models.Edition(title="title", work=c1.work)
        e1.save()
        ebf1 = models.EbookFile(edition=e1, format=1)
        ebf1.save()
        c1.set_cc_date_initial()
        self.assertEqual(c1.cc_date, settings.MAX_CC_DATE)
        c1.target = D(settings.UNGLUEIT_MAXIMUM_TARGET)
        c1.save()
        self.assertEqual(c1.launchable, True)

class WishlistTest(TestCase):
    fixtures = ['initial_data.json', 'neuromancer.json']
    def test_add_remove(self):
        # add a work to a user's wishlist
        user = User.objects.create_user('test', 'test@example.org', 'testpass')
        edition = bookloader.add_by_isbn('0441007465')
        work = edition.work
        num_wishes = work.num_wishes
        user.wishlist.add_work(work, 'test')
        self.assertEqual(user.wishlist.works.count(), 1)
        self.assertEqual(work.num_wishes, num_wishes+1)
        self.assertEqual(work.priority(), 2)
        user.wishlist.remove_work(work)
        self.assertEqual(user.wishlist.works.count(), 0)
        self.assertEqual(work.num_wishes, num_wishes)

class CeleryTaskTest(TestCase):

    def test_single_fac(self):
        n = 10
        task = tasks.fac.delay(n)
        result = task.get(timeout=10)
        self.assertEqual(result, factorial(n))

    def test_subtask(self):
        n = 30
        subtasks = [tasks.fac.subtask(args=(x,)) for x in range(n)]
        job = group(subtasks)
        result = job.apply_async()
        while not result.ready():
            sleep(0.2)
        self.assertEqual(result.join(), [factorial(x) for x in range(n)])


class LibraryThingTest(TestCase):

    def test_scrape_test_lib(self):
        # account yujx : has one book: 0471925675
        lt_username = 'yujx'
        lt = librarything.LibraryThing(username=lt_username)
        books = list(lt.parse_user_catalog(view_style=5))
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0]['isbn'], '0471925675')
        self.assertEqual(books[0]['work_id'], '80826')
        self.assertEqual(books[0]['book_id'], '79883733')

class ISBNTest(TestCase):

    def test_ISBN(self):
        milosz_10 = '006019667X'
        milosz_13 = '9780060196677'
        python_10 = '0-672-32978-6'
        funky = u'0–672—329 78-6' # endash, mdash, space
        python_10_wrong = '0-672-32978-7'
        python_13 = '978-0-672-32978-4'

        isbn_python_10 = isbn.ISBN(python_10)
        isbn_python_13 = isbn.ISBN(python_13)
        # return None for invalid characters
        self.assertEqual(None, isbn.ISBN("978-0-M72-32978-X").to_string('13'))
        self.assertEqual(isbn.ISBN("978-0-M72-32978-X").valid, False)
        self.assertEqual(None, bookloader.valid_isbn("978-0-M72-32978-X"))
        # check that only ISBN 13 starting with 978 or 979 are accepted
        self.assertEqual(None, isbn.ISBN("111-0-M72-32978-X").to_string())
        self.assertEqual(None, bookloader.valid_isbn("111-0-M72-32978-X"))
        self.assertEqual(isbn_python_13.to_string(), bookloader.valid_isbn(funky))

        # right type?
        self.assertEqual(isbn_python_10.type, '10')
        self.assertEqual(isbn_python_13.type, '13')
        # valid?
        self.assertEqual(isbn_python_10.valid, True)
        self.assertEqual(isbn.ISBN(python_10_wrong).valid, False)
        self.assertEqual(13, len(bookloader.valid_isbn(python_10)))
        self.assertEqual(isbn_python_13.to_string(), bookloader.valid_isbn(python_10_wrong))

        # do conversion -- first the outside methods
        self.assertEqual(isbn.convert_10_to_13(isbn.strip(python_10)), isbn.strip(python_13))
        self.assertEqual(isbn.convert_10_to_13(isbn.strip(python_10)), isbn.strip(python_13))
        self.assertEqual(isbn.convert_13_to_10('xxxxxxxxxxxxx'), None)
        self.assertEqual(isbn.convert_10_to_13('xxxxxxxxxx'), None)
        self.assertEqual(None, bookloader.valid_isbn('xxxxxxxxxxxxx'))
        self.assertEqual(None, bookloader.valid_isbn('xxxxxxxxxx'))

        # check formatting
        self.assertEqual(isbn.ISBN(python_13).to_string(type='13'), '9780672329784')
        self.assertEqual(isbn.ISBN(python_13).to_string('13', True), '978-0-672-32978-4')
        self.assertEqual(isbn.ISBN(python_13).to_string(type='10'), '0672329786')
        self.assertEqual(isbn.ISBN(python_10).to_string(type='13'), '9780672329784')
        self.assertEqual(isbn.ISBN(python_10).to_string(10, True), '0-672-32978-6')

        # complain if one tries to get ISBN-10 for a 979 ISBN 13
        # making up a 979 ISBN
        isbn_979 = isbn.ISBN("979-1-234-56789-0").validate()
        self.assertEqual(isbn_979.to_string('10'), None)

        # check casting to string -- ISBN 13
        self.assertEqual(str(isbn.ISBN(python_10)), '0672329786')

        # test __eq__ and __ne__ and validate
        self.assertTrue(isbn.ISBN(milosz_10) == isbn.ISBN(milosz_13))
        self.assertTrue(isbn.ISBN(milosz_10) == milosz_13)
        self.assertFalse(isbn.ISBN(milosz_10) == 'ddds')
        self.assertFalse(isbn.ISBN(milosz_10) != milosz_10)
        self.assertTrue(isbn.ISBN(python_10) != python_10_wrong)
        self.assertEqual(isbn.ISBN(python_10_wrong).validate(), python_10)
        self.assertEqual(isbn.ISBN(python_13).validate(), python_10)

        # curious about set membership
        self.assertEqual(len(set([str(isbn.ISBN(milosz_10)), str(isbn.ISBN(milosz_13))])), 2)
        self.assertEqual(
            len(set([isbn.ISBN(milosz_10).to_string(), isbn.ISBN(milosz_13).to_string()])),
            1
        )

class SafeGetWorkTest(TestCase):
    def test_good_work(self):
        w1 = models.Work()
        w1.save()
        w2 = models.Work()
        w2.save()
        w2_id = w2.id
        bookloader.merge_works(w1, w2)

        work = safe_get_work(w1.id)
        self.assertEqual(work, w1)
        work = safe_get_work(w2_id)
        self.assertEqual(work, w1)
        self.assertRaises(Work.DoesNotExist, safe_get_work, 3)

class WorkTests(TestCase):
    def setUp(self):
        self.w1 = models.Work.objects.create()
        self.w2 = models.Work.objects.create()

    def test_preferred_edition(self):
        ww = models.WasWork.objects.create(work=self.w1, was=self.w2.id)
        e1 = models.Edition.objects.create(work=self.w1)
        self.assertEqual(e1, self.w1.preferred_edition)
        e2 = models.Edition.objects.create(work=self.w1)
        self.w1.selected_edition = e2
        self.w1.save()
        self.assertEqual(e2, self.w1.preferred_edition)
        self.assertEqual(e2, self.w2.preferred_edition)

    def test_valid_subject(self):
        self.assertTrue(valid_subject(u'A, valid, suj\xc3t'))
        self.assertFalse(valid_subject(u'A, valid, suj\xc3t, '))
        self.assertFalse(valid_subject(u'A valid suj\xc3t \x01'))
        Subject.set_by_name(u'A, valid, suj\xc3t; A, valid, suj\xc3t, ', work=self.w1)
        self.assertEqual(1, self.w1.subjects.count())
        sub = Subject.set_by_name('nyt:hardcover_advice=2011-06-18', work=self.w1)
        self.assertEqual(sub.name, 'NYT Bestseller - Hardcover advice')
        self.assertEqual(2, self.w1.subjects.count())
        sub2 = Subject.set_by_name('!lcsh: Something', work=self.w1)
        self.assertEqual(sub2.name, 'Something')
        self.assertEqual(3, self.w1.subjects.count())
        sub3 = Subject.set_by_name('Something', work=self.w1)
        self.assertEqual(sub3.name, 'Something')
        self.assertEqual(3, self.w1.subjects.count())
        self.assertEqual(sub3.authority, 'lcsh')


class DownloadPageTest(TestCase):
    fixtures = ['initial_data.json']
    def test_download_page(self):
        w = models.Work()
        w.save()

        e1 = models.Edition()
        e1.work = w
        e1.unglued = True
        e2 = models.Edition()
        e2.work = w
        e1.save()
        e2.save()

        eb1 = models.Ebook()
        eb1.url = "https://example.org"
        eb1.edition = e1
        eb1.format = 'epub'


        eb1.save()

        anon_client = Client()
        response = anon_client.get("/work/%s/download/" % w.id, follow=True)
        self.assertContains(response, "/download_ebook/%s/"% eb1.id, count=12)
        self.assertTrue(eb1.edition.work.is_free)
        eb1.delete()

class MailingListTests(TestCase):
    #mostly to check that MailChimp account is setp correctly

    def test_mailchimp(self):
        from mailchimp3 import MailChimp
        mc_client = MailChimp(settings.MAILCHIMP_API_KEY)
        if settings.TEST_INTEGRATION:
            root = mc_client.root.get()
            self.assertEqual(root[u'account_id'], u'15472878790f9faa11317e085')
            self.user = User.objects.create_user('chimp_test', 'eric@gluejar.com', 'chimp_test')
            self.assertTrue(self.user.profile.on_ml)

class CoverTests(TestCase):
    test_image = 'https://unglue.it/static/images/logo.png'
    test_bad_image = 'https://example.com/static/images/logo.png'
    def setUp(self):
        self.work = Work.objects.create(title="Cover Work")
        self.edition = Edition.objects.create(title=self.work.title, work=self.work)
        covers.sorl_get_thumbnail(self.test_image, 'x550', crop='noop', quality=95)
    
    def test_cached_cover(self):
        thumb = covers.get_thumbnail(self.test_image, 'x550', crop='noop', quality=95)
        self.assertTrue(thumb.exists())
        self.assertTrue(thumb.width, 550)

    def test_bad_cover(self):
        thumb = covers.get_thumbnail(self.test_bad_image, '128', crop='noop', quality=95)
        self.assertEqual(thumb.url, covers.DEFAULT_COVER)
        

@override_settings(LOCAL_TEST=True)
class EbookFileTests(TestCase):
    fixtures = ['initial_data.json']
    def test_badepub_errors(self):
        textfile = NamedTemporaryFile(delete=False)
        textfile.write(b"bad text file")
        textfile.seek(0)
        self.assertTrue(test_epub(textfile))

    def test_ebookfile(self):
        """
        Read the test epub file
        """
        w = Work.objects.create(title="Work 1")
        e = Edition.objects.create(title=w.title, work=w)
        u = User.objects.create_user('test', 'test@example.org', 'testpass')
        rh = RightsHolder.objects.create(owner=u, rights_holder_name='rights holder name')
        cl = Claim.objects.create(rights_holder=rh, work=w, user=u, status='active')
        c = Campaign.objects.create(
            work=w,
            type=parameters.BUY2UNGLUE,
            cc_date_initial=datetime(2030, 1, 1),
            target=1000,
            deadline=datetime(2030, 1, 1),
            license='CC BY',
            description="dummy description",
        )
        # download the test epub into a temp file
        temp = NamedTemporaryFile(delete=False)
        test_file_content = requests.get(settings.BOOXTREAM_TEST_EPUB_URL).content

        temp.write(test_file_content)
        temp.close()

        try:
            # now we can try putting the test epub file into Django storage
            temp_file = open(temp.name, 'rb')

            dj_file = DjangoFile(temp_file)
            ebf = EbookFile(format='epub', edition=e, file=dj_file)
            ebf.save()

            temp_file.close()
        finally:
            # make sure we get rid of temp file
            os.remove(temp.name)

        test_epub = EPUB(ebf.file, mode='a')
        self.assertEqual(len(test_epub.opf), 4)
        self.assertTrue(len(test_epub.opf[2]) < 30)

        acq = Acq.objects.create(user=u, work=w, license=TESTING)
        self.assertIsNot(acq.nonce, None)

        url = acq.get_watermarked().download_link_epub
        self.assertRegexpMatches(url, 'github.com/eshellman/42_ebook/blob/master/download/42')
        #self.assertRegexpMatches(url, 'booxtream.com/')

        with self.assertRaises(UnglueitError) as cm:
            c.activate()
        off = Offer(price=10.00, work=w, active=True)
        off.save()
        c.activate()
        #flip the campaign to success
        c.cc_date_initial = datetime(2012, 1, 1)
        c.update_status()
        self.assertEqual(c.work.ebooks().count(), 1)
        c.do_watermark = False
        c.save()
        url = acq.get_watermarked().download_link_epub

    def test_ebookfile_thanks(self):
        w = Work.objects.create(title="Work 2")
        e = Edition.objects.create(title=w.title, work=w)
        u = User.objects.create_user('test2', 'test@example.org', 'testpass')
        rh = RightsHolder.objects.create(owner=u, rights_holder_name='rights holder name 2')
        cl = Claim.objects.create(rights_holder=rh, work=w, user=u, status='active')
        c = Campaign.objects.create(work=w,
                                    type=parameters.THANKS,
                                    license='CC BY-NC',
                                    description="Please send me money",
                                   )
        # download the test epub into a temp file
        temp = NamedTemporaryFile(delete=False)
        test_file_content = requests.get(settings.TEST_PDF_URL).content

        temp.write(test_file_content)
        temp.close()
        try:
            # now we can try putting the test pdf file into Django storage
            temp_file = open(temp.name, 'rb')

            dj_file = DjangoFile(temp_file)
            ebf = EbookFile(format='pdf', edition=e, file=dj_file)
            ebf.save()
            eb = Ebook(format='pdf', edition=e, url=ebf.file.url, provider='Unglue.it')
            eb.save()
            ebf.ebook = eb
            ebf.save()


            temp_file.close()
        finally:
            # make sure we get rid of temp file
            os.remove(temp.name)
        #test the ask-appender
        c.add_ask_to_ebfs()
        if settings.AWS_SECRET_ACCESS_KEY:
            askingpdfurl = c.work.ebookfiles().filter(asking=True)[0].file.url
            assert test_pdf(askingpdfurl)
        else:
            assert test_pdf(c.work.ebookfiles().filter(asking=True)[0].file)

        #Now do the same with epub
        temp = NamedTemporaryFile(delete=False)
        test_file_content = requests.get(settings.BOOXTREAM_TEST_EPUB_URL).content

        temp.write(test_file_content)
        temp.close()
        try:
            # now we can try putting the test pdf file into Django storage
            temp_file = open(temp.name, 'rb')

            dj_file = DjangoFile(temp_file)
            ebf = EbookFile(format='epub', edition=e, file=dj_file)
            ebf.save()
            eb = Ebook(format='epub', edition=e, url=ebf.file.url, provider='Unglue.it')
            eb.save()
            ebf.ebook = eb
            ebf.save()
            temp_file.close()
        finally:
            # make sure we get rid of temp file
            os.remove(temp.name)
        #test the ask-appender
        c.add_ask_to_ebfs()
        self.assertTrue(c.work.ebookfiles().filter(asking=True, format='epub').count() > 0)
        self.assertTrue(c.work.ebookfiles().filter(asking=True, ebook__active=True).count() > 0)
        self.assertTrue(c.work.ebookfiles().filter(asking=False, ebook__active=True).count() == 0)
        #test the unasker
        c.revert_asks()
        self.assertTrue(c.work.ebookfiles().filter(asking=True, ebook__active=True).count() == 0)
        self.assertTrue(c.work.ebookfiles().filter(asking=False, ebook__active=True).count() > 0)

    def test_bad_ebookfile(self):
        w = Work.objects.create(title="Work 3")
        e = Edition.objects.create(title=w.title, work=w)

        temp = NamedTemporaryFile(delete=False)
        test_file_content = b"bad text file"
        temp.write(test_file_content)
        temp.close()

        try:
            # put the bad file into Django storage
            temp_file = open(temp.name, 'rb')
            dj_file = DjangoFile(temp_file)
            ebf = EbookFile(format='epub', edition=e, file=dj_file)
            ebf.save()
            temp_file.close()
        finally:
            # make sure we get rid of temp file
            os.remove(temp.name)



@override_settings(LOCAL_TEST=True)
class LibTests(TestCase):
    fixtures = ['initial_data.json']
    class transaction:
        pass

    def test_purchase(self):
        w = Work.objects.create(title="Work 1")
        e = Edition.objects.create(title=w.title, work=w)
        u = User.objects.create_user('test', 'test@example.org', 'testpass')
        lu = User.objects.create_user('library', 'testu@example.org', 'testpass')
        Library = apps.get_model('libraryauth', 'Library')
        lib = Library.objects.create(user=lu, owner=u)
        c = Campaign.objects.create(
            work=w,
            type=parameters.BUY2UNGLUE,
            cc_date_initial=datetime(2020, 1, 1),
            target=1000,
            deadline=datetime(2020, 1, 1)
        )

        new_acq = Acq.objects.create(user=lib.user, work=c.work, license=LIBRARY)
        self.assertTrue(new_acq.borrowable)
        reserve_acq = Acq.objects.create(user=u, work=c.work, license=RESERVE, lib_acq=new_acq)
        self.assertTrue(reserve_acq.borrowable)
        self.assertFalse(new_acq.borrowable)

        self.assertTrue(reserve_acq.expires < now() + timedelta(hours=25))
        reserve_acq.borrow()
        self.assertTrue(reserve_acq.expires > now() + timedelta(hours=25))

        u2 = User.objects.create_user('user2', 'test2@example.org', 'testpass')
        Hold.objects.get_or_create(library=lib, work=w, user=u2)
        reserve_acq.expire_in(timedelta(seconds=0))
        tasks.refresh_acqs()
        self.assertEqual(reserve_acq.holds.count(), 0)

class GitHubTests(TestCase):
    def test_ebooks_in_github_release(self):
        (repo_owner, repo_name, repo_tag) = (
            'GITenberg',
            'Adventures-of-Huckleberry-Finn_76',
            '0.0.50'
        )
        ebooks = bookloader.ebooks_in_github_release(
            repo_owner,
            repo_name,
            tag=repo_tag,
            token=settings.GITHUB_PUBLIC_TOKEN
        )
        expected_set = set([
            ('epub', u'Adventures-of-Huckleberry-Finn.epub'),
            ('pdf', u'Adventures-of-Huckleberry-Finn.pdf')
            ])

        self.assertTrue(('epub', 'Adventures-of-Huckleberry-Finn.epub') in set(ebooks))
        self.assertTrue(('pdf', 'Adventures-of-Huckleberry-Finn.pdf') in set(ebooks))

class OnixLoaderTests(TestCase):
    fixtures = ['initial_data.json']
    def test_load(self):
        TEST_BOOKS = [{
            '': u'',
            'Author1First': u'Joseph',
            'Author1Last': u'Necvatal',
            'Author1Role': u'',
            'Author2First': u'',
            'Author2Last': u'',
            'Author2Role': u'',
            'Author3First': u'',
            'Author3Last': u'',
            'Author3Role': u'',
            'AuthorBio': u'',
            'AuthorsList': u'Joseph Nechvatal',
            'BISACCode1': u'',
            'BISACCode2': u'',
            'BISACCode3': u'',
            'Book-level DOI': u'10.3998/ohp.9618970.0001.001',
            'ClothISBN': u'N/A',
            'CopyrightYear': u'2011',
            'DescriptionBrief': u'',
            'DescriptionLong': u'',
            'Excerpt': u'',
            'FullTitle': u'Immersion into Noise',
            'License': u'CC BY-SA',
            'List Price in USD (paper ISBN)': u'23.99',
            'ListPriceCurrencyType': u'',
            'PaperISBN': u'9781607852414',
            'Publisher': u'Open Humanities Press',
            'SubjectListMARC': u'',
            'Subtitle': u'',
            'TableOfContents': u'',
            'Title': u'Immersion into Noise',
            'URL': u'https://doi.org/10.3998/ohp.9618970.0001.001',
            'eISBN': u'N/A',
            'eListPrice': u'N/A',
            'ePublicationDate': u'',
            'eTerritoryRights': u''
        }, {
            '': u'',
            'CAD price eub': u'9.95',
            'Title': u'That Greece Might Still Be Free',
            'USD price epub': u'9.95',
            'ISBN 2 with dashes': u'978-1-906924-01-0',
            'Plain Text Blurb': u'When in 1821, the Greeks rose in violent revolution against the rule of the Ottoman Turks, waves of sympathy spread across Western Europe and the United States. More than a thousand volunteers set out to fight for the cause. The Philhellenes, whether they set out to recreate the Athens of Pericles, start a new crusade, or make money out of a war, all felt that Greece had unique claim on the sympathy of the world. As Lord Byron wrote, "I dreamed that Greece might still be Free"; and he died at Missolonghi trying to translate that dream into reality. William St Clair\'s meticulously researched and highly readable account of their aspirations and experiences was hailed as definitive when it was first published. Long out of print, it remains the standard account of the Philhellenic movement and essential reading for any students of the Greek War of Independence, Byron, and European Romanticism. Its relevance to more modern ethnic and religious conflicts is becoming increasingly appreciated by scholars worldwide. This revised edition includes a new introduction by Roderick Beaton, an updated bibliography and many new illustrations.',
            'Cover URL': u'http://www.openbookpublishers.com/shopimages/products/cover/3',
            'keywords': u'Greece; Greek History; Lord Byron; War of Independence; Philhellenes; war; history; Romanticism',
            'Publication type': u'Monograph', 'GBP price epub': u'5.95', 'publication month': u'11', 'no of tables': u'',
            'GBP price paperback': u'15.95', 'AUD price epub': u'9.95', 'ISBN 4 with dashes': u'978-1-906924-02-7-epub',
            'DOI prefix': u'10.11647', 'License URL (human-readable summary)': u'https://creativecommons.org/licenses/by-nc-nd/2.0/',
            'Contributor 5 surname': u'', 'Contributor 1 first name': u'William', 'Contributor 6 first name': u'',
            'ONIX Role Code (List 17)6': u'', 'ONIX Role Code (List 17)5': u'', 'ONIX Role Code (List 17)4': u'',
            'ONIX Role Code (List 17)3': u'', 'ONIX Role Code (List 17)2': u'A24', 'ONIX Role Code (List 17)1': u'A01',
            'GBP price hardback': u'29.95', 'Subtitle': u'The Philhellenes in the War of Independence', 'ONIX tag6': u'',
            'ISBN 3 with dashes': u'978-1-906924-02-7', 'Countries excluded': u'None', 'first edition publication date': u'39753',
            'Original Language': u'English', 'ISBN 1 with dashes': u'978-1-906924-00-3', 'Contributor 4 first name': u'',
            'ISBN 5 with dashes': u'978-1-906924-02-7-mobi', 'Contributor 2 surname': u'Beaton',
            'License URL (our copyright tab)': u'https://www.openbookpublishers.com/isbn/9781906924003#copyright',
            'BISAC subject code 1': u'HIS042000', 'BISAC subject code 3': u'HIS037060',
            'BISAC subject code 2': u'HIS054000', 'BISAC subject code 5': u'',
            'BISAC subject code 4': u'', 'Status': u'Active', 'Geographic rights': u'Worldwide',
            'Series Name': u'', 'Contributor 5 first name': u'', 'ISSN Print with dashes': u'',
            'ISBN 5': u'9781906924027mobi', 'Contributor 1 surname': u'St Clair',
            'Contributor 2 first name': u'Roderick',
            'Book-page permanent URL': u'http://www.openbookpublishers.com/isbn/9781906924003',
            'EUR price hardback': u'36.95', 'EUR price epub': u'7.95', 'Contributor 6 surname': u'',
            'current edition number (integers only)': u'1',
            'Table of Content': u"Introduction by Roderick Beaton\n1. The Outbreak\n2. The Return of the Ancient Hellenes\n3. The Regiment\n4. Two Kinds of War\n5. The Cause of Greece, the Cause of Europe\n6. The Road to Marseilles\n7. Chios\n8. The Battalion of Philhellenes\n9. The Battle of Peta\n10. The Triumph of the Captains\n11. The Return Home\n12. The German Legion\n13. Knights and Crusaders\n14. Secrets of State\n15. Enter the British\n16. Lord Byron joins the Cause\n17. 'To bring Freedom and Knowledge to Greece'\n18. Arrivals at Missolonghi\n19. The Byron Brigade\n20. Essays in Regeneration\n21. The New Apostles\n22. The English Gold\n23. The Coming of the Arabs\n24. The Shade of Napoleon\n25. 'No freedom to fight for at home'\n26. French Idealism and French Cynicism\n27. Regulars Again\n28. A New Fleet\n29. Athens and Navarino\n30. America to the Rescue\n31. Later\nAppendix I: Remarks on Numbers\nAppendix II: The Principal Philhellenic Expeditions\nNotes on the Select Bibliography\nSelect Bibliography\nBibliography of Primary and Secondary Material Since 1972\nNotes\nIndex",
            'no of illustrations': u'41', 'OBP Role Name6': u'', 'GBP price PDF': u'5.95',
            'OBP Role Name4': u'', 'OBP Role Name5': u'', 'OBP Role Name2': u'Introduction',
            'OBP Role Name3': u'', 'OBP Role Name1': u'Author', 'ONIX Status code': u'04',
            'LLC (Library of Congress Codes)': u'', 'publication day': u'1',
            'Copyright holder 2': u'', 'Language': u'English', 'Contributor 3 first name': u'',
            'CAD price hardback': u'54.95', 'USD price paperback': u'26.95', 'ONIX tag1': u'By (author)',
            'ONIX tag3': u'', 'ONIX tag2': u'Introduction by', 'ONIX tag5': u'',
            'ONIX tag4': u'', 'no of audio/video': u'0', 'EUR price mobi': u'7.95',
            'Version of the license': u'2.0', 'publication year': u'2008',
            'CAD price paperback': u'29.95', 'Full-text URL - PDF': u'http://www.openbookpublishers.com/reader/3',
            'Copyright holder 1': u'William St Clair', 'Copyright holder 3': u'',
            'Short Blurb (less than 100 words)': u'When in 1821, the Greeks rose in violent revolution against Ottoman rule, waves of sympathy spread across western Europe and the USA. Inspired by a belief that Greece had a unique claim on the sympathy of the world, more than a thousand Philhellenes set out to fight for the cause. This meticulously researched and highly readable account of their aspirations and experiences has long been the standard account of the Philhellenic movement and essential reading for students of the Greek War of Independence, Byron and European Romanticism. Its relevance to more modern conflicts is also becoming increasingly appreciated.',
            'BIC subject code 3': u'3JH', 'BIC subject code 2': u'1DVG', 'BIC subject code 1': u'HBJD',
            'ISSN Digital with dashes': u'', 'USD price mobi': u'9.95', 'BIC subject code 5': u'',
            'BIC subject code 4': u'', 'ONIX Language Code': u'eng', 'AUD price paperback': u'29.95',
            'AUD price mobi': u'9.95', 'No. in the Series': u'', 'CAD price PDF': u'9.95',
            'CAD price mobi': u'9.95', 'DOI suffix': u'OBP.0001', 'USD price PDF': u'9.95',
            'Book-page URL': u'http://www.openbookpublishers.com/product/3',
            'Academic discipline (OBP)': u'History and Biography', 'EUR price paperback': u'19.95',
            'License': u'CC BY-NC-ND', 'AUD price PDF': u'9.95', 'Contributor 3 surname': u'',
            'AUD price hardback': u'54.95', 'ISBN 4': u'9781906924027epub', 'no of pages': u'440',
            'ISBN 2': u'9781906924010', 'ISBN 3': u'9781906924027', 'ISBN 1': u'9781906924003',
            'pages': u'xxi + 419', 'Contributor 4 surname': u'', 'USD price hardback': u'48.95',
            'Full-text URL - HTML': u'http://www.openbookpublishers.com/htmlreader/978-1-906924-00-3/main.html',
            'GBP price mobi': u'5.95', 'Format 1': u'Paperback ', 'EUR price PDF': u'7.95', 'Format 3': u'pdf',
            'Format 2': u'Hardback', 'Format 5': u'mobi', 'Format 4': u'epub', 'MARC Code1': u'aut',
            'MARC Code2': u'aui', 'MARC Code3': u'', 'MARC Code4': u'', 'MARC Code5': u'',
            'MARC Code6': u'', 'ISO Language Code': u'en'
        }]

        results = load_from_books(TEST_BOOKS)
        for (book, work, edition) in results:
            assert loaded_book_ok(book, work, edition)
