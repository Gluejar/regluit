# /free/ facet-browse index, no-language case (#1253).
#
# Same approach as 0033 (see its header): RunSQL with explicit online-DDL
# clauses and a short lock wait, one index per migration, and matching
# state_operations so Django's model state stays in sync.

from django.db import migrations, models

LOCK_WAIT_SECONDS = 10


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_free_facet_lang_index'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=[
                        "SET SESSION lock_wait_timeout = %d" % LOCK_WAIT_SECONDS,
                        "CREATE INDEX core_work_free_new_idx ON core_work "
                        "(is_free, featured DESC, created DESC) "
                        "ALGORITHM=INPLACE LOCK=NONE",
                        "SET SESSION lock_wait_timeout = DEFAULT",
                    ],
                    reverse_sql=[
                        "SET SESSION lock_wait_timeout = %d" % LOCK_WAIT_SECONDS,
                        "DROP INDEX core_work_free_new_idx ON core_work "
                        "ALGORITHM=INPLACE LOCK=NONE",
                        "SET SESSION lock_wait_timeout = DEFAULT",
                    ],
                ),
            ],
            state_operations=[
                migrations.AddIndex(
                    model_name='work',
                    index=models.Index(
                        fields=['is_free', '-featured', '-created'],
                        name='core_work_free_new_idx',
                    ),
                ),
            ],
        ),
    ]
