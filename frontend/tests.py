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


class FeedbackUrlSpaceTests(TestCase):
    """Every page used to mint its own /feedback/?page=<this page> URL. On
    2026-09-17 production served 702,435 requests to /feedback/ across 693,968
    distinct URLs -- unacacheable by construction, and a direct cause of four
    outages. The link is now one constant URL site-wide and the originating
    page is recovered from the Referer header. See issue #1261."""

    FEEDBACK_HREF = re.compile(r'href="(/feedback/[^"]*)"')
    HIDDEN_PAGE = re.compile(r'name="page"[^>]*value="([^"]*)"')

    # A handful of templates hand-write a feedback link with a fixed topic
    # marker instead of a page URL. These are a constant three URLs site-wide,
    # they do not multiply with the page count, and they are not emitted by
    # the {% feedback_url %} tag.
    TOPIC_LINKS = {
        "/feedback/?page=Privacy",
        "/feedback/?page=no+activation+email",
        "/feedback/?page=need+support",
    }

    SAMPLE_PAGES = (
        ("/privacy/", {}),
        ("/faq/", {}),
        ("/search/", {"q": "sverige"}),
        ("/search/", {"q": "sverige", "page": "2"}),
        ("/feedback/", {}),
        ("/feedback/", {"page": "http://testserver/privacy/"}),
        ("/feedback/", {"page": "https://testserver/feedback/?page=x"}),
    )

    def page_field(self, response):
        m = self.HIDDEN_PAGE.search(str(response.content, 'utf-8'))
        self.assertIsNotNone(m, "no hidden page field in the feedback form")
        return m.group(1)

    def test_feedback_links_do_not_vary_with_the_page(self):
        # The whole point of #1261: the set of feedback URLs a page can emit
        # is fixed, so it does not grow with the ~2M crawlable pages.
        emitted = set()
        for path, query in self.SAMPLE_PAGES:
            r = Client().get(path, query)
            self.assertEqual(r.status_code, 200, path)
            hrefs = set(self.FEEDBACK_HREF.findall(str(r.content, 'utf-8')))
            self.assertIn("/feedback/", hrefs, "no bare feedback link on %s" % path)
            emitted |= hrefs
        self.assertEqual(emitted - self.TOPIC_LINKS, {"/feedback/"})

    def test_no_feedback_link_embeds_a_page_url(self):
        # The failure mode being fixed: a feedback link carrying the current
        # page's URL. Nothing url-shaped may appear in a feedback href.
        for path, query in self.SAMPLE_PAGES:
            r = Client().get(path, query)
            for href in self.FEEDBACK_HREF.findall(str(r.content, 'utf-8')):
                self.assertNotIn("%3A", href, path)   # encoded ':' -- a scheme
                self.assertNotIn("%2F", href, path)   # encoded '/' -- a path
                self.assertNotIn("http", href, path)

    def test_feedback_links_are_nofollow(self):
        r = Client().get("/privacy/")
        self.assertIn('href="/feedback/" rel="nofollow"', str(r.content, 'utf-8'))

    def test_pagination_state_reaches_the_form_via_the_referer(self):
        # Pagination state used to ride in the feedback URL (and a July 2026
        # regression guard checked it survived there). It now reaches the form
        # through the Referer instead.
        came_from = "http://testserver/search/?q=sverige&page=2"
        r = Client().get("/feedback/", HTTP_REFERER=came_from)
        self.assertEqual(self.page_field(r), came_from.replace("&", "&amp;"))

    def test_referer_supplies_the_originating_page(self):
        came_from = "http://testserver/work/9/"
        r = Client().get("/feedback/", HTTP_REFERER=came_from)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.page_field(r), came_from)
        self.assertIn("Feedback on page " + came_from, str(r.content, 'utf-8'))

    def test_no_referer_degrades_to_slash(self):
        r = Client().get("/feedback/")
        self.assertEqual(self.page_field(r), "/")

    def test_foreign_referer_is_ignored(self):
        for referer in ("http://evil.example.com/x",
                        "http://testserver.evil.example.com/x",
                        "http://evil@evil.example.com/x",
                        "https://testserver:8443/x",
                        "javascript:alert(1)",
                        "not a url at all",
                        "//testserver/x"):
            r = Client().get("/feedback/", HTTP_REFERER=referer)
            self.assertEqual(r.status_code, 200, referer)
            self.assertEqual(self.page_field(r), "/", referer)

    def test_malformed_referer_does_not_error(self):
        # urlsplit raises ValueError on a bad IPv6 literal
        r = Client().get("/feedback/", HTTP_REFERER="http://[::1/x")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.page_field(r), "/")

    def test_legacy_page_param_still_works_and_wins(self):
        # Links with ?page= will keep arriving from crawled copies of the old
        # pages for years, and a few templates hand-write one as a topic
        # marker (?page=need+support). They must keep working.
        r = Client().get("/feedback/", {"page": "need support"},
                         HTTP_REFERER="http://testserver/privacy/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.page_field(r), "need support")

    def test_page_value_cannot_inject_a_mail_header(self):
        r = Client().get("/feedback/",
                         {"page": "x\r\nBcc: someone@example.org"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.page_field(r), "x Bcc: someone@example.org")

    def test_page_value_is_bounded(self):
        r = Client().get("/feedback/", {"page": "u" * 500})
        self.assertEqual(len(self.page_field(r)), 200)

    def test_post_keeps_the_submitted_page_not_the_referer(self):
        # On POST the Referer is /feedback/ itself; the page the user came
        # from rides along in the hidden field and must survive a form error.
        r = Client().post("/feedback/", {
            'sender': 'someone@example.org',
            'subject': 'Feedback on page http://testserver/work/9/',
            'message': 'hi',
            'page': 'http://testserver/work/9/',
            'num1': '1', 'num2': '2', 'answer': '3',
            'notarobot': '4',  # wrong sum: re-renders the form
        }, HTTP_REFERER="http://testserver/feedback/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.page_field(r), "http://testserver/work/9/")

    def test_form_collapses_newlines_in_the_subject(self):
        # A newline here would raise BadHeaderError inside the celery task,
        # long after the user has been shown a thank-you page.
        from regluit.frontend.forms import FeedbackForm
        form = FeedbackForm(data={
            'sender': 'someone@example.org',
            'subject': 'hello\r\nBcc: someone@example.org',
            'message': 'hi',
            'page': '/',
            'num1': '1', 'num2': '2', 'answer': '3', 'notarobot': '3',
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['subject'],
                         'hello Bcc: someone@example.org')


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
        # a complete THANKS submission is fully valid (django-selectable's
        # multiple field takes a list of pks)
        form = OpenCampaignForm(data={
            'name': self.work.title,
            'work': self.work.id,
            'userid': self.user.id,
            'managers': [str(self.user.id)],
            'type': THANKS,
        })
        self.assertTrue(form.is_valid(), form.errors)

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


class LoginDoubleSubmitGuardTests(TestCase):
    """Tests pinning the #1240 double-submit guard in place.

    The guard itself is client-side JS (static/js/sitewide1.js). Its behavior
    is exercised by a dependency-free Node test (run here when node is
    available); the Django-side tests assert the wiring that makes the guard
    effective: the login form posts to the URL the guard watches, and every
    page loads the script that carries it.
    """

    def test_login_page_wires_up_guard(self):
        r = Client().get("/accounts/superlogin/")
        self.assertEqual(r.status_code, 200)
        content = r.content.decode()
        # base.html loads the sitewide script that contains the guard
        self.assertIn("/static/js/sitewide1.js", content)
        # the login form still posts to the action the guard is scoped to
        self.assertIn('action="/accounts/superlogin/"', content)

    def test_guard_behavior_via_node(self):
        import os
        import shutil
        import subprocess
        import unittest
        if not shutil.which("node"):
            raise unittest.SkipTest("node not available")
        test_js = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "static", "js", "tests", "login_guard_test.js",
        )
        result = subprocess.run(
            ["node", test_js], capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(
            result.returncode, 0,
            "guard behavioral tests failed:\n%s\n%s" % (result.stdout, result.stderr),
        )


from django.test import override_settings


@override_settings(
    ALLOWED_HOSTS=["unglue.it", "test.unglue.it", "localhost", "127.0.0.1"]
)
class RobotsTxtTests(TestCase):
    """/robots.txt is rendered from a template gated on the request host.

    The AI-crawler rules only apply on production; every other host (staging,
    dev, an IP address) must keep serving a blanket disallow so non-canonical
    copies of the site never get indexed.

    This is a ``TestCase`` rather than a ``SimpleTestCase`` even though the
    view itself touches no models: issuing the request loads the root URLconf,
    which imports a module that runs a query at import time. Under
    ``SimpleTestCase`` Django creates no test database, so that query would
    hit whatever database the settings actually point at. ``TestCase`` gets an
    isolated test database instead.
    """

    BASELINE_DISALLOWS = [
        "/accounts/",
        "/feedback/",
        "/socialauth/",
        "/search/",
        "/googlebooks/",
    ]

    # The load-shedding rules this change exists for: the expensive listing
    # and feed endpoints from #1189, excluded for the throttled crawler on
    # top of the baseline.
    CLAUDEBOT_EXTRA_DISALLOWS = [
        "/free/",
        "/bypub/",
        "/pid/",
        "/unglued/",
        "/campaigns/",
        "/api/",
    ]

    # Crawlers that collect model-training data, disallowed outright. This is
    # a content-usage decision, not a claim about their capabilities: several
    # of them do honor Crawl-delay and could be throttled instead.
    BLOCKED_AGENTS = [
        "GPTBot",
        "CCBot",
        "Bytespider",
        "Amazonbot",
        "meta-externalagent",
        "Diffbot",
    ]

    def _get(self, host):
        response = self.client.get("/robots.txt", HTTP_HOST=host)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain")
        return response.content.decode("utf-8")

    @staticmethod
    def _parse_groups(body):
        """Return {user-agent: {"disallow": [...], "other": [...]}}.

        Consecutive ``User-agent`` lines share one group (RFC 9309 2.2.1).
        Only ``Allow``/``Disallow`` close the run of user-agent lines: an
        extension record such as ``Crawl-delay`` or ``Sitemap`` must not end
        a group (2.2.4), so it is recorded without moving the boundary.
        """
        groups = {}
        current = []
        started = False
        for raw in body.splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line or ":" not in line:
                continue
            field, value = (part.strip() for part in line.split(":", 1))
            field = field.lower()
            if field == "user-agent":
                if started:
                    current = []
                    started = False
                groups.setdefault(
                    value, {"disallow": [], "allow": [], "other": []}
                )
                current.append(value)
            elif current:
                for agent in current:
                    if field in ("disallow", "allow"):
                        groups[agent][field].append(value)
                        started = True
                    else:
                        groups[agent]["other"].append((field, value))
        return groups

    def test_parser_keeps_consecutive_user_agents_in_one_group(self):
        """The parser must not let an extension record split a group.

        Guards the guard: if Crawl-delay ended a user-agent run, two agents
        sharing one stanza would be read as separate groups and the
        precedence check below would silently stop covering the second.
        """
        groups = self._parse_groups(
            "User-agent: A\n"
            "Crawl-delay: 5\n"
            "User-agent: B\n"
            "Disallow: /x/\n"
            "\n"
            "User-agent: C\n"
            "Disallow: /\n"
        )
        self.assertEqual(set(groups), {"A", "B", "C"})
        # The load-bearing property: the Crawl-delay between the two
        # User-agent lines did not split them, so both still receive the
        # group's Disallow rule.
        self.assertEqual(groups["A"]["disallow"], ["/x/"])
        self.assertEqual(groups["B"]["disallow"], ["/x/"])
        # The extension record itself is still captured, not discarded.
        self.assertIn(("crawl-delay", "5"), groups["A"]["other"])
        # C opens a new group: a rule line has been seen since the last
        # User-agent, which is what closes the previous group.
        self.assertEqual(groups["C"]["disallow"], ["/"])

    def test_production_host_serves_baseline_and_ai_rules(self):
        body = self._get("unglue.it")
        groups = self._parse_groups(body)

        self.assertIn("*", groups)
        for path in self.BASELINE_DISALLOWS:
            self.assertIn(path, groups["*"]["disallow"])
        self.assertNotIn("/", groups["*"]["disallow"])

        # ClaudeBot is throttled, not blocked, so work pages stay crawlable --
        # but every expensive path must be excluded, since those exclusions
        # are the actual load-shedding this change delivers.
        self.assertIn("ClaudeBot", groups)
        self.assertIn(("crawl-delay", "30"), groups["ClaudeBot"]["other"])
        self.assertNotIn("/", groups["ClaudeBot"]["disallow"])
        for path in self.BASELINE_DISALLOWS + self.CLAUDEBOT_EXTRA_DISALLOWS:
            self.assertIn(
                path, groups["ClaudeBot"]["disallow"],
                "ClaudeBot no longer excludes %s" % path,
            )

        # meta-webindexer indexes for Meta AI search, so it is not blocked
        # outright, but it was the largest single source of /free/ load
        # (#1253). It gets exactly the baseline plus ClaudeBot's listing
        # exclusions -- nothing broader (work pages stay crawlable) and no
        # Allow that could re-open a path. Exact equality also catches a
        # duplicated copy of these rules.
        self.assertIn("meta-webindexer", groups)
        self.assertEqual(
            sorted(groups["meta-webindexer"]["disallow"]),
            sorted(self.BASELINE_DISALLOWS + self.CLAUDEBOT_EXTRA_DISALLOWS),
        )
        self.assertEqual(groups["meta-webindexer"]["allow"], [])
        # Exactly one Crawl-delay, of 10 seconds: the 2026-09-10 experiment
        # (see the comment in robots.txt). Check Crawl-delay specifically, so
        # other extension records (such as a Sitemap line) don't fail this.
        self.assertEqual(
            [value for field, value in groups["meta-webindexer"]["other"]
             if field == "crawl-delay"],
            ["10"],
        )

        # Every crawler selected for blocking is fully disallowed. (Not
        # every training crawler: ClaudeBot trains too and is deliberately
        # throttled instead, and content-usage opt-out tokens are out of
        # scope for this change.)
        for agent in self.BLOCKED_AGENTS:
            self.assertIn(agent, groups)
            self.assertIn(
                "/", groups[agent]["disallow"],
                "%s is named but not actually blocked" % agent,
            )

        # Exhaustive: adding or removing a group has to be a deliberate edit
        # here too, so a stanza cannot be dropped or slipped in unnoticed.
        self.assertEqual(
            set(groups),
            {"*", "ClaudeBot", "meta-webindexer"} | set(self.BLOCKED_AGENTS),
        )

        # Search-indexing and user-triggered agents must NOT have their own
        # groups, so they keep falling through to the permissive "*" group.
        # Their publishers document them as not collecting training data, so
        # blocking one outright costs discoverability. When one does cause
        # real load, exclude the expensive paths instead (see meta-webindexer).
        for agent in (
            "Googlebot",
            "PerplexityBot",
            "Perplexity-User",
            "Amzn-SearchBot",
            "OAI-SearchBot",
            "ChatGPT-User",
            "Claude-SearchBot",
            "Claude-User",
        ):
            self.assertNotIn(agent, groups)

    def test_named_groups_do_not_widen_access(self):
        """Regression guard for robots.txt group precedence.

        The ``User-agent: *`` group applies only to crawlers that match no
        named group, so a named group that is not a blanket disallow has to
        restate the baseline rules -- otherwise adding a group *grants* that
        crawler access to paths it was previously excluded from.
        """
        groups = self._parse_groups(self._get("unglue.it"))
        for agent, rules in groups.items():
            if agent == "*" or "/" in rules["disallow"]:
                continue
            for path in self.BASELINE_DISALLOWS:
                self.assertIn(
                    path, rules["disallow"],
                    "User-agent %s omits baseline rule %s; a named group that "
                    "does not restate the baseline widens that crawler's "
                    "access instead of narrowing it." % (agent, path),
                )
            # Restating a Disallow is not enough on its own: RFC 9309 gives
            # the longest match precedence, so a more specific Allow beneath
            # one of these prefixes would quietly re-open it.
            for allowed in rules["allow"]:
                for path in self.BASELINE_DISALLOWS:
                    self.assertFalse(
                        allowed.startswith(path),
                        "User-agent %s allows %s, which overrides the longer-"
                        "matching baseline rule %s and widens access."
                        % (agent, allowed, path),
                    )

    def test_non_production_hosts_disallow_everything(self):
        for host in ("test.unglue.it", "localhost", "127.0.0.1"):
            with self.subTest(host=host):
                body = self._get(host)
                groups = self._parse_groups(body)
                self.assertEqual(list(groups), ["*"])
                self.assertEqual(groups["*"]["disallow"], ["/"])
                self.assertNotIn("ClaudeBot", body)
