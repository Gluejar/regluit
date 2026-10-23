"""
external library imports
"""
import json
import re
from decimal import Decimal
from unittest import skipUnless
from unittest.mock import patch

"""
django imports
"""
from django.contrib.auth.models import User
from django.db import connection, OperationalError
from django.test import TestCase
from django.test.client import Client
from django.utils.timezone import now

"""
regluit imports
"""
import regluit.core.isbn

from regluit.core import models
from regluit.api import models as apimodels
import time

class ApiTests(TestCase):
    fixtures = ['initial_data.json', 'neuromancer.json']
    work_id=None

    def setUp(self):
        edition = models.Edition.objects.get(pk=1)
        self.work_id=edition.work_id
        campaign = models.Campaign.objects.create(
            name=edition.work.title,
            work=edition.work,
            description='Test Campaign',
            deadline=now(),
            target=Decimal('1000.00'),
        )
        self.user = User.objects.create_user('test', 'test@example.org', 'testpass')
        self.client = Client()
        ebook = models.Ebook.objects.create(
            url="http://example.com/ebook",
            provider="github",
            rights='CC BY',
            format='epub',
            edition=edition,
        )

    def test_widget(self):
        r = self.client.get('/api/widget/0441007465/')
        self.assertEqual(r.status_code, 200)
        r = self.client.get('/api/widget/%s/'%self.work_id)
        self.assertEqual(r.status_code, 200)

    def test_widget_unknown_ids_return_empty_widget(self):
        # Regression for #1156: bad identifiers must render an empty widget (200),
        # not raise an uncaught exception (500).
        # non-numeric token (length != 10/13) -> safe_get_work raises Work.DoesNotExist
        r = self.client.get('/api/widget/featured4iL7gEXx/')
        self.assertEqual(r.status_code, 200)
        # numeric but no such work
        r = self.client.get('/api/widget/999999999/')
        self.assertEqual(r.status_code, 200)
        # invalid ISBN-10 -> convert_10_to_13 returns None (was len(None) TypeError)
        r = self.client.get('/api/widget/ABCDEFGHIJ/')
        self.assertEqual(r.status_code, 200)

class FeedTests(TestCase):
    fixtures = ['initial_data.json', 'neuromancer.json']
    def setUp(self):
        edition = models.Edition.objects.get(pk=1)
        ebook = models.Ebook.objects.create(edition=edition, url='http://example.org/', format='epub', rights='CC BY')
        self.test_work_id = edition.work_id

    def test_opds(self):
        r = self.client.get('/api/opds/creative_commons/')
        self.assertEqual(r.status_code, 200)
        r = self.client.get('/api/opds/epub/?order_by=featured')
        self.assertEqual(r.status_code, 200)
        r = self.client.get('/api/opds/by/pdf/?order_by=popular')
        self.assertEqual(r.status_code, 200)
        r = self.client.get('/api/opds/active_campaigns/?order_by=title')
        self.assertEqual(r.status_code, 200)
        r = self.client.get('/api/opds/?work=%s' % self.test_work_id)
        self.assertEqual(r.status_code, 200)

    def test_opds_all_keyword_alias_works(self):
        r = self.client.get('/api/opds/all/kw.Fiction/')
        self.assertEqual(r.status_code, 200)

    def test_opds_keyword_compound_returns_404(self):
        r = self.client.get('/api/opds/kw.Fiction/epub/')
        self.assertEqual(r.status_code, 404)

    def test_opds_single_keyword_works(self):
        r = self.client.get('/api/opds/kw.Fiction/')
        self.assertEqual(r.status_code, 200)

    def test_opdsjson_keyword_compound_returns_404(self):
        r = self.client.get('/api/opdsjson/kw.Fiction/epub/')
        self.assertEqual(r.status_code, 404)

    def test_onix_keyword_compound_returns_404(self):
        r = self.client.get('/api/onix/kw.Fiction/epub/')
        self.assertEqual(r.status_code, 404)

    def test_keyword_feeds_with_work_param(self):
        # A compound keyword path 404s even with ?work= (that early return used
        # to skip facet validation); a single keyword still serves the work.
        for feed in ('opds', 'opdsjson', 'onix'):
            for path, status in (('kw.Fiction/epub', 404), ('epub/kw.Fiction', 404),
                                 ('kw.Fiction/kw.Science', 404), ('kw.Fiction', 200),
                                 ('all/kw.Fiction', 200)):
                url = '/api/%s/%s/?work=%s' % (feed, path, self.test_work_id)
                with self.subTest(url=url):
                    self.assertEqual(self.client.get(url).status_code, status)


    def test_nix(self):
        r = self.client.get('/api/onix/by/')
        self.assertEqual(r.status_code, 200)
        r = self.client.get('/api/onix/cc0/')
        self.assertEqual(r.status_code, 200)
        r = self.client.get('/api/onix/epub/?max=10')
        self.assertEqual(r.status_code, 200)
        r = self.client.get('/api/onix/?work=%s' % self.test_work_id)
        self.assertEqual(r.status_code, 200)

    def test_onix_all_keyword_alias_works(self):
        r = self.client.get('/api/onix/all/kw.Fiction/')
        self.assertEqual(r.status_code, 200)

class SearchFeedGuardTests(TestCase):
    """OPDS search feeds (s.TERM): no facet fan-out; a slow query gets a 503 (#1265)."""
    fixtures = ['initial_data.json', 'neuromancer.json']

    def setUp(self):
        edition = models.Edition.objects.get(pk=1)
        models.Ebook.objects.create(edition=edition, url='http://example.org/',
                                    format='epub', rights='CC BY')

    @staticmethod
    def feed_paths(body):
        # the /api/opds/<path>/ part of every feed link in an XML feed
        return set(re.findall(r'href="https://unglue\.it/api/opds/([^"?]*)', body))

    def test_search_feed_links_only_to_itself(self):
        r = self.client.get('/api/opds/s.neuromancer/?page=1')
        self.assertEqual(r.status_code, 200)
        body = r.content.decode()
        self.assertEqual(self.feed_paths(body), {'s.neuromancer/'})
        self.assertIn('Sorted by popularity', body)
        self.assertIn('Previous 10', body)

    def test_non_search_feed_keeps_other_facet_links(self):
        r = self.client.get('/api/opds/epub/')
        self.assertEqual(r.status_code, 200)
        body = b''.join(r.streaming_content).decode()
        self.assertTrue(any(p.startswith('epub/') and p != 'epub/'
                            for p in self.feed_paths(body)))

    def test_json_search_feed_links_only_to_itself(self):
        r = self.client.get('/api/opdsjson/s.neuromancer/')
        self.assertEqual(r.status_code, 200)
        # parse only the links block: the feed puts a comma after every publication
        body = r.content.decode()
        links = json.loads(body.split('"links": ', 1)[1].split(',\n"publications"', 1)[0])
        paths = {l['href'].split('/api/opdsjson/')[1].split('?')[0] for l in links}
        self.assertEqual(paths, {'s.neuromancer/'})

    def test_search_timeout_is_503_without_error_log(self):
        def timed_out(*args, **kwargs):
            raise OperationalError(3024, 'maximum statement execution time exceeded')
            yield
        with patch('regluit.api.opds.opds_feed_for_works', timed_out), \
                self.assertNoLogs('django.request', level='ERROR'):
            r = self.client.get('/api/opds/s.open/pdf/')
        self.assertEqual(r.status_code, 503)
        self.assertEqual(r['Retry-After'], '3600')

    def test_other_database_errors_are_not_swallowed(self):
        def lost(*args, **kwargs):
            raise OperationalError(2013, 'Lost connection to MySQL server')
            yield
        with patch('regluit.api.opds.opds_feed_for_works', lost):
            with self.assertRaises(OperationalError):
                self.client.get('/api/opds/s.open/')

    @skipUnless(connection.vendor == 'mysql', 'max_execution_time is MySQL-only')
    def test_time_limit_is_reset_after_the_request(self):
        r = self.client.get('/api/opds/s.neuromancer/')
        self.assertEqual(r.status_code, 200)
        with connection.cursor() as cursor:
            cursor.execute("SELECT @@SESSION.max_execution_time, @@GLOBAL.max_execution_time")
            session_value, global_value = cursor.fetchone()
        self.assertEqual(session_value, global_value)

class AllowedRepoTests(TestCase):
    def setUp(self):
        apimodels.AllowedRepo.objects.create(org='test',repo_name='test')
        apimodels.AllowedRepo.objects.create(org='star',repo_name='*')

    def test_urls(self):
        #good
        self.assertTrue(apimodels.repo_allowed('https://github.com/test/test/raw/master/metadata.yaml')[0])
        self.assertTrue(apimodels.repo_allowed('https://github.com/star/test/raw/master/metadata.yaml')[0])
        # bad urls
        self.assertFalse(apimodels.repo_allowed('auhf8peargp8ge')[0])
        self.assertFalse(apimodels.repo_allowed('')[0])
        self.assertFalse(apimodels.repo_allowed('http://github.com/test/test/raw/master/metadata.yaml')[0])
        self.assertFalse(apimodels.repo_allowed('https://github.com/test/test/raw/master/samples/metadata.yaml')[0])
        self.assertFalse(apimodels.repo_allowed('https://github.com/test/test/raw/branch/metadata.yaml')[0])
        self.assertFalse(apimodels.repo_allowed('https://github.com/test/test/master/metadata.yaml')[0])
        self.assertFalse(apimodels.repo_allowed('https://github.com/test/test/raw/master/metadata.json')[0])

class FeedUpdatedTests(TestCase):
    """regluit#1265: a feed's <updated> date is served from the cache, and an
    expired or missing value is recomputed by one request at a time."""
    fixtures = ['initial_data.json', 'neuromancer.json']
    cache_name = 'test_1265_updated'

    def setUp(self):
        from django.core.cache import cache
        self.cache = cache
        cache.clear()
        self.works = models.Work.objects.all()
        self.newest = models.Work.objects.latest('created').created.isoformat()

    def tearDown(self):
        self.cache.clear()

    def test_cold_cache_computes_once_then_serves_from_cache(self):
        from regluit.api.opds import latest_created
        with self.assertNumQueries(1):
            first = latest_created(self.cache_name, self.works)
        self.assertTrue(first.startswith(self.newest[:19]))
        with self.assertNumQueries(0):
            self.assertEqual(latest_created(self.cache_name, self.works), first)

    def test_expired_value_is_refreshed_by_the_request_that_gets_the_lock(self):
        from regluit.api.opds import latest_created
        self.cache.set(self.cache_name, ('old', time.time() - 1), 100)
        with self.assertNumQueries(1):
            value = latest_created(self.cache_name, self.works)
        self.assertNotEqual(value, 'old')
        self.assertEqual(self.cache.get(self.cache_name)[0], value)

    def test_expired_value_is_served_stale_while_another_request_refreshes(self):
        from regluit.api.opds import latest_created
        self.cache.set(self.cache_name, ('old', time.time() - 1), 100)
        self.cache.add(self.cache_name + ':refreshing', 1, 60)
        with self.assertNumQueries(0):
            self.assertEqual(latest_created(self.cache_name, self.works), 'old')

    def test_cold_cache_while_another_request_computes_does_not_query(self):
        from regluit.api.opds import latest_created
        self.cache.add(self.cache_name + ':refreshing', 1, 60)
        with self.assertNumQueries(0):
            value = latest_created(self.cache_name, self.works)
        self.assertTrue(value)  # "now", as an ISO date
        self.assertIsNone(self.cache.get(self.cache_name))  # nothing cached from it

    def test_value_cached_before_the_change_is_served_and_refreshed(self):
        from regluit.api.opds import latest_created
        self.cache.set(self.cache_name, 'pre-1265 value', 100)
        with self.assertNumQueries(1):
            value = latest_created(self.cache_name, self.works)
        self.assertNotEqual(value, 'pre-1265 value')
        self.cache.set(self.cache_name, 'pre-1265 value', 100)
        self.cache.add(self.cache_name + ':refreshing', 1, 60)
        with self.assertNumQueries(0):
            self.assertEqual(latest_created(self.cache_name, self.works), 'pre-1265 value')

    def test_empty_feed_gets_a_date(self):
        from regluit.api.opds import latest_created
        self.assertTrue(latest_created(self.cache_name, models.Work.objects.none()))

    def test_lock_is_released_when_the_query_fails(self):
        from regluit.api.opds import latest_created

        class Broken:
            model = models.Work
            def latest(self, field):
                raise RuntimeError('database went away')

        with self.assertRaises(RuntimeError):
            latest_created(self.cache_name, Broken())
        self.assertIsNone(self.cache.get(self.cache_name + ':refreshing'))

    def test_refresh_outliving_its_lock_does_not_release_the_next_lock(self):
        # Request A takes the lock; its query runs past the lock's TTL, so the
        # lock expires and request B takes a new one. When A finishes it must
        # leave B's lock alone, or request C would start a third query.
        from regluit.api.opds import latest_created
        lock = self.cache_name + ':refreshing'
        cache = self.cache
        seen = {}

        class SlowWorks:
            model = models.Work
            def latest(self, field):
                seen['a_token'] = cache.get(lock)
                cache.delete(lock)  # A's lease runs out mid-query
                self.b_took_it = cache.add(lock, 'request-B-token', 60)
                return models.Work.objects.latest(field)

        slow = SlowWorks()
        value = latest_created(self.cache_name, slow)
        self.assertTrue(slow.b_took_it)
        self.assertTrue(seen['a_token'])
        self.assertNotEqual(seen['a_token'], 'request-B-token')
        self.assertEqual(cache.get(lock), 'request-B-token')  # B still holds it
        self.assertEqual(cache.get(self.cache_name)[0], value)  # A's value stored
        # and while B holds it, request C serves the cached value without querying
        cache.set(self.cache_name, (value, time.time() - 1), 100)
        with self.assertNumQueries(0):
            self.assertEqual(latest_created(self.cache_name, self.works), value)

    def test_successful_refresh_keeps_its_lock_until_the_lease_lapses(self):
        # Releasing after success is what opened the races; the lock now
        # lapses on its own, and the next stale read finds it still held.
        from regluit.api.opds import latest_created
        lock = self.cache_name + ':refreshing'
        value = latest_created(self.cache_name, self.works)
        self.assertTrue(self.cache.get(lock))  # still held, by this request's token
        self.cache.set(self.cache_name, ('old', time.time() - 1), 100)
        with self.assertNumQueries(0):  # within the lease: serve stale, no second query
            self.assertEqual(latest_created(self.cache_name, self.works), 'old')
        self.cache.delete(lock)  # the lease lapses
        with self.assertNumQueries(1):
            self.assertEqual(latest_created(self.cache_name, self.works), value)

    def test_slow_refresh_does_not_overwrite_a_newer_date(self):
        # A's query outlives its lease; B refreshes meanwhile and stores a
        # newer date. A finishing later must not put the older date back.
        from regluit.api.opds import latest_created
        cache = self.cache
        newer = '2999-01-01T00:00:00+00:00'

        class SlowWorks:
            model = models.Work
            def latest(self, field):
                cache.set(self_name, (newer, time.time() + 3600), 100)  # B's result
                return models.Work.objects.latest(field)

        self_name = self.cache_name
        self.assertEqual(latest_created(self.cache_name, SlowWorks()), newer)
        self.assertEqual(cache.get(self.cache_name)[0], newer)

    def test_navigation_feed_repeat_request_skips_the_date_queries(self):
        # The bare navigation feed is what timed out. Its first request
        # computes the dates; a repeat must not run them again.
        from django.db import connection
        from django.test.utils import CaptureQueriesContext
        with CaptureQueriesContext(connection) as first:
            r = self.client.get('/api/opds/')
        self.assertEqual(r.status_code, 200)
        with CaptureQueriesContext(connection) as repeat:
            r = self.client.get('/api/opds/')
        self.assertEqual(r.status_code, 200)
        self.assertLess(len(repeat.captured_queries), len(first.captured_queries))
        date_queries = [q['sql'] for q in repeat.captured_queries
                        if '`created` DESC' in q['sql'] and 'LIMIT 1' in q['sql']]
        self.assertEqual(date_queries, [])


class SingleWorkFeedTests(TestCase):
    # ?work= is user input. A non-numeric value makes filter() raise
    # ValueError; the feed should come back empty, not as a 500.
    def test_opds_non_numeric_work_returns_empty_feed(self):
        r = self.client.get('/api/opds/all/?work=notanumber')
        self.assertEqual(r.status_code, 200)
        self.assertNotIn(b'<entry', b''.join(r.streaming_content))

    def test_opdsjson_non_numeric_work_returns_empty_feed(self):
        r = self.client.get('/api/opdsjson/all/?work=notanumber')
        self.assertEqual(r.status_code, 200)
        # the feed isn't strict JSON (its @context URL is unquoted, as on
        # master), so check the text: the publications list is empty
        body = b''.join(r.streaming_content).decode()
        self.assertRegex(body, r'"publications":\s*\[\s*\]')


class WebHookTests(TestCase):
    fixtures = ['initial_data.json']
    def test_travisci_webhook(self):
        """
        test of api.views.travisci_webhook
        """

        payload = json.dumps({
          "repository":{
              "id":4651401,
              "name":"Adventures-of-Huckleberry-Finn_76",
              "owner_name":"GITenberg",
              "url":"http://GITenberg.github.com/"
           },
          "status_message": "Passed",
          "type": "push"
        })

        invalid_payload = json.dumps({
          "repository":{
              "id":4651401,
              "name":"",
              "url":"http://GITenberg.github.com/"
           },
          "status_message": "Passed",
          "type": "push"
        })

        url = "/api/travisci/webhook"

        # 200 if a simple get
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

        # 200 when we actually load a valid repo (should we use 201?)
        r = self.client.post(url, data={'payload':payload}, headers={}, allow_redirects=True)
        self.assertEqual(r.status_code, 200)

        # 400 error if we get exception when trying to load a book
        r = self.client.post(url, data={'payload':invalid_payload}, headers={}, allow_redirects=True)
        self.assertEqual(r.status_code, 400)
