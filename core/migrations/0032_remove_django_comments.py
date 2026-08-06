# Remove django-contrib-comments data (#1130) — PHASE 2 of the removal.
#
# Step 1 below re-runs the phase-1 batch scrub (core.0031) verbatim: it
# catches any straggler batch created in phase 1's migrate-to-restart window
# (comment ingress only ends at the phase-1 restart). Idempotent either way.
#
# ⚠️ MERGE/DEPLOY GATE: this migration ships as its own release, AFTER the
# comment-free code release (PR: remove-comments-1130) has been deployed and
# every Python process restarted (apache2, celeryd, celerybeat) on the target
# box. That ordering is what makes it safe on every deploy path — deploy.yml,
# the deploy guide's §5 chained flow, or a full setup-*.yml provision — since
# by then no running code references the comment tables or notice types, and
# comment ingress (which could re-poison the notification queue) has ended.
#
# The app is gone from INSTALLED_APPS, so its tables are orphaned. Per Eric's
# decision (spam magnet, low-value content), the data is dropped rather than
# archived; the pre-deploy RDS snapshot is the recovery path.
#
# What this migration does, in order:
#
# 1. Deletes any pending NoticeQueueBatch rows that carry comment notices.
#    Rationale: notification.engine.send_all() only tolerates missing *users*;
#    a missing NoticeType raises into its outer bare `except`, the batch is
#    never deleted, and every subsequent batch is blocked on every run — a
#    permanently wedged notification queue. Batches are inspected with a
#    restricted unpickler that stubs out classes (the pickles embed
#    django_comments.Comment instances, and importing the removed package is
#    neither possible nor safe), and a batch is deleted only when the label
#    slot of a queued five-tuple holds a comment label. If a batch cannot be
#    unpickled at all, we fall back to a byte-scan for the labels and delete
#    on match — a false positive there discards at worst one pending
#    notification batch; a false negative would wedge the whole queue.
#
# 2. Deletes the three comment NoticeType rows via the ORM so the delete
#    cascades to NoticeSetting / Notice / ObservedItem rows (RESTRICT FKs at
#    the MySQL level; the ORM collector deletes children first).
#
# 3. Deletes the stale django_comments ContentType rows (cascades to their
#    auth_permission rows) so no dead metadata lingers in the admin.
#
# 4. Drops django_comment_flags then django_comments (FK ordering).
#
# Notes:
# - Stale rows for the 'django_comments' app remain in django_migrations;
#   inert, cleanable later with `migrate --prune`.
# - `pip install -r requirements.txt` does not uninstall packages, so the
#   django-contrib-comments distribution stays (inert) in existing venvs
#   until a venv rebuild; nothing imports it after phase 1.

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


def _queued_comment_labels(pickled_data):
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
        verdict = _queued_comment_labels(data)
        if verdict is None:
            # Uninspectable pickle: conservative byte-scan fallback.
            verdict = any(label in data for label in byte_labels)
        if verdict:
            batch.delete()


def delete_comment_notice_types(apps, schema_editor):
    NoticeType = apps.get_model("notification", "NoticeType")
    for notice_type in NoticeType.objects.filter(label__in=COMMENT_NOTICE_TYPES):
        notice_type.delete()


def delete_comment_content_types(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    for content_type in ContentType.objects.filter(app_label="django_comments"):
        content_type.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_scrub_comment_notice_batches'),
        ('notification', '0002_auto_20200215_1821'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RunPython(
            scrub_queued_comment_batches,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunPython(
            delete_comment_notice_types,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunPython(
            delete_comment_content_types,
            reverse_code=migrations.RunPython.noop,
        ),
        # django_comment_flags carries a foreign key to django_comments,
        # so it must be dropped first.
        migrations.RunSQL(
            sql=[
                "DROP TABLE IF EXISTS django_comment_flags;",
                "DROP TABLE IF EXISTS django_comments;",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
