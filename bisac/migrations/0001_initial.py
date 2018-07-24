# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BisacHeading',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('full_label', models.CharField(unique=True, max_length=100)),
                ('label', models.CharField(max_length=60)),
                ('notation', models.CharField(max_length=9)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(on_delete=models.CASCADE, related_name='children', blank=True, to='bisac.BisacHeading', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
