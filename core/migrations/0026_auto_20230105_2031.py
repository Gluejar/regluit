# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2023-01-05 20:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_remove_ebookfile_mobied'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='twitter_id',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='avatar_source',
            field=models.PositiveSmallIntegerField(choices=[(0, 'No Avatar, Please'), (1, 'Gravatar'), (4, 'Unglueitar')], default=4, null=True),
        ),
    ]