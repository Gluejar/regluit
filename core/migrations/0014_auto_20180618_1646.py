# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_ebookfile_mobied'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workrelation',
            name='relation',
            field=models.CharField(max_length=15, choices=[(b'translation', b'translation'), (b'revision', b'revision'), (b'sequel', b'sequel'), (b'part', b'part')]),
        ),
    ]
