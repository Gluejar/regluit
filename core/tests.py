"""
external library imports
"""
from datetime import datetime, timedelta
from decimal import Decimal as D
from math import factorial
from time import sleep, mktime
from urlparse import parse_qs, urlparse
from tempfile import NamedTemporaryFile
from celery.task import chord
from celery.task.sets import TaskSet
import requests
import os

"""
django imports
"""
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.files import File as DjangoFile
from django.db import IntegrityError
from django.http import Http404
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from django.utils import unittest

"""
regluit imports
"""
from regluit.core import (
    isbn,
    bookloader,
    models,
    search,
    goodreads,
    librarything,
    tasks,
    parameters,
)
from regluit.core.models import (
    Campaign,
    Work,
    UnglueitError,
    Edition,
    RightsHolder,
    Claim,
    Key,
    Ebook,
    Premium,
    Subject,
    Publisher,
    Offer,
    EbookFile,
    Acq,
)

from regluit.core.parameters import TESTING
from regluit.frontend.views import safe_get_work
from regluit.payment.models import Transaction
from regluit.payment.parameters import PAYMENT_TYPE_AUTHORIZATION
from regluit.utils.localdatetime import now, date_today
from regluit.pyepub import EPUB

class BookLoaderTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('core_test', 'test@example.org', 'core_test')
        self.client = Client()
        self.client.login(username='core_test', password='core_test')

    def test_add_by_isbn(self):
        # edition
        edition = bookloader.add_by_isbn('0441007465')
        self.assertEqual(edition.title, 'Neuromancer')
        self.assertEqual(edition.publication_date, u'2000')
        self.assertEqual(edition.publisher, u'Penguin')
        self.assertEqual(edition.isbn_10, '0441007465')
        self.assertEqual(edition.isbn_13, '9780441007462')
        self.assertEqual(edition.googlebooks_id, 'IDFfMPW32hQC')

        # authors
        self.assertEqual(edition.authors.all().count(), 1)
        self.assertEqual(edition.authors.all()[0].name, 'William Gibson')

        # work
        self.assertTrue(edition.work)
        self.assertEqual(edition.work.googlebooks_id, 'IDFfMPW32hQC')
        self.assertEqual(edition.work.first_isbn_13(), '9780441007462')
        
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
        self.assertEqual(edition.publisher, u'test publisher name') # Penguin has been aliased
        # locale in language
        # Obama Dreams from My Father, Chinese edition
        # http://www.worldcat.org/title/oubama-de-meng-xiang-zhi-lu-yi-fu-zhi-ming/oclc/272997721&referer=brief_results
        edition = bookloader.add_by_isbn('9789571349268')
        self.assertEqual(edition.work.language, 'zh')

    # @unittest.expectedFailure
    def test_update_edition(self):  
        w = models.Work(title='silly title', language='xx')
        w.save()
        e = models.Edition(title=w.title,work=w)
        e.save()
        models.Identifier(type='isbn', value='9780226032030', work=w, edition=e).save()
        bookloader.update_edition(e)    
        self.assertEqual(e.work.language, 'en')
        self.assertEqual(e.title, 'Forbidden Journeys')

    def test_double_add(self):
        bookloader.add_by_isbn('0441007465')
        bookloader.add_by_isbn('0441007465')
        self.assertEqual(models.Edition.objects.all().count(), 1)
        self.assertEqual(models.Author.objects.all().count(), 1)
        self.assertEqual(models.Work.objects.all().count(), 1)
       
    def test_missing_isbn(self):
        e = bookloader.add_by_isbn_from_google('0139391401')
        self.assertEqual(e, None)

    def test_thingisbn(self):
        isbns = bookloader.thingisbn('0441007465')
        self.assertTrue(len(isbns) > 20)
        self.assertTrue('0441007465' in isbns)
        self.assertTrue('3453313895' in isbns)

    def test_add_related(self):
        # add one edition
        edition = bookloader.add_by_isbn('0441007465')
        self.assertEqual(models.Edition.objects.count(), 1)
        self.assertEqual(models.Work.objects.count(), 1)
        lang=edition.work.language
        # ask for related editions to be added using the work we just created
        bookloader.add_related('0441007465')
        self.assertTrue(models.Edition.objects.count() > 15)
        self.assertEqual(models.Work.objects.filter(language=lang).count(), 1)
        self.assertTrue(edition.work.editions.count() > 9)


    def test_populate_edition(self):
        edition = bookloader.add_by_googlebooks_id('c_dBPgAACAAJ')
        edition = tasks.populate_edition.run(edition.isbn_13)
        self.assertTrue(edition.work.editions.all().count() > 10)
        self.assertTrue(edition.work.subjects.all().count() > 8)
        self.assertTrue(edition.work.publication_date)
        edition.publication_date = None
        self.assertTrue(edition.work.publication_date)
        self.assertTrue(len(edition.work.description) > 20)
        self.assertTrue(edition.work.identifiers.filter(type='oclc')[0])
        

    def test_merge_works_mechanics(self):
        """Make sure then merge_works is still okay when we try to merge works with themselves and with deleted works"""
        sub1= Subject(name='test1')
        sub1.save()
        sub2= Subject(name='test2')
        sub2.save()
        w1 = Work(title="Work 1")
        w1.save()
        w1.subjects.add(sub1)
        
        w2 = Work(title="Work 2")
        w2.save()
        w2.subjects.add(sub1,sub2)
        
        e1 = Edition(work=w1)
        e1.save()
        
        e2 = Edition(work=w2)
        e2.save()
        
        e2a = Edition(work=w2)
        e2a.save()
        
        self.assertTrue(e1)
        self.assertTrue(e2)
        self.assertTrue(e2a)
        self.assertTrue(e1.work)
        self.assertTrue(e2.work)
        self.assertEqual(models.Work.objects.count(), 2)
 
        w1_id = w1.id
        w2_id = w2.id
        
        # first try to merge work 1 into itself -- should not do anything
        bookloader.merge_works(w1,w1)
        self.assertEqual(models.Work.objects.count(), 2)
        
        # merge the second work into the first
        bookloader.merge_works(e1.work, e2.work)
        self.assertEqual(models.Work.objects.count(),1)
        self.assertEqual(models.WasWork.objects.count(),1)
        self.assertEqual(w1.subjects.count(),2)
       
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
        

    def test_merge_works(self):
        # add two editions and see that there are two stub works
        
        # for this test, we need two isbns that are considered related in LibraryThing and are both
        # recognized by Google Books API
        # see http://nbviewer.ipython.org/70f0b17b9d0c8b9b651b for a way to calculate a match
        # for a given input ISBN
        
        # Crawfish Dreams by Nancy Rawles -- what could work once the LT thingisbn cache clears
        #isbn1 = '0385722133'
        #isbn2 = '0307425363'
        
        # RY switched to Atwood's Handmaid's Tale for hopefully longer term resilience for this test
        isbn1 = '9780395404256'
        isbn2 = '9780547345666'
        e1 = bookloader.add_by_isbn(isbn1)
        e2 = bookloader.add_by_isbn(isbn2)
        self.assertTrue(e1)
        self.assertTrue(e2)
        self.assertTrue(e1.work)
        self.assertTrue(e2.work)
        self.assertEqual(models.Work.objects.count(), 2)

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
        site = Site.objects.all()[0]
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
        c1=Campaign.objects.get(pk=c1.pk)
        c2=Campaign.objects.get(pk=c2.pk)

        self.assertEqual(c1.work, c2.work)
        self.assertEqual(user.wishlist.works.all().count(), 1)
        self.assertEqual(Comment.objects.for_model(w3).count(), 3)
        
        anon_client = Client()
        r = anon_client.get("/work/%s/" % w3.pk)
        self.assertEqual(r.status_code, 200)
        r = anon_client.get("/work/%s/" % e2.work.pk)
        self.assertEqual(r.status_code, 200)

    
    def test_ebook(self):
        edition = bookloader.add_by_oclc('1246014')
        self.assertEqual(edition.ebooks.count(), 2)
        #ebook_epub = edition.ebooks.all()[0]
        ebook_epub = edition.ebooks.filter(format='epub')[0]
        self.assertEqual(ebook_epub.format, 'epub')
        #self.assertEqual(ebook_epub.url, 'http://books.google.com/books/download/The_Latin_language.epub?id=N1RfAAAAMAAJ&ie=ISO-8859-1&output=epub&source=gbs_api')
        self.assertEqual(parse_qs(urlparse(ebook_epub.url).query).get("id"), ['N1RfAAAAMAAJ'])
        self.assertEqual(parse_qs(urlparse(ebook_epub.url).query).get("output"), ['epub'])
        self.assertEqual(ebook_epub.provider, 'Google Books')
        self.assertEqual(ebook_epub.set_provider(), 'Google Books')
        ebook_pdf = edition.ebooks.filter(format='pdf')[0]
        self.assertEqual(ebook_pdf.format, 'pdf')
        #self.assertEqual(ebook_pdf.url, 'http://books.google.com/books/download/The_Latin_language.pdf?id=N1RfAAAAMAAJ&ie=ISO-8859-1&output=pdf&sig=ACfU3U2yLt3nmTncB8ozxOWUc4iHKUznCA&source=gbs_api')
        self.assertEqual(parse_qs(urlparse(ebook_pdf.url).query).get("id"), ['N1RfAAAAMAAJ'])
        self.assertEqual(parse_qs(urlparse(ebook_pdf.url).query).get("output"), ['pdf'])
        self.assertEqual(ebook_pdf.provider, 'Google Books')        
        self.assertEqual(edition.public_domain, True)  

        w = edition.work
        self.assertEqual(w.first_epub().url, ebook_epub.url)
        self.assertEqual(w.first_pdf().url, ebook_pdf.url)
        self.assertEqual(w.first_epub_url(), ebook_epub.url)
        self.assertEqual(w.first_pdf_url(), ebook_pdf.url)

        ebook_pdf.url='http://en.wikisource.org/wiki/Frankenstein'      
        self.assertEqual(ebook_pdf.set_provider(), 'Wikisource')

        self.user.wishlist.add_work(w, 'test')        
        tasks.report_new_ebooks(date_today())
        r = self.client.get("/notification/" )
        self.assertEqual(r.status_code, 200)
        
        ebook_pdf.increment()
        updated_ebook = Ebook.objects.get(pk=ebook_pdf.pk)
        self.assertEqual(int(updated_ebook.download_count), 1)
        self.assertEqual(int(edition.work.download_count), 1)

    def test_add_no_ebook(self):
        # this edition lacks an ebook, but we should still be able to load it
        # http://books.google.com/books?id=D-WjL_HRbNQC&printsec=frontcover#v=onepage&q&f=false
        # Social Life of Information
        e = bookloader.add_by_isbn('1578517087')
        self.assertTrue(e)

    @unittest.expectedFailure
    def test_one_language(self):
        # english edition for cat's cradle should only pull in other 
        # english editions
        # expected failure right now because Google seems to have bad data about language of Cat's Cradle
        # e.g., https://www.googleapis.com/books/v1/volumes?q=isbn:9789513033774
        # title = "Kissan kehto" -- language according to API = English
        work = bookloader.add_by_isbn('079530272X').work
        self.assertEqual(work.language, 'en')
        bookloader.add_related('079530272X')
        for edition in work.editions.all():
            self.assertEqual(edition.title.lower(), "cat's cradle")

    def test_add_openlibrary(self):
        work = bookloader.add_by_isbn('0441007465').work
        bookloader.add_related('0441007465')
        bookloader.add_openlibrary(work)
        subjects = [s.name for s in work.subjects.all()]
        self.assertTrue(len(subjects) > 10)
        self.assertTrue('Science fiction' in subjects)
        self.assertTrue('/works/OL27258W' in work.identifiers.filter(type='olwk').values_list('value',flat=True) )
        self.assertTrue('888628' in work.identifiers.filter(type='gdrd').values_list('value',flat=True))
        self.assertTrue('609' in work.identifiers.filter(type='ltwk').values_list('value',flat=True))

    def test_unicode_openlibrary(self):
        work = bookloader.add_by_isbn('9783894808358').work
        bookloader.add_openlibrary(work)
        self.assertTrue(work.description.startswith('Sie sind jung,'))
        
    def test_load_gutenberg_edition(self):
        """Let's try this out for Moby Dick"""
        
        title = "Moby Dick"
        ol_work_id = "/works/OL102749W"
        gutenberg_etext_id = 2701
        epub_url = "http://www.gutenberg.org/cache/epub/2701/pg2701.epub"
        license = 'http://www.gutenberg.org/license'
        lang = 'en'
        format = 'epub'
        publication_date = datetime(2001,7,1)
        seed_isbn = '9780142000083' # http://www.amazon.com/Moby-Dick-Whale-Penguin-Classics-Deluxe/dp/0142000086
        
        ebook = bookloader.load_gutenberg_edition(title, gutenberg_etext_id, ol_work_id, seed_isbn, epub_url, format, license, lang, publication_date)
        self.assertEqual(ebook.url, epub_url)
        

class SearchTests(TestCase):

    def test_basic_search(self):
        results = search.gluejar_search('melville')
        self.assertEqual(len(results), 10)

        r = results[0]
        self.assertTrue(r.has_key('title'))
        self.assertTrue(r.has_key('author'))
        self.assertTrue(r.has_key('description'))
        self.assertTrue(r.has_key('cover_image_thumbnail'))
        self.assertTrue(r['cover_image_thumbnail'].startswith('https'))
        self.assertTrue(r.has_key('publisher'))
        self.assertTrue(r.has_key('isbn_13'))
        self.assertTrue(r.has_key('googlebooks_id'))

    def test_pagination(self):
        r1 = search.gluejar_search('melville', page=1)
        r2 = search.gluejar_search('melville', page=2)
        isbns1 = set([r['isbn_13'] for r in r1])
        isbns2 = set([r['isbn_13'] for r in r2])
        self.assertTrue(isbns1 != isbns2)

    def test_googlebooks_search(self):
        response = search.googlebooks_search('melville', '69.243.24.29', 1)
        self.assertEqual(len(response['items']), 10)


class CampaignTests(TestCase):

    def test_b2u(self):
        w = Work()
        w.save()
        c = Campaign(
            target=D('12000.00'), 
            deadline=datetime(2013, 1, 1), 
            work=w, type=2, 
            cc_date_initial=datetime(2113, 1, 1),
            )
        self.assertTrue(c.set_dollar_per_day()<0.34)
        self.assertTrue(c.dollar_per_day>0.31)
        c._current_total = D(6000.1)
        c.status = 'ACTIVE'
        c.save()
        c.update_left()
        #print(w.percent_of_goal())
        self.assertEqual(w.percent_unglued(),3)
        self.assertTrue(w.percent_of_goal()>49)
        ofr = Offer.objects.create(work=w,price=D(10),active=True)
        self.assertTrue(c.days_per_copy <D(32.26))
        self.assertTrue(c.days_per_copy >D(29.41))

    def test_required_fields(self):
        # a campaign must have a target, deadline and a work

        c = Campaign()
        self.assertRaises(IntegrityError, c.save)

        c = Campaign(target=D('1000.00'))
        self.assertRaises(IntegrityError, c.save)

        c = Campaign(target=D('1000.00'), deadline=datetime(2013, 1, 1))
        self.assertRaises(IntegrityError, c.save)

        w = Work()
        w.save()
        c = Campaign(target=D('1000.00'), deadline=datetime(2013, 1, 1), work=w)
        c.license = 'CC BY-NC'
        c.save()
        self.assertEqual(c.license_url, 'http://creativecommons.org/licenses/by-nc/3.0/')
        self.assertEqual(c.license_badge, 'https://i.creativecommons.org/l/by-nc/3.0/88x31.png')
        
    def test_campaign_status(self):
        
        # need a user to associate with a transaction
        user = User.objects.create_user('test', 'test@example.org', 'testpass')
        
        w = Work()
        w.save()
        w2 = Work()
        w2.save()
        # INITIALIZED
        c1 = Campaign(target=D('1000.00'),deadline=Campaign.latest_ending(),work=w)
        c1.save()
        self.assertEqual(c1.status, 'INITIALIZED')
        # ACTIVATED
        c2 = Campaign(target=D('1000.00'),deadline=datetime(2013,1,1),work=w)
        c2.save()
        self.assertEqual(c2.status, 'INITIALIZED')
        u = User.objects.create_user('claimer', 'claimer@example.org', 'claimer')
        u.save()
        rh = RightsHolder(owner = u, rights_holder_name = 'rights holder name')
        rh.save()
        cl = Claim(rights_holder = rh, work = w, user = u, status = 'active')
        cl.save()
        cl2 = Claim(rights_holder = rh, work = w2, user = u, status = 'active')
        cl2.save()
        c2.activate()
        self.assertEqual(c2.status, 'ACTIVE')
        # SUSPENDED
        c2.suspend(reason="for testing")
        self.assertEqual(c2.status, 'SUSPENDED')
        # RESUMING
        c2.resume(reason="for testing")
        #self.assertEqual(c2.suspended, None)
        self.assertEqual(c2.status,'ACTIVE')
        # should not let me suspend a campaign that hasn't been initialized
        self.assertRaises(UnglueitError, c1.suspend, "for testing")
        # UNSUCCESSFUL
        c3 = Campaign(target=D('1000.00'),deadline=now() - timedelta(days=1),work=w2)
        c3.save()
        c3.activate()
        self.assertEqual(c3.status, 'ACTIVE')
        # at this point, since the deadline has passed, the status should change and be UNSUCCESSFUL
        self.assertTrue(c3.update_status())
        self.assertEqual(c3.status, 'UNSUCCESSFUL')
        
        # premiums
        pr1= Premium(type='CU', campaign=c3, amount=10, description='botsnack', limit=1)
        pr1.save()
        self.assertEqual(pr1.premium_remaining,1)
        
        #cloning (note we changed c3 to w2 to make it clonable)
        c7= c3.clone()
        self.assertEqual(c7.status, 'INITIALIZED')
        self.assertEqual(c7.premiums.all()[0].description , 'botsnack')
        
        
        # SUCCESSFUL
        c4 = Campaign(target=D('1000.00'),deadline=now() - timedelta(days=1),work=w)
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
        c5 = Campaign(target=D('1000.00'),deadline=datetime(2013,1,1),work=w)
        c5.save()
        c5.activate().withdraw('testing')
        self.assertEqual(c5.status, 'WITHDRAWN')     

        # testing percent-of-goal
        w2 = Work()
        w2.save()
        c6 = Campaign(target=D('1000.00'),deadline=now() + timedelta(days=1),work=w2)
        c6.save()
        cl = Claim(rights_holder = rh, work = w2, user = u, status = 'active')
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
        
        self.assertEqual(c1.launchable, True)
        c1.work.create_offers()
        self.assertEqual(c1.work.offers.count(), 2)
        self.assertEqual(c1.work.offers.filter(license=2).count(), 1)
        c1.type = 2
        c1.save()
        self.assertEqual(c1.launchable, False)
        of1=c1.work.offers.get(license=2)
        of1.price=D(2)
        of1.active=True
        of1.save()
        self.assertEqual(c1.launchable, False)
        e1= models.Edition(title="title",work=c1.work)
        e1.save()
        ebf1= models.EbookFile(edition=e1, format=1)
        ebf1.save()
        c1.set_cc_date_initial()
        self.assertEqual(c1.cc_date, settings.MAX_CC_DATE)
        c1.target = D(settings.UNGLUEIT_MAXIMUM_TARGET)
        c1.save()
        self.assertEqual(c1.launchable, True)

class WishlistTest(TestCase):

    def test_add_remove(self):
        # add a work to a user's wishlist
        user = User.objects.create_user('test', 'test@example.org', 'testpass')
        edition = bookloader.add_by_isbn('0441007465')
        work = edition.work
        num_wishes=work.num_wishes
        user.wishlist.add_work(work, 'test')
        self.assertEqual(user.wishlist.works.count(), 1)
        self.assertEqual(work.num_wishes, num_wishes+1)
        user.wishlist.remove_work(work)
        self.assertEqual(user.wishlist.works.count(), 0)
        self.assertEqual(work.num_wishes, num_wishes)
        
class CeleryTaskTest(TestCase):

    def test_single_fac(self):
        n = 10
        task = tasks.fac.delay(n)
        result = task.get(timeout=10)
        self.assertEqual(result,factorial(n))

    def test_subtask(self):
        n = 30
        subtasks = [tasks.fac.subtask(args=(x,)) for x in range(n)]
        job = TaskSet(tasks=subtasks)
        result = job.apply_async()
        while not result.ready():
            sleep(0.2)
        self.assertEqual(result.join(),[factorial(x) for x in range(n)])
    
class GoodreadsTest(TestCase):

    def test_goodreads_shelves(self):
        # test to see whether the core undeletable shelves are on the list
        gr_uid = "767708"  # for Raymond Yee
        gc = goodreads.GoodreadsClient(key=settings.GOODREADS_API_KEY, secret=settings.GOODREADS_API_SECRET)
        shelves = gc.shelves_list(gr_uid)
        shelf_names = [s['name'] for s in shelves['user_shelves']]
        self.assertTrue('currently-reading' in shelf_names)
        self.assertTrue('read' in shelf_names)
        self.assertTrue('to-read' in shelf_names)

    def test_review_list_unauth(self):
        gr_uid = "767708"  # for Raymond Yee
        gc = goodreads.GoodreadsClient(key=settings.GOODREADS_API_KEY, secret=settings.GOODREADS_API_SECRET)
        reviews = gc.review_list_unauth(user_id=gr_uid, shelf='read')
        # test to see whether there is a book field in each of the review
        # url for test is http://www.goodreads.com/review/list.xml?id=767708&shelf=read&page=1&per_page=20&order=a&v=2&key=[key]
        self.assertTrue(all([r.has_key("book") for r in reviews]))

class LibraryThingTest(TestCase):

    def test_scrape_test_lib(self):
        # account yujx : has one book: 0471925675
        lt_username = 'yujx'
        lt = librarything.LibraryThing(username=lt_username)
        books = list(lt.parse_user_catalog(view_style=5))
        self.assertEqual(len(books),1)
        self.assertEqual(books[0]['isbn'], '0471925675')
        self.assertEqual(books[0]['work_id'], '80826')
        self.assertEqual(books[0]['book_id'], '79883733')

class ISBNTest(TestCase):

    def test_ISBN(self):
        milosz_10 = '006019667X'
        milosz_13 = '9780060196677'
        python_10 = '0-672-32978-6'
        python_10_wrong = '0-672-32978-7'
        python_13 = '978-0-672-32978-4'
        
        isbn_python_10 = isbn.ISBN(python_10)
        isbn_python_13 = isbn.ISBN(python_13)
        # return None for invalid characters
        self.assertEqual(None, isbn.ISBN("978-0-M72-32978-X").to_string('13'))
        self.assertEqual(isbn.ISBN("978-0-M72-32978-X").valid, False)
        # check that only ISBN 13 starting with 978 or 979 are accepted
        self.assertEqual(None, isbn.ISBN("111-0-M72-32978-X").to_string())
        
        # right type?
        self.assertEqual(isbn_python_10.type, '10')
        self.assertEqual(isbn_python_13.type, '13')
        # valid?
        self.assertEqual(isbn_python_10.valid, True)
        self.assertEqual(isbn.ISBN(python_10_wrong).valid, False)
        
        # do conversion -- first the outside methods
        self.assertEqual(isbn.convert_10_to_13(isbn.strip(python_10)),isbn.strip(python_13))
        self.assertEqual(isbn.convert_13_to_10(isbn.strip(python_13)),isbn.strip(python_10))
        
        # check formatting
        self.assertEqual(isbn.ISBN(python_13).to_string(type='13'), '9780672329784')
        self.assertEqual(isbn.ISBN(python_13).to_string('13',True), '978-0-672-32978-4')
        self.assertEqual(isbn.ISBN(python_13).to_string(type='10'), '0672329786')
        self.assertEqual(isbn.ISBN(python_10).to_string(type='13'), '9780672329784')
        self.assertEqual(isbn.ISBN(python_10).to_string(10,True), '0-672-32978-6')
        
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
        self.assertEqual(len(set([isbn.ISBN(milosz_10), isbn.ISBN(milosz_13)])),2)
        self.assertEqual(len(set([str(isbn.ISBN(milosz_10)), str(isbn.ISBN(milosz_13))])),2)
        self.assertEqual(len(set([isbn.ISBN(milosz_10).to_string(), isbn.ISBN(milosz_13).to_string()])),1)

class EncryptedKeyTest(TestCase):
    def test_create_read_key(self):
        name = "the great answer"
        value = "42"
        key = Key.objects.create(name=name, value=value)
        key.save()
        # do we get back the value?
        self.assertEqual(Key.objects.filter(name=name)[0].value, value)
        # just checking that the encrypted value is not the same as the value
        self.assertNotEqual(key.encrypted_value, value)  # is this always true?
        
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
        self.assertRaises(Http404, safe_get_work, 3)
        
class DownloadPageTest(TestCase):
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
        eb1.url = "http://example.org"
        eb1.edition = e1
        eb1.format = 'epub'
        
        eb2 = models.Ebook()
        eb2.url = "http://example2.com"
        eb2.edition = e2
        eb2.format = 'mobi'
        
        eb1.save()
        eb2.save()
        
        anon_client = Client()
        response = anon_client.get("/work/%s/download/" % w.id, follow=True)
        self.assertContains(response, "/download_ebook/%s/"% eb1.id, count=10) 
        self.assertContains(response, "/download_ebook/%s/"% eb2.id, count=4)


class LocaldatetimeTest(TestCase):
    @override_settings(LOCALDATETIME_NOW=None)
    def test_LOCALDATETIME_NOW_none(self):
        
        try:
            localdatetime.now
        except NameError:
            from regluit.utils import localdatetime
        else:
            reload(localdatetime)
            
        self.assertAlmostEqual(mktime(datetime.now().timetuple()), mktime(localdatetime.now().timetuple()), 1.0)
        
    @override_settings(LOCALDATETIME_NOW=lambda : datetime.now() + timedelta(365))
    def test_LOCALDATETIME_NOW_year_ahead(self):
                
        try:
            localdatetime.now
        except NameError:
            from regluit.utils import localdatetime
        else:
            reload(localdatetime)
            
        self.assertAlmostEqual(mktime((datetime.now() + timedelta(365)).timetuple()), mktime(localdatetime.now().timetuple()), 1.0)
        
    def test_no_time_override(self):

        from regluit.utils import localdatetime
        self.assertAlmostEqual(mktime(datetime.now().timetuple()), mktime(localdatetime.now().timetuple()), 1.0)
    
    def tearDown(self):
        # restore localdatetime.now() to what's in the settings file
        try:
            localdatetime.now
        except NameError:
            from regluit.utils import localdatetime
        else:
            reload(localdatetime)
        
class MailingListTests(TestCase):
    #mostly to check that MailChimp account is setp correctly

    def test_mailchimp(self):
        from postmonkey import PostMonkey
        pm = PostMonkey(settings.MAILCHIMP_API_KEY)
        self.assertEqual(pm.ping(),"Everything's Chimpy!" )
        self.user = User.objects.create_user('chimp_test', 'eric@gluejar.com', 'chimp_test')
        self.assertTrue(self.user.profile.on_ml)

class EbookFileTests(TestCase):

    def test_ebookfile(self):
        """
        Read the test epub file
        """
        w = Work.objects.create(title="Work 1")
        e = Edition.objects.create(title=w.title,work=w)
        u = User.objects.create_user('test', 'test@example.org', 'testpass')
        c = Campaign.objects.create(work=w, type = parameters.BUY2UNGLUE, cc_date_initial= datetime(2020,1,1),target=1000, deadline=datetime(2020,1,1))
        
        # download the test epub into a temp file
        temp = NamedTemporaryFile(delete=False)
        test_file_content = requests.get(settings.BOOXTREAM_TEST_EPUB_URL).content
        
        temp.write(test_file_content)
        temp.close()
        
        try:
            # now we can try putting the test epub file into Django storage
            temp_file = open(temp.name)
                
            dj_file = DjangoFile(temp_file)
            ebf = EbookFile( format='epub', edition=e, file=dj_file)
            ebf.save()
                
            temp_file.close()
        finally:
            # make sure we get rid of temp file
            os.remove(temp.name)
            
        test_epub= EPUB(ebf.file, mode='a')
        self.assertEqual(len(test_epub.opf) , 4)
        self.assertTrue(len(test_epub.opf[2]) < 30) 
        
        acq=Acq.objects.create(user=u,work=w,license=TESTING)
        self.assertIsNot(acq.nonce, None)

        url= acq.get_watermarked().download_link_epub
        self.assertRegexpMatches(url,'download.booxtream.com/')
        print url

        
        
