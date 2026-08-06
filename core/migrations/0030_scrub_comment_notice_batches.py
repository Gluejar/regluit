# Phase 1 of the django-contrib-comments removal (#1130): scrub pending
# comment notification batches.
#
# Why this ships WITH the code-removal release: pending NoticeQueueBatch rows
# embed pickled django_comments.Comment instances. Once the app leaves
# INSTALLED_APPS, notification.engine.send_all() can no longer unpickle them
# (model import fails for an uninstalled app), and even a successful unpickle
# would hit the deleted notification templates. send_all() only tolerates
# missing *users*; any other exception escapes past batch.delete() into its
# outer bare `except`, so one poisoned batch permanently blocks every
# subsequent batch — a wedged notification queue.
#
# This migration is deliberately safe under ANY deploy ordering: it only
# deletes queued comment batches, which the old code is perfectly happy
# without, and the tables / notice types it leaves alone are still intact.
# So the deploy guide's §5 flow (migrate before restart) applies unchanged.
#
# Residual window and how it is closed: a comment posted between this
# migration running and the app restart creates one more poisoned batch.
# Ingress ends at the restart (the comment URLs are gone), so the deploy
# sequence for this release finishes with a definitive post-restart scrub:
#
#     manage.py scrub_comment_notice_batches
#
# (same logic as this migration; see the command's docstring). Any wedge in
# the seconds before that command runs is transient — failed batches are not
# consumed, so deleting the poison batch lets the next send_all() drain the
# queue normally. The phase-2 migration (0031) re-runs the scrub once more
# before deleting the notice types, as a final belt.
#
# Batch inspection: a restricted unpickler resolves every class to an inert
# stub (django_comments must not and often cannot be imported) and validates
# the label slot of the queued five-tuples — (user_pk, label, extra_context,
# on_site, sender) — so a comment label appearing in unrelated message text
# does not cause a false positive. A raw byte-scan is the fallback for
# uninspectable pickles: a false positive there discards at worst one pending
# batch; a false negative would wedge the whole queue.

import io
import pickle

from django.db import migrations

COMMENT_NOTICE_TYPES = [
    "comment_on_commented",
    "wishlist_comment",
    "wishlist_official_comment",
]


class _StubbedUnpickler(pickle.Unpickler):
    """Unpickler that never imports application classes.

    Every GLOBAL/STACK_GLOBAL resolves to an inert stub, so the queued
    five-tuples' *structure* (ints and strings survive as-is) can be
    inspected without importing django_comments or executing any
    class-specific reduce logic.
    """

    class _Stub:
        def __new__(cls, *args, **kwargs):
            return object.__new__(cls)

        def __init__(self, *args, **kwargs):
            pass

        def __setstate__(self, state):
            pass

        def __call__(self, *args, **kwargs):
            return self

        def append(self, *args, **kwargs):  # list-like BUILD paths
            pass

        def extend(self, *args, **kwargs):
            pass

    def find_class(self, module, name):
        return self._Stub

    def persistent_load(self, pid):
        return None


def _queues_comment_labels(pickled_data):
    """Return whether the batch queues any comment-label notices.

    Returns True/False from precise inspection of the label slot, or None
    if the pickle cannot be inspected.
    """
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


def scrub_queued_comment_batches(apps, schema_editor):
    NoticeQueueBatch = apps.get_model("notification", "NoticeQueueBatch")
    byte_labels = [label.encode() for label in COMMENT_NOTICE_TYPES]
    for batch in NoticeQueueBatch.objects.all():
        data = bytes(batch.pickled_data)
        verdict = _queues_comment_labels(data)
        if verdict is None:
            # Uninspectable pickle: conservative byte-scan fallback.
            verdict = any(label in data for label in byte_labels)
        if verdict:
            batch.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_auto_20241122_1525'),
        ('notification', '0002_auto_20200215_1821'),
    ]

    operations = [
        migrations.RunPython(
            scrub_queued_comment_batches,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
