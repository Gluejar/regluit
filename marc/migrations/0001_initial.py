# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MARCRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('guts', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('edition', models.ForeignKey(on_delete=models.CASCADE, related_name='MARCRecords', to='core.Edition', null=True)),
                ('user', models.ForeignKey(on_delete=models.CASCADE, related_name='MARCRecords', to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
