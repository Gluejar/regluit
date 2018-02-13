# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20171110_1253'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='charitable',
            field=models.BooleanField(default=False),
        ),
    ]
