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

Same restricted-unpickler inspection as migrations core.0031/core.0032
(duplicated deliberately — migration files must stay frozen/self-contained).
This command is interphase tooling and can be removed after phase 2
(core.0032) has run everywhere.
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
    """True/False from label-slot inspection; None if uninspectable."""
    try:
        notices = _StubbedUnpickler(io.BytesIO(pickled_data)).load()
        labels = set()
        for entry in notices:
            # queue() writes (user_pk, label, extra_context, on_site, sender)
            if isinstance(entry, (tuple, list)) and len(entry) >= 2:
                labels.add(entry[1])
        return bool(labels & set(COMMENT_NOTICE_TYPES))
    except Exception:
        return None


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
