# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20180618_1646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='avatar_source',
            field=models.PositiveSmallIntegerField(default=4, null=True, choices=[(0, b'No Avatar, Please'), (1, b'Gravatar'), (2, b'Twitter/Facebook'), (4, b'Unglueitar')]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='facebook_id',
            field=models.CharField(default='', max_length=31, blank=True),
            preserve_default=False,
        ),
    ]
