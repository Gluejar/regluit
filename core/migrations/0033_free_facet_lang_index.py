# /free/ facet-browse index, language-filtered case (#1253).
#
# Written as RunSQL rather than a plain AddIndex so the DDL on this live table
# is explicit and bounded:
#   * ALGORITHM=INPLACE, LOCK=NONE: MySQL fails the statement instead of
#     silently falling back to a table copy that blocks writes.
#   * SET SESSION lock_wait_timeout: an online CREATE INDEX still needs a brief
#     exclusive metadata lock. If a long-running query or open transaction
#     holds a conflicting lock, the queued request can block later queries on
#     core_work until it is granted. A short timeout makes the migration fail
#     fast instead; rerun it once the blocker is gone.
# One index per migration, so a failure cannot leave a migration half applied.
# state_operations keeps Django's model state identical to Work.Meta.indexes,
# so makemigrations sees no drift.

from django.db import migrations, models

LOCK_WAIT_SECONDS = 10


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_drop_comment_tables'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=[
                        "SET SESSION lock_wait_timeout = %d" % LOCK_WAIT_SECONDS,
                        "CREATE INDEX core_work_free_lang_new_idx ON core_work "
                        "(is_free, language, featured DESC, created DESC) "
                        "ALGORITHM=INPLACE LOCK=NONE",
                        "SET SESSION lock_wait_timeout = DEFAULT",
                    ],
                    reverse_sql=[
                        "SET SESSION lock_wait_timeout = %d" % LOCK_WAIT_SECONDS,
                        "DROP INDEX core_work_free_lang_new_idx ON core_work "
                        "ALGORITHM=INPLACE LOCK=NONE",
                        "SET SESSION lock_wait_timeout = DEFAULT",
                    ],
                ),
            ],
            state_operations=[
                migrations.AddIndex(
                    model_name='work',
                    index=models.Index(
                        fields=['is_free', 'language', '-featured', '-created'],
                        name='core_work_free_lang_new_idx',
                    ),
                ),
            ],
        ),
    ]
