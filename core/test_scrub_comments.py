"""Regression tests for the comment-batch scrub (#1130 phase 1, PR #1217).

The scrub logic exists in exactly two places — migration core.0031 and the
scrub_comment_notice_batches management command — duplicated deliberately so
the migration stays frozen. These tests run the same scenarios against BOTH
copies, so a future edit to either cannot silently diverge from the other.

The scenarios are the synthetic-pickle fixtures from the PR #1217 review
(previously verified interactively but never committed):

  * a genuine comment batch, in the exact shape notification.models.queue()
    writes, including one embedding an object whose class is UNIMPORTABLE —
    the actual poisoned-batch scenario after django_comments is removed;
  * a non-comment batch (must be kept);
  * a comment label appearing only in message TEXT, not the label slot
    (the byte-scan false-positive case: precise inspection must say False);
  * non-conforming shapes (not a list / wrong tuple arity / non-str label)
    which MUST return None so the byte-scan fallback runs — the failure
    direction matters: a fallback false positive discards one batch, a
    False here would leave a poisoned batch and wedge the whole queue;
  * corrupt bytes, and a protocol-0 pickle.

Every verdict is exercised at every pickle protocol (0 through highest), and
the poisoned-batch scenario is covered in both failure shapes: a vanished
module (ModuleNotFoundError) and the production-shaped Django-model pickle,
which dies in the app registry (LookupError via model_unpickle) instead.

The command is also tested end-to-end against real NoticeQueueBatch rows.
"""

import importlib
import io
import pickle
import sys
import types

from django.core.management import call_command
from django.test import SimpleTestCase, TestCase

from notification.models import NoticeQueueBatch

# The two independent copies under test.
_migration = importlib.import_module(
    "regluit.core.migrations.0031_scrub_comment_notice_batches"
)
_command_mod = importlib.import_module(
    "regluit.core.management.commands.scrub_comment_notice_batches"
)

COMMENT_LABELS = [
    "comment_on_commented",
    "wishlist_comment",
    "wishlist_official_comment",
]


def _batch(entries, protocol=pickle.DEFAULT_PROTOCOL):
    """Pickle a batch exactly the way notification.models.queue() does."""
    return pickle.dumps(entries, protocol=protocol)


def _unimportable_instance(protocol=pickle.DEFAULT_PROTOCOL):
    """Return pickled bytes embedding a class whose module cannot be imported.

    Simulates a queued batch that froze an object from a removed module: the
    pickle names a module/class that no longer exists in the environment, so a
    plain pickle.loads() raises — the state that wedges send_all().
    """
    mod_name = "regluit_test_vanishing_module"
    mod = types.ModuleType(mod_name)

    class Frozen(object):
        pass

    Frozen.__module__ = mod_name
    Frozen.__qualname__ = "Frozen"
    mod.Frozen = Frozen
    sys.modules[mod_name] = mod
    try:
        obj = Frozen()
        obj.__dict__["text"] = "frozen comment body"
        data = pickle.dumps(
            [(1, "wishlist_comment", {"comment": obj}, True, None)],
            protocol=protocol,
        )
    finally:
        del sys.modules[mod_name]
    # Prove the fixture is what it claims to be: unimportable for the exact
    # expected reason — the module is gone (not some unrelated failure).
    try:
        pickle.loads(data)
    except ModuleNotFoundError as e:
        if mod_name not in str(e):  # pragma: no cover
            raise AssertionError("fixture failed for the wrong module: %s" % e)
    else:  # pragma: no cover
        raise AssertionError("fixture is importable; test premise broken")
    return data


def _django_model_poisoned_batch(protocol=pickle.DEFAULT_PROTOCOL):
    """Production-shaped poisoned batch: how a real pickled Django model dies.

    A pickled Django model instance does not reference its class directly — it
    references django.db.models.base.model_unpickle plus an (app_label, model)
    tuple. After the app leaves INSTALLED_APPS, loading fails inside
    model_unpickle with LookupError("No installed app with label ..."), NOT
    with ModuleNotFoundError. This fixture reproduces that exact failure mode
    for the removed 'django_comments' app.
    """
    from django.db.models.base import model_unpickle

    class _FrozenComment(object):
        # __reduce__ makes the pickle reference model_unpickle by name, the
        # same way Django's Model.__reduce__ does; _FrozenComment itself is
        # never named in the resulting bytes.
        def __reduce__(self):
            return (
                model_unpickle,
                (("django_comments", "comment"),),
                {"comment": "frozen spam"},
            )

    data = pickle.dumps(
        [(1, "comment_on_commented", {"comment": _FrozenComment()}, True, None)],
        protocol=protocol,
    )
    # Self-check: dies in Django's app registry, exactly as in production.
    try:
        pickle.loads(data)
    except LookupError as e:
        if "django_comments" not in str(e):  # pragma: no cover
            raise AssertionError("fixture failed on the wrong app: %s" % e)
    else:  # pragma: no cover
        raise AssertionError(
            "fixture loaded cleanly; is django_comments installed here?")
    return data


class QueuesCommentLabelsTests(SimpleTestCase):
    """Same assertions against both copies of _queues_comment_labels."""

    COPIES = [
        ("migration core.0031", _migration._queues_comment_labels),
        ("management command", _command_mod._queues_comment_labels),
    ]

    def both(self, data, expected, msg):
        for name, fn in self.COPIES:
            self.assertIs(fn(data), expected, "%s [%s]" % (msg, name))

    def test_comment_batch_each_label(self):
        for label in COMMENT_LABELS:
            self.both(
                _batch([(1, label, {}, True, None)]),
                True,
                "comment batch (%s) must be flagged" % label,
            )

    def test_non_comment_batch_kept(self):
        self.both(
            _batch([(1, "account_active", {"context": "x"}, True, None)]),
            False,
            "ordinary batch must be kept",
        )

    def test_mixed_batch_flagged(self):
        self.both(
            _batch([
                (1, "account_active", {}, True, None),
                (2, "wishlist_comment", {}, True, None),
            ]),
            True,
            "batch mixing comment and non-comment notices must be flagged",
        )

    def test_label_in_prose_is_not_a_match(self):
        # The byte-scan false-positive case: the label string appears in
        # message text but the label SLOT is a non-comment type.
        data = _batch([
            (1, "account_active",
             {"message": "you once got a wishlist_comment notice"},
             True, None)
        ])
        self.both(data, False, "label in prose must not flag the batch")

    def test_unimportable_embedded_class_still_inspected(self):
        self.both(
            _unimportable_instance(),
            True,
            "poisoned batch (unimportable class) must still be flagged by label",
        )

    def test_all_pickle_protocols(self):
        # queue() uses the interpreter's default protocol, which has changed
        # across the Python versions this codebase has lived through — queued
        # batches may exist at any protocol. Every verdict must hold at all
        # of them (Codex review 2026-08-23: committed matrix required).
        for proto in range(0, pickle.HIGHEST_PROTOCOL + 1):
            tag = "protocol %d" % proto
            self.both(
                _batch([(1, "comment_on_commented", {}, True, None)],
                       protocol=proto),
                True, "comment batch flagged at " + tag)
            self.both(
                _batch([(1, "account_active",
                         {"message": "mentions wishlist_comment only"},
                         True, None)], protocol=proto),
                False, "prose false-positive kept at " + tag)
            self.both(
                _batch([("bad-arity", "wishlist_comment")], protocol=proto),
                None, "malformed shape falls to byte scan at " + tag)
            self.both(
                _unimportable_instance(protocol=proto),
                True, "poisoned batch flagged at " + tag)

    def test_django_model_poisoned_batch(self):
        # The production-shaped failure: LookupError from Django's app
        # registry, not ModuleNotFoundError. Must still be flagged by label.
        self.both(
            _django_model_poisoned_batch(),
            True,
            "Django-model-shaped poisoned batch must be flagged",
        )

    # --- the 25703468 hardening: non-conforming shapes → None, never False ---

    def test_not_a_list_is_uninspectable(self):
        self.both(_batch({"not": "a list"}), None,
                  "non-list top level must fall through to byte scan")

    def test_wrong_arity_is_uninspectable(self):
        self.both(_batch([(1, "account_active", {})]), None,
                  "wrong tuple arity must fall through to byte scan")

    def test_non_string_label_is_uninspectable(self):
        self.both(_batch([(1, 42, {}, True, None)]), None,
                  "non-string label slot must fall through to byte scan")

    def test_list_entry_not_a_tuple_is_uninspectable(self):
        self.both(_batch([["list", "not", "tuple", True, None]]), None,
                  "non-tuple entry must fall through to byte scan")

    def test_corrupt_bytes_uninspectable(self):
        self.both(b"\x80\x04this is not a pickle", None,
                  "corrupt pickle must fall through to byte scan")

    def test_truncated_pickle_uninspectable(self):
        whole = _batch([(1, "account_active", {}, True, None)])
        self.both(whole[: len(whole) // 2], None,
                  "truncated pickle must fall through to byte scan")


class ScrubCommandTests(TestCase):
    """End-to-end: the command against real NoticeQueueBatch rows."""

    @staticmethod
    def _add(data):
        return NoticeQueueBatch.objects.create(pickled_data=data)

    def _run(self):
        out = io.StringIO()
        call_command("scrub_comment_notice_batches", stdout=out)
        return out.getvalue()

    def test_scrubs_only_comment_batches(self):
        keep_plain = self._add(
            _batch([(1, "account_active", {}, True, None)]))
        keep_prose = self._add(
            _batch([(1, "account_active",
                     {"message": "about a wishlist_comment"}, True, None)]))
        drop_comment = self._add(
            _batch([(1, "wishlist_comment", {}, True, None)]))
        drop_poisoned = self._add(_unimportable_instance())
        drop_django_shaped = self._add(_django_model_poisoned_batch())

        output = self._run()

        remaining = set(
            NoticeQueueBatch.objects.values_list("id", flat=True))
        self.assertEqual(remaining, {keep_plain.id, keep_prose.id})
        self.assertNotIn(drop_comment.id, remaining)
        self.assertNotIn(drop_poisoned.id, remaining)
        self.assertNotIn(drop_django_shaped.id, remaining)
        self.assertIn("batches examined: 5", output)
        self.assertIn("scrubbed: 3", output)
        self.assertIn("remaining: 2", output)

    def test_byte_scan_fallback_on_uninspectable_batches(self):
        # Uninspectable AND contains a comment label byte-wise → scrubbed
        # via fallback. Uninspectable without label bytes → kept (better to
        # leave an unknown batch than discard pending mail on no evidence).
        drop_fallback = self._add(b"garbage wishlist_comment garbage")
        keep_garbage = self._add(b"garbage with no label in it")
        # Non-conforming shape whose bytes DO contain a label: this is the
        # exact case the 25703468 hardening exists for — inspection must
        # return None (not False) so the byte scan can catch it.
        drop_hardened = self._add(
            _batch([("wrong-arity", "wishlist_comment")]))

        output = self._run()

        remaining = set(
            NoticeQueueBatch.objects.values_list("id", flat=True))
        self.assertEqual(remaining, {keep_garbage.id})
        self.assertNotIn(drop_fallback.id, remaining)
        self.assertNotIn(drop_hardened.id, remaining)
        self.assertIn("scrubbed: 2 (byte-scan fallback: 2)", output)

    def test_empty_queue_is_a_clean_noop(self):
        # The state production is expected to be in (queue measured 0 on
        # 2026-08-23): the command must report cleanly and touch nothing.
        output = self._run()
        self.assertIn("batches examined: 0, scrubbed: 0", output)
        self.assertIn("remaining: 0", output)
