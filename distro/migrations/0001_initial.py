# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Deposit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('isbn', models.CharField(max_length=13)),
                ('format', models.CharField(max_length=30)),
                ('updated', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Format',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='Target',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('host', models.CharField(max_length=60)),
                ('pw', models.CharField(max_length=30)),
                ('user', models.CharField(max_length=30)),
                ('protocol', models.CharField(default=b'ftp', max_length=10)),
                ('formats', models.ManyToManyField(related_name='targets', to='distro.Format')),
            ],
        ),
        migrations.AddField(
            model_name='deposit',
            name='target',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='deposits', to='distro.Target'),
        ),
    ]
