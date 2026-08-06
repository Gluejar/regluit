# Remove django-contrib-comments (#1130).
#
# ⚠️ DEPLOY ORDER: run this migration only AFTER the new code is deployed and
# ALL Python processes restarted (apache2, celeryd, celerybeat — i.e. after the
# deploy.yml hotfix flow completes). Old in-memory code still queries the
# comment tables (homepage feed, work merge/delete); dropping the tables under
# it would 500 those paths until restart. The provisioning deploy.yml
# deliberately does not run migrations, so the safe order is natural:
# deploy + restart first, migrate second.
#
# The app has been removed from INSTALLED_APPS, so its tables are orphaned.
# Per Eric's decision (spam magnet, low-value content), the data is dropped
# rather than archived; the pre-deploy RDS snapshot is the recovery path.
#
# What this migration does, in order:
#
# 1. Deletes any pending NoticeQueueBatch rows that carry comment notices.
#    Rationale: notification.engine.send_all() only tolerates missing *users*;
#    a missing NoticeType raises into its outer bare `except`, the batch is
#    never deleted, and every subsequent batch is blocked on every run — a
#    permanently wedged notification queue. Batches are matched by byte-scan
#    for the comment labels rather than by unpickling, because the pickles
#    embed django_comments.Comment instances and unpickling would require the
#    very package being removed. Each queue() call produces a single-label
#    batch, so deleting a matching batch cannot discard unrelated notices.
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
# Note: stale rows for the 'django_comments' app remain in django_migrations;
# they are inert and can be cleaned up later with `migrate --prune` if desired.

from django.db import migrations

COMMENT_NOTICE_TYPES = [
    "comment_on_commented",
    "wishlist_comment",
    "wishlist_official_comment",
]


def scrub_queued_comment_batches(apps, schema_editor):
    NoticeQueueBatch = apps.get_model("notification", "NoticeQueueBatch")
    labels = [label.encode() for label in COMMENT_NOTICE_TYPES]
    for batch in NoticeQueueBatch.objects.all():
        data = bytes(batch.pickled_data)
        if any(label in data for label in labels):
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
        ('core', '0029_auto_20241122_1525'),
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
