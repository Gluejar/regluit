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

    # Crawlers that collect training data and document no Crawl-delay
    # support, so there is nothing to throttle -- fully disallowed.
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
                groups.setdefault(value, {"disallow": [], "other": []})
                current.append(value)
            elif current:
                for agent in current:
                    if field in ("disallow", "allow"):
                        if field == "disallow":
                            groups[agent]["disallow"].append(value)
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

        # Every training crawler is fully disallowed.
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
            {"*", "ClaudeBot"} | set(self.BLOCKED_AGENTS),
        )

        # Search-indexing and user-triggered agents must NOT have their own
        # groups, so they keep falling through to the permissive "*" group.
        # Their publishers document them as not collecting training data, so
        # blocking one costs discoverability while shedding no crawl load.
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

    def test_non_production_hosts_disallow_everything(self):
        for host in ("test.unglue.it", "localhost", "127.0.0.1"):
            with self.subTest(host=host):
                body = self._get(host)
                groups = self._parse_groups(body)
                self.assertEqual(list(groups), ["*"])
                self.assertEqual(groups["*"]["disallow"], ["/"])
                self.assertNotIn("ClaudeBot", body)
