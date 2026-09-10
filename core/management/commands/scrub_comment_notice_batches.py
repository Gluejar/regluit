"""Scrub pending comment notification batches (#1130).

Run this ONCE, immediately after the phase-1 (comments-removal) restart:

    manage.py scrub_comment_notice_batches

Why: pending NoticeQueueBatch rows embed pickled django_comments.Comment
instances that the comment-free code can neither unpickle nor render, and
notification.engine.send_all() blocks on the first failing batch. Migration
core.0031 scrubs these at migrate time, but a comment posted between that
migration and the restart (old code still accepts comment POSTs) can create
one more poisoned batch. Comment ingress ends permanently at the restart, so
a scrub run *after* the restart is definitive.

A wedge in the brief window before this command runs is transient: failed
batches are not consumed, so once the poison batch is deleted here, the next
send_all() run drains the queue normally.

Same restricted-unpickler inspection as migration core.0031 (duplicated
deliberately — migration files must stay frozen/self-contained). Phase 2
(core.0032_drop_comment_tables, PR #1220) carries no copy of this logic: it
only drops the two comment tables, so this command is the LAST line of
defense against a poisoned batch. It keeps working after the tables are
dropped (it never touches them), so it can also clear a batch that slips in
via a phase-1 rollback or a stray old-code host. Remove it only once phase 2
has run everywhere and the queue has been verified clean.

Regression tests: core/test_scrub_comments.py (covers this module's copy of
the inspection logic and the migration's, plus this command end-to-end).
"""

import io
import pickle

from django.core.management.base import BaseCommand

from notification.models import NoticeQueueBatch

COMMENT_NOTICE_TYPES = [
    "comment_on_commented",
    "wishlist_comment",
    "wishlist_official_comment",
]


class _StubbedUnpickler(pickle.Unpickler):
    """Unpickler that never imports application classes."""

    class _Stub:
        def __new__(cls, *args, **kwargs):
            return object.__new__(cls)

        def __init__(self, *args, **kwargs):
            pass

        def __setstate__(self, state):
            pass

        def __call__(self, *args, **kwargs):
            return self

        def append(self, *args, **kwargs):
            pass

        def extend(self, *args, **kwargs):
            pass

    def find_class(self, module, name):
        return self._Stub

    def persistent_load(self, pid):
        return None


def _queues_comment_labels(pickled_data):
    """True/False from label-slot inspection; None if uninspectable.

    "Uninspectable" MUST include any batch whose shape is not exactly what
    queue() writes, not merely one that fails to unpickle. Returning False for a
    non-conforming batch would suppress the caller's byte-scan fallback and
    silently leave a poisoned batch behind; a byte-scan false positive costs one
    pending batch, a false negative wedges the whole notification queue.
    """
    try:
        notices = _StubbedUnpickler(io.BytesIO(pickled_data)).load()
    except Exception:
        return None

    # queue() pickles a list of (user_pk, label, extra_context, on_site, sender)
    if not isinstance(notices, list):
        return None

    for entry in notices:
        if not isinstance(entry, tuple) or len(entry) != 5:
            return None
        label = entry[1]
        if not isinstance(label, str):
            return None
        if label in COMMENT_NOTICE_TYPES:
            return True

    return False


class Command(BaseCommand):
    help = "Delete pending notification batches that queue removed comment notice types (#1130)"

    def handle(self, *args, **options):
        byte_labels = [label.encode() for label in COMMENT_NOTICE_TYPES]
        total = scrubbed = fallback = 0
        for batch in NoticeQueueBatch.objects.all():
            total += 1
            data = bytes(batch.pickled_data)
            verdict = _queues_comment_labels(data)
            if verdict is None:
                verdict = any(label in data for label in byte_labels)
                if verdict:
                    fallback += 1
            if verdict:
                batch.delete()
                scrubbed += 1
        self.stdout.write(
            "batches examined: %d, scrubbed: %d (byte-scan fallback: %d), remaining: %d"
            % (total, scrubbed, fallback, NoticeQueueBatch.objects.count())
        )
