# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20160818_1809'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ebook',
            name='version',
        ),
        migrations.AddField(
            model_name='ebook',
            name='version_iter',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='ebook',
            name='version_label',
            field=models.CharField(default=b'', max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name='edition',
            name='note',
            field=models.ForeignKey(blank=True, to='core.EditionNote', null=True),
        ),
        migrations.AlterField(
            model_name='edition',
            name='publisher_name',
            field=models.ForeignKey(related_name='editions', blank=True, to='core.PublisherName', null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='badges',
            field=models.ManyToManyField(related_name='holders', to='core.Badge', blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='facebook_id',
            field=models.BigIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='work',
            name='age_level',
            field=models.CharField(default=b'', max_length=5, blank=True, choices=[(b'', b'No Rating'), (b'5-6', b"Children's - Kindergarten, Age 5-6"), (b'6-7', b"Children's - Grade 1-2, Age 6-7"), (b'7-8', b"Children's - Grade 2-3, Age 7-8"), (b'8-9', b"Children's - Grade 3-4, Age 8-9"), (b'9-11', b"Children's - Grade 4-6, Age 9-11"), (b'12-14', b'Teen - Grade 7-9, Age 12-14'), (b'15-18', b'Teen - Grade 10-12, Age 15-18'), (b'18-', b'Adult/Advanced Reader')]),
        ),
        migrations.AlterField(
            model_name='work',
            name='openlibrary_lookup',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='work',
            name='publication_range',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
