# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_userprofile_works'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rightsholder',
            old_name='can_sell',
            new_name='approved',
        ),
        migrations.AddField(
            model_name='rightsholder',
            name='address',
            field=models.CharField(default=b'', max_length=400),
        ),
        migrations.AddField(
            model_name='rightsholder',
            name='mailing',
            field=models.CharField(default=b'', max_length=400),
        ),
        migrations.AddField(
            model_name='rightsholder',
            name='signature',
            field=models.CharField(default=b'', max_length=100),
        ),
        migrations.AddField(
            model_name='rightsholder',
            name='signer',
            field=models.CharField(default=b'', max_length=100),
        ),
        migrations.AddField(
            model_name='rightsholder',
            name='signer_ip',
            field=models.CharField(max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='rightsholder',
            name='signer_title',
            field=models.CharField(default=b'', max_length=30),
        ),
        migrations.AddField(
            model_name='rightsholder',
            name='telephone',
            field=models.CharField(max_length=30, blank=True),
        ),
        migrations.AlterField(
            model_name='rightsholder',
            name='email',
            field=models.CharField(default=b'', max_length=100),
        ),
    ]
