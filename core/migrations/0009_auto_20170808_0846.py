# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20161109_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebookfile',
            name='source',
            field=models.URLField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='status',
            field=models.CharField(default=b'INITIALIZED', max_length=15, null=True, db_index=True, choices=[(b'INITIALIZED', b'INITIALIZED'), (b'ACTIVE', b'ACTIVE'), (b'SUSPENDED', b'SUSPENDED'), (b'WITHDRAWN', b'WITHDRAWN'), (b'SUCCESSFUL', b'SUCCESSFUL'), (b'UNSUCCESSFUL', b'UNSUCCESSFUL')]),
        ),
    ]
