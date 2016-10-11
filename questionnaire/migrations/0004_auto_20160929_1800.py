# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0003_auto_20160929_1321'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='runinfo',
            name='runid',
        ),
        migrations.RemoveField(
            model_name='runinfohistory',
            name='runid',
        ),
        migrations.AlterField(
            model_name='answer',
            name='run',
            field=models.ForeignKey(related_name='answers', default=1, to='questionnaire.Run'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='runinfo',
            name='run',
            field=models.ForeignKey(related_name='run_infos', default=1, to='questionnaire.Run'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='runinfohistory',
            name='run',
            field=models.ForeignKey(related_name='run_info_histories', to='questionnaire.Run'),
        ),
        migrations.AlterIndexTogether(
            name='answer',
            index_together=set([('subject', 'run'), ('subject', 'run', 'id')]),
        ),
        migrations.RemoveField(
            model_name='answer',
            name='runid',
        ),
    ]
