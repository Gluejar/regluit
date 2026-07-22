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



from django.test import SimpleTestCase
from django.template import Template, Context
from regluit.utils.html import sanitize_html


class SanitizeRichTextTests(SimpleTestCase):
    """Server-side sanitization of CKEditor rich text (security-private#26)."""

    def test_strips_script(self):
        self.assertEqual(sanitize_html('<script>alert(1)</script>hi'), 'hi')

    def test_strips_event_handlers(self):
        self.assertNotIn('onerror', sanitize_html(
            '<img src="https://s3/c.jpg" alt="c" onerror="alert(1)">'))

    def test_strips_javascript_url(self):
        self.assertNotIn('javascript:', sanitize_html(
            '<a href="javascript:alert(1)">x</a>'))

    def test_keeps_allowed_formatting(self):
        out = sanitize_html('<p>Hello <strong>world</strong> <em>ok</em></p>'
                            '<blockquote>q</blockquote><ul><li>a</li></ul>')
        for frag in ('<strong>world</strong>', '<em>ok</em>',
                     '<blockquote>q</blockquote>', '<li>a</li>'):
            self.assertIn(frag, out)

    def test_keeps_safe_links_and_images(self):
        out = sanitize_html('<a href="https://x.com">l</a>'
                            '<img src="https://s3/c.jpg" alt="c">')
        self.assertIn('href="https://x.com"', out)
        self.assertIn('src="https://s3/c.jpg"', out)

    def test_none_passthrough(self):
        self.assertIsNone(sanitize_html(None))

    def test_template_filter_strips_and_marks_safe(self):
        rendered = Template(
            '{% load sanitizer %}{{ body|sanitize }}'
        ).render(Context({'body': '<b>ok</b><script>alert(1)</script>'}))
        self.assertIn('<b>ok</b>', rendered)
        self.assertNotIn('<script>', rendered)  # not escaped, actually removed
        self.assertNotIn('&lt;script&gt;', rendered)
class FeedbackSelfLinkTests(TestCase):
    """Regression: the feedback page must not link back to itself with a
    ?page=<current-url> parameter. That self-reference (emitted by the base
    template's footer/nav on every page, including /feedback/ itself) created
    an infinite, self-encoding URL space that crawler fleets walked at tens of
    thousands of requests per hour on 2026-07-10, saturating the web workers.
    See INCIDENT_2026-07-10_crawler_trap_flood.md."""

    def test_feedback_page_has_no_self_referencing_link(self):
        r = Client().get("/feedback/")
        self.assertEqual(r.status_code, 200)
        self.assertNotIn("/feedback/?page=", str(r.content, 'utf-8'))

    def test_feedback_page_with_page_param_has_no_self_referencing_link(self):
        # Even a crawler-style request that already carries an encoded
        # feedback URL must not be handed a deeper level of nesting.
        r = Client().get("/feedback/", {"page": "https://testserver/feedback/?page=x"})
        self.assertEqual(r.status_code, 200)
        # Assert on hrefs specifically: the form legitimately echoes the
        # incoming page value in a hidden field / subject line, but no LINK
        # (the crawlable surface) may carry a parameterized feedback URL.
        self.assertNotIn('href="/feedback/?page=', str(r.content, 'utf-8'))

    def test_other_pages_carry_exact_current_url(self):
        # The footer feedback link on non-feedback pages must embed the exact
        # current URL (urlencoded) so the form records where the user came from.
        from urllib.parse import quote
        r = Client().get("/privacy/")
        self.assertEqual(r.status_code, 200)
        content = str(r.content, 'utf-8')
        self.assertIn("/feedback/?page=", content)
        self.assertIn(quote("http://testserver/privacy/", safe=''), content)

    def test_pagination_state_is_preserved_in_recorded_url(self):
        # A page= query parameter on a non-feedback page is legitimate
        # pagination state and must survive into the recorded URL
        # (regression guard: an earlier draft of this fix stripped it).
        from urllib.parse import quote
        r = Client().get("/privacy/", {"q": "sverige", "page": "2"})
        self.assertEqual(r.status_code, 200)
        content = str(r.content, 'utf-8')
        self.assertIn(quote("page=2", safe=''), content)
        self.assertIn(quote("q=sverige", safe=''), content)

    def test_feedback_login_chain_reaches_fixed_point(self):
        # Codex round-2 finding: on /feedback/ the Sign In link's ?next=
        # embedded the full feedback URL, so a crawler alternating
        # feedback -> superlogin -> feedback -> superlogin got ever-growing
        # URLs. With auth_next using the bare path on the feedback route,
        # the chain must reach a fixed point instead.
        import re
        c = Client()

        def signin_href(html):
            m = re.search(r'href="(/accounts/superlogin/\?next=[^"]*)"', html)
            self.assertIsNotNone(m, "no sign-in link found")
            return m.group(1)

        def feedback_href(html):
            m = re.search(r'href="(/feedback/[^"]*)"', html)
            self.assertIsNotNone(m, "no feedback link found")
            return m.group(1)

        url = "/feedback/?page=https%3A%2F%2Ftestserver%2Fwork%2F1%2F"
        seen = set()
        for _ in range(4):
            r = c.get(url)
            self.assertEqual(r.status_code, 200)
            html = str(r.content, 'utf-8')
            login = signin_href(html)
            # next must be the bare feedback path, never a growing URL
            self.assertEqual(login, "/accounts/superlogin/?next=%2Ffeedback%2F")
            r2 = c.get(login)
            self.assertEqual(r2.status_code, 200)
            url = feedback_href(str(r2.content, 'utf-8'))
            self.assertLess(len(url), 300, "chain URL should not grow")
            if url in seen:
                break
            seen.add(url)
        else:
            self.fail("feedback/login chain did not reach a fixed point in 4 rounds")

    def test_feedback_url_tag_without_request_in_context(self):
        # Rendering outside a request cycle (e.g. error pages, emails) must
        # degrade to the bare feedback URL, not raise.
        from django.template import Context, Template
        rendered = Template(
            "{% load feedback_link %}{% feedback_url %}"
        ).render(Context({}))
        self.assertEqual(rendered, "/feedback/")



class CampaignRetirementTests(TestCase):
    """Pledge (REWARDS) and Buy-to-unglue campaigns are retired (#1195):
    the rights-holder UI must no longer offer them for new campaigns, while
    existing legacy campaigns must keep rendering."""

    def setUp(self):
        from regluit.core.models import RightsHolder, Claim
        self.user = User.objects.create_user('rhuser', 'rhuser@example.org', 'test')
        self.rh = RightsHolder.objects.create(
            rights_holder_name='retirement test rh', owner=self.user, approved=True
        )
        self.work = Work.objects.create(title="legacy pledge work", language='en')
        self.b2u_work = Work.objects.create(title="legacy b2u work", language='en')
        Claim.objects.create(
            work=self.work, user=self.user, status='active', rights_holder=self.rh
        )
        Claim.objects.create(
            work=self.b2u_work, user=self.user, status='active', rights_holder=self.rh
        )

    def test_open_campaign_form_offers_only_thanks(self):
        from regluit.frontend.forms import OpenCampaignForm
        from regluit.core.parameters import REWARDS, BUY2UNGLUE, THANKS
        form = OpenCampaignForm()
        self.assertEqual(
            [int(value) for value, label in form.fields['type'].choices],
            [THANKS],
        )
        # POSTs that try to force a retired type are rejected with a clean
        # form error on 'type'
        for retired_type in (REWARDS, BUY2UNGLUE):
            form = OpenCampaignForm(data={
                'name': self.work.title,
                'work': self.work.id,
                'userid': self.user.id,
                'type': retired_type,
            })
            self.assertFalse(form.is_valid())
            self.assertIn('type', form.errors)
        # THANKS is still accepted by the type field
        form = OpenCampaignForm(data={
            'name': self.work.title,
            'work': self.work.id,
            'userid': self.user.id,
            'type': THANKS,
        })
        form.is_valid()
        self.assertNotIn('type', form.errors)

    def test_legacy_campaigns_still_render(self):
        from datetime import datetime, timedelta
        from decimal import Decimal as D
        from django.utils.timezone import now
        from regluit.core import parameters
        from regluit.core.models import Campaign
        pledge = Campaign.objects.create(
            work=self.work,
            type=parameters.REWARDS,
            name='legacy pledge campaign',
            description='legacy pledge campaign',
            target=D('1000.00'),
            deadline=now() + timedelta(days=30),
        )
        b2u = Campaign.objects.create(
            work=self.b2u_work,
            type=parameters.BUY2UNGLUE,
            name='legacy b2u campaign',
            description='legacy b2u campaign',
            target=D('1000.00'),
            deadline=datetime(2030, 1, 1),
            cc_date_initial=datetime(2030, 1, 1),
        )
        # legacy campaigns launched before retirement carry ACTIVE status in
        # the db; retirement must not break their read-only display
        for campaign in (pledge, b2u):
            campaign.status = 'ACTIVE'
            campaign.activated = now()
            campaign.left = campaign.target
            campaign.save()
        anon_client = Client()
        for work in (self.work, self.b2u_work):
            r = anon_client.get("/work/{}/".format(work.id))
            self.assertEqual(r.status_code, 200)
