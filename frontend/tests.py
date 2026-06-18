#external library imports
import re
import mimetypes

#django imports
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

#regluit imports
from regluit.core.models import Work, RightsHolder, Claim, Subject

class WishlistTests(TestCase):
    fixtures = ['initial_data.json', 'neuromancer.json']
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@example.org', 'test')
        self.client = Client()
        self.client.login(username='test', password='test')

    def test_add_remove(self):
        # add a book to the wishlist
        r = self.client.post("/wishlist/", {"googlebooks_id": "IDFfMPW32hQC"},
                HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.user.wishlist.works.all().count(), 1)
        wished = self.user.wishlist.works.first()
        # test the work page
        r = self.client.get("/work/%s/" % wished.id)
        self.assertEqual(r.status_code, 200)
        anon_client = Client()
        r = anon_client.get("/work/%s/" % wished.id)
        self.assertEqual(r.status_code, 200)

        # remove the book
        r = self.client.post("/wishlist/", {"remove_work_id": wished.id},
                HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(self.user.wishlist.works.all().count(), 0)

class RhPageTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('test', 'test@example.org', 'test')
        self.rh_user =  User.objects.create_user('rh', 'rh@example.org', 'test')
        self.staff_user =  User.objects.create_superuser('staff', 'staff@example.org', 'test')
        self.work = Work.objects.create(title="test work", language='en')
        rh = RightsHolder.objects.create(rights_holder_name='test', owner=self.rh_user)
        Claim.objects.create(work=self.work, user=self.rh_user, status='active', rights_holder=rh)
        self.kw = Subject.objects.create(name="Fiction")

    def test_anonymous(self):
        anon_client = Client()
        r = anon_client.get("/work/{}/".format(self.work.id))
        r = anon_client.head("/work/{}/".format(self.work.id))
        self.assertEqual(r.status_code, 200)
        csrfmatch =  re.search("name='csrfmiddlewaretoken' value='([^']*)'", str(r.content, 'utf-8'))
        self.assertFalse(csrfmatch)
        r = anon_client.post("/work/{}/kw/".format(self.work.id))
        self.assertEqual(r.status_code, 302)

    def can_edit(self, client, can=True):
        r = client.get("/work/{}/".format(self.work.id))
        self.assertEqual(r.status_code, 200)
        csrfmatch =  re.search("name='csrfmiddlewaretoken' value='([^']*)'", str(r.content, 'utf-8'))
        self.assertTrue(csrfmatch)
        csrf = csrfmatch.group(1)
        r = client.post("/work/{}/kw/".format(self.work.id), {
                'csrfmiddlewaretoken': csrf,
                'kw_add':'true',
                'add_kw_0':'Fiction',
                'add_kw_1':self.kw.id
            })
        if can:
            self.assertEqual(r.content, b'Fiction')
        else:
            self.assertEqual(r.content, b'true')
        r = client.post("/work/{}/kw/".format(self.work.id), {
                'csrfmiddlewaretoken': csrf,
                'remove_kw' : 'Fiction'
            })
        if can:
            self.assertEqual(r.content, b'removed Fiction')
        else:
            self.assertEqual(r.content, b'False')

    def test_user(self):
        # test non-RightsHolder
        client = Client()
        client.login(username='test', password='test')
        self.can_edit(client, can=False)

    def test_rh(self):
        # test RightsHolder
        client = Client()
        client.login(username='rh', password='test')
        self.can_edit(client)

    def test_staff(self):
        client = Client()
        client.login(username='staff', password='test')
        self.can_edit(client)


class PageTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('test', 'test@example.org', 'test')
        User.objects.create_user('test_other', 'test@example.org', 'test_other')
        self.client = Client()
        self.client.login(username='test', password='test')
        w = Work.objects.create(title="test work", language='en')

    def test_setttings(self):
        self.assertEqual(mimetypes.guess_type('/whatever/my_file.epub')[0], 'application/epub+zip')

    def test_view_by_self(self):
        # logged in
        r = self.client.get("/supporter/test/")
        self.assertEqual(r.status_code, 200)
        r = self.client.get("/search/?q=sverige")
        self.assertEqual(r.status_code, 200)
        r = self.client.get("/search/?q=sverige&page=2")
        self.assertEqual(r.status_code, 200)
        r = self.client.get("/notification/settings/")
        self.assertEqual(r.status_code, 200)

    def test_view_by_other(self):
        # someone else's supporter page
        r = self.client.get("/supporter/test_other/")
        self.assertEqual(r.status_code, 200)

    def test_view_by_anonymous(self):
        # not logged in
        anon_client = Client()
        r = anon_client.get("/supporter/test/")
        self.assertEqual(r.status_code, 200)
        r = anon_client.get("/")
        self.assertEqual(r.status_code, 200)
        r = anon_client.get("/search/?q=sverige")
        self.assertEqual(r.status_code, 200)
        r = anon_client.get("/search/?q=sverige&page=2")
        self.assertEqual(r.status_code, 200)
        r = anon_client.get("/info/metrics.html")
        self.assertEqual(r.status_code, 200)
        r = anon_client.get("/marc/")
        self.assertEqual(r.status_code, 200)
        r = anon_client.get("/creativecommons/?order_by=popular")
        self.assertEqual(r.status_code, 200)
        r = anon_client.get("/creativecommons/by")
        self.assertEqual(r.status_code, 200)
        r = anon_client.get("/free/by-nc/?order_by=title")
        self.assertEqual(r.status_code, 200)
        r = anon_client.get("/free/epub/gfdl/")
        self.assertEqual(r.status_code, 200)

class AllFacetAliasTests(TestCase):
    fixtures = ['initial_data.json', 'neuromancer.json']

    def test_all_keyword_alias_matches_keyword_path(self):
        plain = self.client.get("/free/kw.Fiction/?order_by=newest")
        alias = self.client.get("/free/all/kw.Fiction/?order_by=newest")
        self.assertEqual(plain.status_code, 200)
        self.assertEqual(alias.status_code, 200)

    def test_all_non_keyword_alias_matches_compound_path(self):
        plain = self.client.get("/free/epub/doab/?order_by=newest")
        alias = self.client.get("/free/all/epub/doab/?order_by=newest")
        self.assertEqual(plain.status_code, 200)
        self.assertEqual(alias.status_code, 200)

class FacetIsolationTests(TestCase):
    """Tests for #1110: keyword/subject facets cannot combine with other facets."""
    fixtures = ['initial_data.json', 'neuromancer.json']

    def test_base_free_page_offers_keywords(self):
        """The base /free/ page should offer keyword facets in the sidebar."""
        r = self.client.get("/free/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Keyword")

    def test_keyword_page_no_refine_sidebar(self):
        """A keyword facet page should NOT offer further facet refinement."""
        r = self.client.get("/free/kw.Fiction/")
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, "Show me only")

    def test_non_keyword_page_excludes_keywords(self):
        """A non-keyword facet page should offer refinement but NOT keywords."""
        r = self.client.get("/free/epub/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Show me only")
        self.assertNotContains(r, "Keyword")

    def test_single_keyword_still_works(self):
        r = self.client.get("/free/kw.Fiction/")
        self.assertEqual(r.status_code, 200)

    def test_keyword_compound_returns_404(self):
        r = self.client.get("/free/kw.Fiction/epub/")
        self.assertEqual(r.status_code, 404)

    def test_keyword_compound_reversed_returns_404(self):
        r = self.client.get("/free/epub/kw.Fiction/")
        self.assertEqual(r.status_code, 404)

    def test_keyword_with_all_prefix_still_works(self):
        r = self.client.get("/free/all/kw.Fiction/")
        self.assertEqual(r.status_code, 200)

    def test_non_keyword_compound_still_works(self):
        r = self.client.get("/free/epub/doab/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "EPUB format")
        self.assertContains(r, "Directory of Open Access Books")

class GoogleBooksTest(TestCase):
    fixtures = ['initial_data.json', 'neuromancer.json']
    def test_googlebooks_id(self):
        r = self.client.get("/googlebooks/IDFfMPW32hQC/")
        self.assertEqual(r.status_code, 302)
        work_url = r['location']
        self.assertTrue(re.match(r'.*/work/\d+/$', work_url))


# --- #1125 ownership regression (authored 2026-06-18; verify locally) ---------
from unittest.mock import patch as _patch
from django.test import TestCase as _TestCase, Client as _Client
from django.urls import reverse as _reverse
from django.contrib.auth.models import User as _User
from payment.models import Transaction as _Transaction
from payment.parameters import PAYMENT_HOST_NONE as _PAYMENT_HOST_NONE


class FundViewOwnershipTest(_TestCase):
    """Regression for #1125 hardening: a no-campaign transaction owned by a user
    must NOT be payable by anyone else. Otherwise (now that FundView passes
    transaction.user into make_account) an anonymous or different requester could
    take over the transaction and mutate the owner's Stripe account /
    recharge_failed_transactions(). The guard must return pledge_user_error.html
    BEFORE PaymentManager.charge() is called."""

    def setUp(self):
        self.owner = _User.objects.create_user('owner1125', 'owner1125@example.org', 'pw')
        self.other = _User.objects.create_user('other1125', 'other1125@example.org', 'pw')
        self.txn = _Transaction.create(amount=5.00, max_amount=5.00,
                                       host=_PAYMENT_HOST_NONE, user=self.owner, campaign=None)

    @_patch('frontend.views.PaymentManager')
    def test_anonymous_cannot_pay_owned_transaction(self, mock_pm):
        r = _Client().post(_reverse('fund', args=[self.txn.id]), {'stripe_token': 'tok_test'})
        self.assertTemplateUsed(r, 'pledge_user_error.html')
        mock_pm.return_value.charge.assert_not_called()

    @_patch('frontend.views.PaymentManager')
    def test_other_user_cannot_pay_owned_transaction(self, mock_pm):
        c = _Client()
        c.login(username='other1125', password='pw')
        r = c.post(_reverse('fund', args=[self.txn.id]),
                   {'stripe_token': 'tok_test', 'username': 'other1125'})
        self.assertTemplateUsed(r, 'pledge_user_error.html')
        mock_pm.return_value.charge.assert_not_called()
