# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2024-11-22 15:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_auto_20240819_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subject',
            name='name',
            field=models.CharField(db_index=True, max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='work',
            name='is_free',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]