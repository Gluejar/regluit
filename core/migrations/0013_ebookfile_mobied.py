# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_campaign_charitable'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebookfile',
            name='mobied',
            field=models.IntegerField(default=0),
        ),
    ]
