# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20160722_1716'),
    ]

    operations = [
        migrations.CreateModel(
            name='EditionNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('note', models.CharField(max_length=64, unique=True, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='WorkRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('relation', models.CharField(max_length=15, choices=[(b'translation', b'translation'), (b'revision', b'revision'), (b'sequel', b'sequel'), (b'compilation', b'compilation')])),
            ],
        ),
        migrations.AddField(
            model_name='ebook',
            name='version',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='work',
            name='age_level',
            field=models.CharField(default=b'', max_length=5, choices=[(b'', b'No Rating'), (b'5-6', b"Children's - Kindergarten, Age 5-6"), (b'6-7', b"Children's - Grade 1-2, Age 6-7"), (b'7-8', b"Children's - Grade 2-3, Age 7-8"), (b'8-9', b"Children's - Grade 3-4, Age 8-9"), (b'9-11', b"Children's - Grade 4-6, Age 9-11"), (b'12-14', b'Teen - Grade 7-9, Age 12-14'), (b'15-18', b'Teen - Grade 10-12, Age 15-18'), (b'18-', b'Adult/Advanced Reader')]),
        ),
        migrations.AddField(
            model_name='workrelation',
            name='from_work',
            field=models.ForeignKey(related_name='works_related_from', to='core.Work'),
        ),
        migrations.AddField(
            model_name='workrelation',
            name='to_work',
            field=models.ForeignKey(related_name='works_related_to', to='core.Work'),
        ),
        migrations.AddField(
            model_name='edition',
            name='note',
            field=models.ForeignKey(to='core.EditionNote', null=True),
        ),
        migrations.AddField(
            model_name='work',
            name='related',
            field=models.ManyToManyField(related_name='reverse_related', null=True, through='core.WorkRelation', to='core.Work'),
        ),
    ]
