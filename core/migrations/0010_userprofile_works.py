# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20170808_0846'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='works',
            field=models.ManyToManyField(related_name='contributors', to='core.Work', blank=True),
        ),
    ]
