# -*- coding: utf-8 -*-
# Migration: Re-parent IPAddressModelField from GenericIPAddressField to PositiveIntegerField.
#
# This is a no-op at the database level — the column was already stored as
# PositiveIntegerField because the old IPAddressModelField.get_internal_type()
# returned "PositiveIntegerField". We're just updating Django's migration state
# to reflect the new (correct) field class hierarchy.

from django.db import migrations
import regluit.libraryauth.models


class Migration(migrations.Migration):

    dependencies = [
        ('libraryauth', '0004_auto_20200214_1347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='block',
            name='lower',
            field=regluit.libraryauth.models.IPAddressModelField(db_index=True, unique=True),
        ),
        migrations.AlterField(
            model_name='block',
            name='upper',
            field=regluit.libraryauth.models.IPAddressModelField(blank=True, db_index=True, null=True),
        ),
    ]
