"""Network-free tests for the backfill_doab command (#1151, PR #1152) and the
shared Retry-After sentinel helpers in load_doab.

Every DOAB/OAI call is mocked, the sentinel is redirected to a temp file, and
setUp blocks any non-loopback socket connect so an accidental network call
fails the test instead of reaching DOAB.
"""
import datetime
import json
import os
import socket
import tempfile
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, TestCase

from regluit.core.management.commands import backfill_doab as bf
from regluit.core.management.commands import load_doab as ld

UTC = datetime.timezone.utc
REAL_CONNECT = socket.socket.connect


def _deny_non_loopback(self, address, *args, **kwargs):
    host = address[0] if isinstance(address, tuple) else address
    if host not in ('127.0.0.1', '::1', 'localhost') and not str(host).startswith('/'):
        raise AssertionError('test attempted a network connection to %r' % (address,))
    return REAL_CONNECT(self, address, *args, **kwargs)


def _future(seconds=3600):
    return datetime.datetime.now(UTC) + datetime.timedelta(seconds=seconds)


class NoNetworkMixin:
    def block_network(self):
        patcher = mock.patch.object(socket.socket, 'connect', _deny_non_loopback)
        patcher.start()
        self.addCleanup(patcher.stop)


class SentinelTests(NoNetworkMixin, SimpleTestCase):
    def setUp(self):
        self.block_network()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, 'sentinel')

    def test_write_is_monotonic(self):
        later = _future(7200)
        sooner = _future(60)
        ld.write_block_deadline(later, path=self.path)
        # A shorter deadline must not replace a longer one.
        self.assertTrue(ld.write_block_deadline(sooner, path=self.path))
        self.assertEqual(ld.read_block_deadline(self.path), later)
        # Equal deadline is also a no-op; a later one does move it.
        self.assertTrue(ld.write_block_deadline(later, path=self.path))
        even_later = _future(10800)
        ld.write_block_deadline(even_later, path=self.path)
        self.assertEqual(ld.read_block_deadline(self.path), even_later)

    def test_concurrent_writers_end_at_the_latest_deadline(self):
        import random
        import threading
        base = _future(0)
        offsets = list(range(1, 41))
        random.shuffle(offsets)
        threads = [threading.Thread(
            target=ld.write_block_deadline,
            args=(base + datetime.timedelta(seconds=o),), kwargs={'path': self.path})
            for o in offsets]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(ld.read_block_deadline(self.path),
                         base + datetime.timedelta(seconds=40))
        # atomic replace leaves no temp files behind
        self.assertEqual(sorted(os.listdir(self.tmp.name)), ['sentinel', 'sentinel.lock'])

    def test_write_replaces_an_expired_deadline_with_a_sooner_future_one(self):
        ld.write_block_deadline(_future(-3600), path=self.path)
        new = _future(60)
        ld.write_block_deadline(new, path=self.path)
        self.assertEqual(ld.read_block_deadline(self.path), new)

    def test_lock_failure_fails_closed_and_keeps_existing_deadline(self):
        deadline = _future(3600)
        ld.write_block_deadline(deadline, path=self.path)
        with mock.patch.object(ld.fcntl, 'flock', side_effect=OSError('nope')):
            self.assertFalse(ld.write_block_deadline(_future(7200), path=self.path,
                                                     stderr=StringIO()))
        self.assertEqual(ld.read_block_deadline(self.path), deadline)

    def test_clear_never_deletes_expired(self):
        ld.write_block_deadline(_future(-60), path=self.path)
        self.assertIsNone(ld.clear_sentinel(self.path))
        self.assertTrue(os.path.exists(self.path))

    def test_clear_returns_active_deadline_and_keeps_file(self):
        deadline = _future(3600)
        ld.write_block_deadline(deadline, path=self.path)
        self.assertEqual(ld.clear_sentinel(self.path), deadline)
        self.assertTrue(os.path.exists(self.path))
        self.assertEqual(ld.read_block_deadline(self.path), deadline)

    def test_clear_on_missing_file_creates_nothing(self):
        self.assertIsNone(ld.clear_sentinel(self.path))
        self.assertFalse(os.path.exists(self.path))

    def test_naive_timestamp_is_read_as_utc(self):
        with open(self.path, 'w') as f:
            f.write('2030-01-01T00:00:00')
        self.assertEqual(ld.read_block_deadline(self.path).tzinfo, UTC)


class ParsingTests(SimpleTestCase):
    def test_numeric_suffix(self):
        self.assertEqual(bf.numeric_suffix('20.500.12854/123'), 123)
        self.assertEqual(bf.numeric_suffix('20.500.12854/123.4'), 123)
        self.assertEqual(bf.numeric_suffix('bogus'), -1)

    def test_load_input_ids_dedupes_and_flags_malformed(self):
        with tempfile.NamedTemporaryFile('w', suffix='.ids', delete=False) as f:
            f.write('# comment\n20.500.12854/5\n20.500.12854/5\nnope\n\n20.500.12854/6\n')
        self.addCleanup(os.remove, f.name)
        ids, sha, malformed = bf.load_input_ids(f.name)
        self.assertEqual(ids, ['20.500.12854/5', '20.500.12854/6'])
        self.assertEqual(len(sha), 64)
        self.assertEqual([m[0] for m in malformed], [4])


def _record(deleted=False, has_metadata=True):
    header = mock.Mock()
    header.isDeleted.return_value = deleted
    return (header, mock.Mock() if has_metadata else None, None)


class BackfillCommandTests(NoNetworkMixin, TestCase):
    """Drives handle() with the OAI client and loader mocked out."""

    def setUp(self):
        self.block_network()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.state = os.path.join(self.tmp.name, 'state.json')
        self.ids_path = os.path.join(self.tmp.name, 'ids.txt')
        self.sentinel = os.path.join(self.tmp.name, 'sentinel')

        # backfill_doab imported the sentinel helpers by name with the real
        # path baked in as a default; rebind them to the temp file.
        def _patch(name, func):
            p = mock.patch.object(
                bf, name, lambda *a, **k: func(*a, **{**k, 'path': self.sentinel}))
            p.start()
            self.addCleanup(p.stop)
        _patch('read_block_deadline', ld.read_block_deadline)
        _patch('write_block_deadline', ld.write_block_deadline)
        _patch('clear_sentinel', ld.clear_sentinel)

        sleeper = mock.patch.object(bf.time, 'sleep')
        self.sleep = sleeper.start()
        self.addCleanup(sleeper.stop)

        self.bitstream_open = mock.patch.object(
            bf.doab, 'bitstream_breaker_open', return_value=False).start()
        self.fetch = mock.patch.object(bf.doab, 'get_doab_record').start()
        self.add = mock.patch.object(bf.doab, 'add_by_doab').start()
        self.addCleanup(mock.patch.stopall)
        self.fetch.return_value = _record()
        self.add.return_value = mock.Mock(id=42)

    def write_ids(self, n, start=100000):
        ids = ['20.500.12854/%d' % (start + i) for i in range(n)]
        with open(self.ids_path, 'w') as f:
            f.write('\n'.join(ids) + '\n')
        return ids

    def run_cmd(self, **opts):
        out = StringIO()
        call_command('backfill_doab', ids_file=self.ids_path, state_file=self.state,
                     rate=0, stdout=out, **opts)
        return out.getvalue()

    def exit_code(self, **opts):
        with self.assertRaises(SystemExit) as cm:
            self.run_cmd(**opts)
        return cm.exception.code

    def load_state(self):
        with open(self.state) as f:
            return json.load(f)

    # --- exit 0 ---------------------------------------------------------

    def test_drained_exits_zero_and_records_ok(self):
        self.write_ids(3)
        self.run_cmd()  # returns normally: exit 0
        st = self.load_state()
        self.assertEqual(st['totals']['ok'], 3)
        self.assertEqual(st['totals']['remaining'], 0)
        self.assertEqual(st['last_run']['exit_reason'], 'drained')
        self.assertEqual(self.add.call_count, 3)

    def test_rerun_after_drain_makes_no_calls(self):
        self.write_ids(2)
        self.run_cmd()
        self.fetch.reset_mock()
        self.run_cmd()
        self.fetch.assert_not_called()

    def test_dry_run_makes_no_remote_or_db_write_calls(self):
        self.write_ids(3)
        out = self.run_cmd(dry_run=True)
        self.assertIn('DRY RUN', out)
        self.fetch.assert_not_called()
        self.add.assert_not_called()
        self.assertFalse(os.path.exists(self.state))

    # --- exit 3: checkpoints --------------------------------------------

    def test_max_remote_calls_exits_three(self):
        self.write_ids(5)
        self.assertEqual(self.exit_code(max_remote_calls=2), bf.EXIT_CHECKPOINT)
        st = self.load_state()
        self.assertEqual(st['last_run']['exit_reason'], 'max_remote_calls')
        self.assertEqual(st['totals']['ok'], 2)

    def test_active_sentinel_exits_three_without_fetching(self):
        self.write_ids(2)
        ld.write_block_deadline(_future(3600), path=self.sentinel)
        self.assertEqual(self.exit_code(), bf.EXIT_CHECKPOINT)
        self.fetch.assert_not_called()

    def test_ignore_retry_after_bypasses_sentinel(self):
        self.write_ids(1)
        ld.write_block_deadline(_future(3600), path=self.sentinel)
        self.run_cmd(ignore_retry_after=True)
        self.assertEqual(self.fetch.call_count, 1)

    def test_long_retry_after_checkpoints_and_sets_sentinel(self):
        self.write_ids(3)
        err = bf._PyOAIRateLimitedError()
        err.retry_after_seconds = 1000
        err.retry_after_raw = '1000'
        self.fetch.side_effect = err
        self.assertEqual(self.exit_code(max_retry_after=300), bf.EXIT_CHECKPOINT)
        self.assertEqual(self.fetch.call_count, 1)
        self.sleep.assert_not_called()  # over the cap: no sleep, no retry
        self.assertGreater(ld.read_block_deadline(self.sentinel), _future(900))
        self.assertEqual(self.load_state()['totals']['retry'], 1)

    def test_short_retry_after_sleeps_retries_once_then_stops(self):
        self.write_ids(3)
        err = bf._PyOAIRateLimitedError()
        err.retry_after_seconds = 5
        err.retry_after_raw = '5'
        self.fetch.side_effect = [err, _record()]

        def fake_sleep(secs):  # real sleep would let the ban expire
            with open(self.sentinel, 'w') as f:
                f.write(_future(-1).isoformat())
        self.sleep.side_effect = fake_sleep
        self.assertEqual(self.exit_code(), bf.EXIT_CHECKPOINT)
        self.sleep.assert_called_once_with(5)
        self.assertEqual(self.fetch.call_count, 2)
        st = self.load_state()
        self.assertEqual(st['totals']['ok'], 1)
        self.assertEqual(st['last_run']['exit_reason'], '429_recovered_single_record')

    def test_peer_extends_ban_during_courtesy_sleep_skips_retry(self):
        self.write_ids(3)
        err = bf._PyOAIRateLimitedError()
        err.retry_after_seconds = 5
        err.retry_after_raw = '5'
        self.fetch.side_effect = [err, _record()]
        self.sleep.side_effect = lambda secs: ld.write_block_deadline(
            _future(7200), path=self.sentinel)
        self.assertEqual(self.exit_code(), bf.EXIT_CHECKPOINT)
        self.assertEqual(self.fetch.call_count, 1)  # no courtesy retry
        self.assertEqual(self.load_state()['totals']['retry'], 1)

    def courtesy_retry_fails_with(self, exc):
        self.write_ids(3)
        err = self.rate_limited(5)
        self.fetch.side_effect = [err, exc]

        def fake_sleep(secs):
            with open(self.sentinel, 'w') as f:
                f.write(_future(-1).isoformat())
        self.sleep.side_effect = fake_sleep
        return self.exit_code()

    def test_courtesy_retry_non_429_client_error_halts_without_inventing_a_ban(self):
        import urllib.error
        code = self.courtesy_retry_fails_with(
            urllib.error.HTTPError('u', 403, 'x', {}, None))
        self.assertEqual(code, bf.EXIT_HALT)
        self.assertLess(ld.read_block_deadline(self.sentinel), _future(0))

    def test_courtesy_retry_network_error_is_checkpoint_without_a_ban(self):
        code = self.courtesy_retry_fails_with(ConnectionError('reset'))
        self.assertEqual(code, bf.EXIT_CHECKPOINT)
        self.assertLess(ld.read_block_deadline(self.sentinel), _future(0))

    def test_courtesy_retry_unknown_error_halts(self):
        self.assertEqual(self.courtesy_retry_fails_with(RuntimeError('parser')),
                         bf.EXIT_HALT)

    def test_courtesy_retry_second_429_extends_ban_and_checkpoints(self):
        code = self.courtesy_retry_fails_with(self.rate_limited(900))
        self.assertEqual(code, bf.EXIT_CHECKPOINT)
        self.assertGreater(ld.read_block_deadline(self.sentinel), _future(600))

    def test_server_error_is_transient_checkpoint(self):
        import urllib.error
        self.write_ids(2)
        self.fetch.side_effect = urllib.error.HTTPError('u', 503, 'x', {}, None)
        self.assertEqual(self.exit_code(), bf.EXIT_CHECKPOINT)
        self.assertEqual(self.load_state()['totals']['retry'], 1)

    # --- exit 4: circuit breakers ---------------------------------------

    def test_unknown_exception_halts_with_four_and_is_not_terminal(self):
        self.write_ids(3)
        self.add.side_effect = RuntimeError('boom')
        self.assertEqual(self.exit_code(), bf.EXIT_HALT)
        st = self.load_state()
        self.assertEqual(st['totals']['retry'], 1)  # not frozen as terminal
        self.assertEqual(st['last_run']['exit_reason'], 'unknown_exception_halt')

    def test_other_4xx_halts_with_four(self):
        import urllib.error
        self.write_ids(2)
        self.fetch.side_effect = urllib.error.HTTPError('u', 403, 'x', {}, None)
        self.assertEqual(self.exit_code(), bf.EXIT_HALT)
        self.assertEqual(self.load_state()['totals']['error_review'], 1)

    def test_gone_rate_halt_on_final_batch(self):
        # Exactly 100 records, all gone: there is no 101st iteration to trip the
        # top-of-loop check, so the post-loop check must halt instead of draining.
        self.write_ids(100)
        self.fetch.return_value = None
        self.assertEqual(self.exit_code(), bf.EXIT_HALT)
        self.assertEqual(self.load_state()['last_run']['exit_reason'], 'gone_rate_halt')

    def test_sentinel_set_mid_run_stops_before_next_fetch(self):
        self.write_ids(5)
        sentinel = self.sentinel

        def ban_after_first(doab_id):
            ld.write_block_deadline(_future(3600), path=sentinel)
            return _record()
        self.fetch.side_effect = ban_after_first
        self.assertEqual(self.exit_code(), bf.EXIT_CHECKPOINT)
        self.assertEqual(self.fetch.call_count, 1)
        self.assertEqual(self.load_state()['last_run']['exit_reason'], 'sentinel_set_by_peer')

    def test_gone_rate_halt(self):
        # 101 records, every one gone: the breaker is checked at the top of the
        # loop once 100 have been processed, so the 101st is never fetched.
        self.write_ids(101)
        self.fetch.return_value = None
        self.assertEqual(self.exit_code(), bf.EXIT_HALT)
        st = self.load_state()
        self.assertEqual(st['last_run']['exit_reason'], 'gone_rate_halt')
        self.assertEqual(st['last_run']['processed'], 100)
        self.assertEqual(self.fetch.call_count, 100)

    def test_gone_rate_under_threshold_does_not_halt(self):
        self.write_ids(100)
        # 20% gone, below the 30% default
        self.fetch.side_effect = [None if i % 5 == 0 else _record() for i in range(100)]
        self.run_cmd()
        self.assertEqual(self.load_state()['totals']['gone'], 20)

    # --- record-level outcomes ------------------------------------------

    def test_deleted_and_empty_records_are_gone(self):
        self.write_ids(2)
        self.fetch.side_effect = [_record(deleted=True), _record(has_metadata=False)]
        self.run_cmd()
        self.assertEqual(self.load_state()['totals']['gone'], 2)
        self.add.assert_not_called()

    def test_validation_error_is_terminal_and_drained_run_halts_for_review(self):
        self.write_ids(2)
        self.add.side_effect = [ValueError('bad'), mock.Mock(id=1)]
        # both records are processed (the bad one doesn't stop the loop), but a
        # drained worklist with error_review items must not look "done".
        self.assertEqual(self.exit_code(), bf.EXIT_HALT)
        st = self.load_state()
        totals = st['totals']
        self.assertEqual((totals['error_review'], totals['ok']), (1, 1))
        self.assertEqual(st['last_run']['exit_reason'], 'error_review_halt')

    def test_add_by_doab_returning_none_is_error_review_exit_four(self):
        self.write_ids(1)
        self.add.return_value = None
        self.assertEqual(self.exit_code(), bf.EXIT_HALT)
        self.assertEqual(self.load_state()['totals']['error_review'], 1)

    def test_error_review_does_not_halt_until_the_whole_worklist_is_done(self):
        self.write_ids(3)
        self.add.side_effect = [ValueError('bad'), mock.Mock(id=1), mock.Mock(id=2)]
        # a slice that drains with work left elsewhere is a checkpoint (3)...
        self.assertEqual(self.exit_code(id_range='100000-100001'), bf.EXIT_CHECKPOINT)
        # ...and the final drain is what reports the review items (4).
        self.assertEqual(self.exit_code(), bf.EXIT_HALT)

    def make_doab_work(self, doab_id, with_ebook):
        from regluit.core.models import Ebook, Edition, Identifier, Work
        work = Work.objects.create(title='t', language='en')
        edition = Edition.objects.create(title='t', work=work)
        Identifier.objects.create(type='doab', value=doab_id, work=work, edition=edition)
        if with_ebook:
            Ebook.objects.create(edition=edition, format='pdf', provider='x',
                                 url='http://example.invalid/b.pdf')
        return work

    def test_complete_local_load_is_present_locally_without_fetch(self):
        ids = self.write_ids(1)
        self.make_doab_work(ids[0], with_ebook=True)
        self.run_cmd()
        self.fetch.assert_not_called()
        self.assertEqual(self.load_state()['ids'][ids[0]]['status'], 'present_locally')

    def test_bare_identifier_without_ebook_is_reloaded_not_frozen(self):
        ids = self.write_ids(1)
        self.make_doab_work(ids[0], with_ebook=False)
        self.run_cmd()
        self.assertEqual(self.fetch.call_count, 1)
        self.assertEqual(self.add.call_count, 1)
        self.assertEqual(self.load_state()['ids'][ids[0]]['status'], 'ok')

    def test_load_is_complete_helper(self):
        self.assertFalse(bf.load_is_complete('20.500.12854/999'))
        self.make_doab_work('20.500.12854/1', with_ebook=False)
        self.make_doab_work('20.500.12854/2', with_ebook=True)
        self.assertFalse(bf.load_is_complete('20.500.12854/1'))
        self.assertTrue(bf.load_is_complete('20.500.12854/2'))

    def test_discovery_keeps_partial_identifiers_on_the_worklist(self):
        done = '20.500.12854/10'
        partial = '20.500.12854/11'
        new = '20.500.12854/12'
        self.make_doab_work(done, with_ebook=True)
        self.make_doab_work(partial, with_ebook=False)
        active = os.path.join(self.tmp.name, 's.active')
        with open(active, 'w') as f:
            f.write('\n'.join([done, partial, new]) + '\n')
        out = StringIO()
        call_command('backfill_doab', state_file=self.state, use_active_file=active,
                     stdout=out, dry_run=True)
        self.assertIn('backfill=2', out.getvalue())

    def test_refresh_retires_old_worklist_marker_before_republishing(self):
        active = os.path.join(self.tmp.name, 's.active')
        with open(active, 'w') as f:
            f.write('20.500.12854/1\n')
        ids_out = os.path.join(self.tmp.name, 'w.ids')
        with open(ids_out, 'w') as f:
            f.write('20.500.12854/999\n')
        with mock.patch.object(bf, 'atomic_write_lines', side_effect=OSError('crash')):
            with self.assertRaises(OSError):
                bf.discover_via_active_file(
                    active, None, ids_out, ids_out + '.stale', ids_out + '.orphans',
                    StringIO(), StringIO())
        self.assertFalse(os.path.exists(ids_out))  # no stale marker survives a crash

    def test_integrity_error_with_complete_load_is_present_locally(self):
        from django.db import IntegrityError
        ids = self.write_ids(1)
        self.add.side_effect = lambda *a, **k: (
            self.make_doab_work(ids[0], with_ebook=True), (_ for _ in ()).throw(
                IntegrityError('dup')))[1]
        self.run_cmd()
        self.assertEqual(self.load_state()['ids'][ids[0]]['status'], 'present_locally')

    def test_integrity_error_with_incomplete_load_stays_retryable(self):
        from django.db import IntegrityError
        ids = self.write_ids(2)

        def racing_add(doab_id, record=None):
            if doab_id == ids[0]:
                self.make_doab_work(doab_id, with_ebook=False)
                raise IntegrityError('dup')
            return mock.Mock(id=1)
        self.add.side_effect = racing_add
        # newest-first would reorder; use as-given so ids[0] goes first
        self.assertEqual(self.exit_code(order='as-given'), bf.EXIT_CHECKPOINT)
        st = self.load_state()
        self.assertEqual(st['ids'][ids[0]]['status'], 'retry')
        self.assertEqual(st['ids'][ids[1]]['status'], 'ok')

    def test_integrity_error_with_no_identifier_halts(self):
        from django.db import IntegrityError
        self.write_ids(1)
        self.add.side_effect = IntegrityError('weird')
        self.assertEqual(self.exit_code(), bf.EXIT_HALT)

    # --- bitstream (cover) breaker --------------------------------------

    def test_bitstream_breaker_tripped_by_add_by_doab_checkpoints(self):
        self.write_ids(5)

        def add(doab_id, record=None):
            self.bitstream_open.return_value = True  # cover fetch 429 tripped it
            return mock.Mock(id=1)
        self.add.side_effect = add
        out = StringIO()
        with self.assertRaises(SystemExit) as cm:
            call_command('backfill_doab', ids_file=self.ids_path, state_file=self.state,
                         rate=0, stdout=out)
        self.assertEqual(cm.exception.code, bf.EXIT_CHECKPOINT)
        self.assertIn('bitstream', out.getvalue())
        st = self.load_state()
        self.assertEqual(st['totals']['ok'], 1)  # the record just loaded is kept
        self.assertEqual(st['last_run']['exit_reason'], 'bitstream_breaker_open')
        self.assertEqual(self.fetch.call_count, 1)

    def test_bitstream_breaker_already_open_stops_before_fetching(self):
        self.write_ids(2)
        self.bitstream_open.return_value = True
        self.assertEqual(self.exit_code(), bf.EXIT_CHECKPOINT)
        self.fetch.assert_not_called()

    # --- --id-range -----------------------------------------------------

    def test_id_range_slice_drained_with_work_elsewhere_exits_three(self):
        self.write_ids(4)  # 100000..100003
        self.assertEqual(self.exit_code(id_range='100000-100001'), bf.EXIT_CHECKPOINT)
        st = self.load_state()
        self.assertEqual(st['totals']['ok'], 2)
        self.assertEqual(st['totals']['remaining'], 2)
        self.assertEqual(st['last_run']['exit_reason'], 'partial_drain')

    def test_id_range_covering_everything_exits_zero(self):
        self.write_ids(2)
        self.run_cmd(id_range='100000-100001')

    # --- discovery-phase 429 and unpersistable bans ----------------------

    def discover(self, **opts):
        out, err = StringIO(), StringIO()
        with self.assertRaises(SystemExit) as cm:
            call_command('backfill_doab', state_file=self.state, rate=0,
                         stdout=out, stderr=err, **opts)
        return cm.exception.code

    def rate_limited(self, secs=120):
        err = bf._PyOAIRateLimitedError()
        err.retry_after_seconds = secs
        err.retry_after_raw = str(secs)
        return err

    def test_discovery_429_persists_ban_and_exits_three(self):
        with mock.patch.object(bf.doab, 'doab_client') as client:
            client.listIdentifiers.side_effect = self.rate_limited(120)
            self.assertEqual(self.discover(), bf.EXIT_CHECKPOINT)
        self.assertGreater(ld.read_block_deadline(self.sentinel), _future(60))

    def test_discovery_stock_http_429_exits_three(self):
        import urllib.error
        with mock.patch.object(bf.doab, 'doab_client') as client:
            client.listIdentifiers.side_effect = urllib.error.HTTPError(
                'u', 429, 'x', {'Retry-After': '90'}, None)
            self.assertEqual(self.discover(), bf.EXIT_CHECKPOINT)
        self.assertTrue(os.path.exists(self.sentinel))

    def test_discovery_429_with_unpersistable_ban_halts(self):
        with mock.patch.object(bf.doab, 'doab_client') as client, \
                mock.patch.object(bf, 'write_block_deadline', return_value=False):
            client.listIdentifiers.side_effect = self.rate_limited(120)
            self.assertEqual(self.discover(), bf.EXIT_HALT)

    def test_loop_429_with_unpersistable_ban_halts(self):
        self.write_ids(2)
        self.fetch.side_effect = self.rate_limited(5)
        with mock.patch.object(bf, 'write_block_deadline', return_value=False):
            self.assertEqual(self.exit_code(), bf.EXIT_HALT)
        self.sleep.assert_not_called()
        self.assertEqual(self.fetch.call_count, 1)

    def test_stock_429_in_loop_with_unpersistable_ban_halts(self):
        import urllib.error
        self.write_ids(2)
        self.fetch.side_effect = urllib.error.HTTPError(
            'u', 429, 'x', {'Retry-After': '30'}, None)
        with mock.patch.object(bf, 'write_block_deadline', return_value=False):
            self.assertEqual(self.exit_code(), bf.EXIT_HALT)

    # --- guards ---------------------------------------------------------

    def test_changed_ids_file_is_refused(self):
        self.write_ids(2)
        self.run_cmd()
        self.write_ids(3)
        with self.assertRaises(CommandError):
            self.run_cmd()

    def test_malformed_ids_file_is_refused(self):
        with open(self.ids_path, 'w') as f:
            f.write('garbage\n')
        with self.assertRaises(CommandError):
            self.run_cmd()

    def test_use_deleted_file_requires_use_active_file(self):
        with self.assertRaises(CommandError):
            call_command('backfill_doab', state_file=self.state,
                         use_deleted_file='x', stdout=StringIO())

    def test_use_active_file_conflicts_with_ids_file(self):
        self.write_ids(1)
        with self.assertRaises(CommandError):
            call_command('backfill_doab', state_file=self.state, ids_file=self.ids_path,
                         use_active_file='x', stdout=StringIO())

    def test_active_file_dry_run_diffs_without_writing_or_calling_doab(self):
        active = os.path.join(self.tmp.name, 's.active')
        with open(active, 'w') as f:
            f.write('20.500.12854/1\n20.500.12854/2\n')
        out = StringIO()
        with mock.patch.object(bf.doab, 'doab_client') as client:
            call_command('backfill_doab', state_file=self.state, use_active_file=active,
                         dry_run=True, stdout=out)
        client.listIdentifiers.assert_not_called()
        self.fetch.assert_not_called()
        self.assertIn('backfill=2', out.getvalue())
        self.assertEqual(os.listdir(self.tmp.name).count('state.json.ids'), 0)
