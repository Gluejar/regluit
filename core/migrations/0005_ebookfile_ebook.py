# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20160808_1548'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebookfile',
            name='ebook',
            field=models.ForeignKey(related_name='ebook_files', to='core.Ebook', null=True),
        ),
    ]
