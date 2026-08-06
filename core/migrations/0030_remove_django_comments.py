# Remove django-contrib-comments (#1130).
#
# The app has been removed from INSTALLED_APPS, so its tables are orphaned.
# Per Eric's decision (spam magnet, low-value content), the data is dropped
# rather than archived; the pre-deploy RDS snapshot is the recovery path.
#
# Also removes the three comment-related NoticeType rows so they no longer
# appear on users' notification-settings pages. Deleting via the ORM (rather
# than raw SQL) lets the delete cascade to NoticeSetting / Notice /
# ObservedItem rows, which carry RESTRICT foreign keys at the DB level.
#
# Note: stale rows for the 'django_comments' app remain in django_migrations;
# they are inert and can be cleaned up later with `migrate --prune` if desired.

from django.db import migrations

COMMENT_NOTICE_TYPES = [
    "comment_on_commented",
    "wishlist_comment",
    "wishlist_official_comment",
]


def delete_comment_notice_types(apps, schema_editor):
    NoticeType = apps.get_model("notification", "NoticeType")
    for notice_type in NoticeType.objects.filter(label__in=COMMENT_NOTICE_TYPES):
        notice_type.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_auto_20241122_1525'),
        ('notification', '0002_auto_20200215_1821'),
    ]

    operations = [
        migrations.RunPython(
            delete_comment_notice_types,
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
