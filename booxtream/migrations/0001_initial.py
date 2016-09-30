# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Boox',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('download_link_epub', models.URLField(null=True)),
                ('download_link_mobi', models.URLField(null=True)),
                ('referenceid', models.CharField(max_length=32)),
                ('downloads_remaining', models.PositiveSmallIntegerField(default=0)),
                ('expirydays', models.PositiveSmallIntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
