from decimal import Decimal as D
from datetime import datetime, timedelta

from django.test import TestCase
from django.utils import unittest
from django.db import IntegrityError
from django.contrib.auth.models import User

from regluit.payment.models import Transaction
from regluit.core.models import Campaign, Work, UnglueitError
from regluit.core import bookloader, models, search
from regluit.payment.parameters import PAYMENT_TYPE_AUTHORIZATION


class TestBookLoader(TestCase):

    def test_add_book(self):
        # edition
        edition = bookloader.add_by_isbn('0441012035')
        self.assertEqual(edition.title, 'Neuromancer')
        self.assertEqual(edition.publication_date, '2004')
        self.assertEqual(edition.publisher, 'Ace Books')
        self.assertEqual(edition.isbn_10, '0441012035')
        self.assertEqual(edition.isbn_13, '9780441012039')
        self.assertEqual(edition.googlebooks_id, "2NyiPwAACAAJ")
        self.assertEqual(edition.language, "en")

        # subjects
        subject_names = [subject.name for subject in edition.subjects.all()]
        self.assertEqual(len(subject_names), 11)
        self.assertTrue('Japan' in subject_names)

        # authors
        self.assertEqual(edition.authors.all().count(), 1)
        self.assertEqual(edition.authors.all()[0].name, 'William Gibson')

        # work
        self.assertTrue(edition.work)

    def test_double_add(self):
        bookloader.add_by_isbn('0441012035')
        bookloader.add_by_isbn('0441012035')
        self.assertEqual(models.Edition.objects.all().count(), 1)
        self.assertEqual(models.Author.objects.all().count(), 1)
        self.assertEqual(models.Work.objects.all().count(), 1)
        self.assertEqual(models.Subject.objects.all().count(), 11)
       
    def test_missing_isbn(self):
        e = bookloader.add_by_isbn('0139391401')
        self.assertEqual(e, None)

    def test_thingisbn(self):
        isbns = bookloader.thingisbn('0441012035')
        self.assertTrue(len(isbns) > 20)
        self.assertTrue('0441012035' in isbns)
        self.assertTrue('3453313895' in isbns)

    def test_add_related(self):
        # add one edition
        edition = bookloader.add_by_isbn('0441012035')
        self.assertEqual(models.Edition.objects.count(), 1)
        self.assertEqual(models.Work.objects.count(), 1)
    
        # ask for related editions to be added using the work we just created
        bookloader.add_related('0441012035')
        self.assertTrue(models.Edition.objects.count() > 20)
        self.assertEqual(models.Work.objects.count(), 1)
        self.assertTrue(edition.work.editions.count() > 20)

class SearchTests(TestCase):

    def test_basic_search(self):
        results = search.gluejar_search('melville')
        self.assertEqual(len(results), 10)

        r = results[0]
        self.assertTrue(r.has_key('title'))
        self.assertTrue(r.has_key('author'))
        self.assertTrue(r.has_key('description'))
        self.assertTrue(r.has_key('image'))
        self.assertTrue(r.has_key('publisher'))
        self.assertTrue(r.has_key('isbn_10'))
        self.assertTrue(r.has_key('googlebooks_id'))

    def test_googlebooks_search(self):
        response = search.googlebooks_search('melville')
        self.assertEqual(len(response['items']), 10)


class CampaignTests(TestCase):

    def test_required_fields(self):
        # a campaign must have a target, deadline and a work

        c = Campaign()
        self.assertRaises(IntegrityError, c.save)

        c = Campaign(target=D('1000.00'))
        self.assertRaises(IntegrityError, c.save)

        c = Campaign(target=D('1000.00'), deadline=datetime(2012, 1, 1))
        self.assertRaises(IntegrityError, c.save)

        w = Work()
        w.save()
        c = Campaign(target=D('1000.00'), deadline=datetime(2012, 1, 1), work=w)
        c.save()

    def test_campaign_status(self):
        w = Work()
        w.save()
        # INITIALIZED
        c1 = Campaign(target=D('1000.00'),deadline=datetime(2012,1,1),work=w)
        c1.save()
        self.assertEqual(c1.status, 'INITIALIZED')
        # ACTIVATED
        c2 = Campaign(target=D('1000.00'),deadline=datetime(2012,1,1),work=w)
        c2.save()
        self.assertEqual(c2.status, 'INITIALIZED')
        c2.activate()
        self.assertEqual(c2.status, 'ACTIVE')
        # SUSPENDED
        c2.suspend(reason="for testing")
        self.assertEqual(c2.status, 'SUSPENDED')
        # RESUMING
        c2.resume()
        self.assertEqual(c2.suspended, None)
        self.assertEqual(c2.status,'ACTIVE')
        # should not let me suspend a campaign that hasn't been initialized
        self.assertRaises(UnglueitError, c1.suspend, "for testing")
        # UNSUCCESSFUL
        c3 = Campaign(target=D('1000.00'),deadline=datetime.utcnow() - timedelta(days=1),work=w)
        c3.save()
        c3.activate()
        self.assertEqual(c3.status, 'UNSUCCESSFUL')
        # SUCCESSFUL
        c4 = Campaign(target=D('1000.00'),deadline=datetime.utcnow() - timedelta(days=1),work=w)
        c4.save()
        c4.activate()
        
        t = Transaction()
        t.amount = D('1234.00')
        t.type = PAYMENT_TYPE_AUTHORIZATION
        t.status = 'ACTIVE'
        t.campaign = c4
        t.save()        
        self.assertEqual(c4.status, 'SUCCESSFUL')
        
        # ACTIVE
        c4.deadline = datetime.utcnow() + timedelta(days=1)
        c4.save()
        self.assertEqual(c4.status, 'ACTIVE')
        
        # WITHDRAWN
        c5 = Campaign(target=D('1000.00'),deadline=datetime(2012,1,1),work=w)
        c5.save()
        c5.activate().withdraw('testing')
        self.assertEqual(c5.status, 'WITHDRAWN')        


<<<<<<< HEAD
class SettingsTest(TestCase):
    
    def test_dev_me_alignment(self):
        from regluit.settings import me, dev
        self.assertEqual(set(me.__dict__.keys()) ^ set(dev.__dict__.keys()), set([]))
        
    def test_prod_me_alignment(self):
        from regluit.settings import me, prod
        self.assertEqual(set(me.__dict__.keys()) ^ set(prod.__dict__.keys()), set([]))
        

class WishlistTest(TestCase):

    def test_add_remove(self):
        # add a work to a user's wishlist
        user = User.objects.create_user('test', 'test@example.com', 'testpass')
        edition = bookloader.add_by_isbn('0441012035')
        work = edition.work
        user.wishlist.works.add(work)
        self.assertEqual(user.wishlist.works.count(), 1)
        user.wishlist.works.remove(work)
        self.assertEqual(user.wishlist.works.count(), 0)

class SettingsTest(TestCase):
    
    def test_dev_me_alignment(self):
        from regluit.settings import me, dev
        self.assertEqual(set(me.__dict__.keys()) ^ set(dev.__dict__.keys()), set([]))
        
    def test_prod_me_alignment(self):
        from regluit.settings import me, prod
        self.assertEqual(set(me.__dict__.keys()) ^ set(prod.__dict__.keys()), set([]))
        
def suite():

    testcases = [TestBookLoader, SearchTests, CampaignTests, WishlistTest]
    suites = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(testcase) for testcase in testcases])
    suites.addTest(SettingsTest('test_dev_me_alignment'))  # leave out alignment with prod test right now
    return suites         
        
