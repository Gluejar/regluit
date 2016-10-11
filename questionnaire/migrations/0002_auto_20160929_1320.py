# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Run',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('runid', models.CharField(max_length=32, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='answer',
            name='run',
            field=models.ForeignKey(related_name='answers', to='questionnaire.Run', null=True),
        ),
        migrations.AddField(
            model_name='runinfo',
            name='run',
            field=models.ForeignKey(related_name='run_infos', to='questionnaire.Run', null=True),
        ),
        migrations.AddField(
            model_name='runinfohistory',
            name='run',
            field=models.ForeignKey(related_name='run_info_histories', to='questionnaire.Run', null=True),
        ),
    ]
