# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20160923_1314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='work',
            name='related',
            field=models.ManyToManyField(related_name='reverse_related', through='core.WorkRelation', to='core.Work', blank=True),
        ),
    ]
