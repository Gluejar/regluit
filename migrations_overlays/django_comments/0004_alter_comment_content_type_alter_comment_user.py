# regluit overlay migration — records explicit on_delete values that
# django-contrib-comments's own migration history never recorded.
#
# Why this exists:
#   The django_comments Comment model has declared
#     content_type = ForeignKey(..., on_delete=CASCADE)
#     user         = ForeignKey(..., on_delete=SET_NULL)
#   since at least django-contrib-comments 1.x. But the package's shipped
#   migration files (0001-0003) were generated under Django 1.x, which
#   didn't require on_delete in migration operations. When Django 4.x
#   introspects the current model vs. migration state, it sees the mismatch
#   and complains on every `makemigrations --check` run.
#
# Applying this migration is a **state-tracker no-op**. Verified on
# dj42.unglue.it with `sqlmigrate`:
#
#     -- Alter field content_type on comment
#     -- (no-op)
#     -- Alter field user on comment
#     -- (no-op)
#
# The actual MySQL FOREIGN KEY constraints are untouched (stay as
# ON DELETE RESTRICT, which is what Django 1.x created when the tables
# were first set up). Django's ORM-layer cascade logic (driven by the
# Python model's on_delete values) already produces the correct runtime
# behavior — it deletes children in Python before the parent DELETE hits
# the DB — so the DB-level constraint is inert under normal ORM usage.
#
# Upstream tracking: django-contrib-comments 2.2.0 (Jan 2022) was the
# latest release at the time this was filed and did not include this fix.
# If/when the upstream package ships an equivalent migration, this overlay
# should be reconciled (likely: drop this file and let the upstream one
# take over, since migration names will match).

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('django_comments', '0003_add_submit_date_index'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='content_type',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='content_type_set_for_%(class)s',
                to='contenttypes.contenttype',
                verbose_name='content type',
            ),
        ),
        migrations.AlterField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='%(class)s_comments',
                to=settings.AUTH_USER_MODEL,
                verbose_name='user',
            ),
        ),
    ]
