# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2023-04-12 14:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0004_auto_20160929_1800'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='answer',
            index_together=set([]),
        ),
        migrations.RemoveField(
            model_name='answer',
            name='question',
        ),
        migrations.RemoveField(
            model_name='answer',
            name='run',
        ),
        migrations.RemoveField(
            model_name='answer',
            name='subject',
        ),
        migrations.AlterIndexTogether(
            name='choice',
            index_together=set([]),
        ),
        migrations.RemoveField(
            model_name='choice',
            name='question',
        ),
        migrations.DeleteModel(
            name='DBStylesheet',
        ),
        migrations.DeleteModel(
            name='GlobalStyles',
        ),
        migrations.AlterIndexTogether(
            name='question',
            index_together=set([]),
        ),
        migrations.RemoveField(
            model_name='question',
            name='questionset',
        ),
        migrations.AlterIndexTogether(
            name='questionset',
            index_together=set([]),
        ),
        migrations.RemoveField(
            model_name='questionset',
            name='questionnaire',
        ),
        migrations.AlterIndexTogether(
            name='runinfo',
            index_together=set([]),
        ),
        migrations.RemoveField(
            model_name='runinfo',
            name='landing',
        ),
        migrations.RemoveField(
            model_name='runinfo',
            name='questionset',
        ),
        migrations.RemoveField(
            model_name='runinfo',
            name='run',
        ),
        migrations.RemoveField(
            model_name='runinfo',
            name='subject',
        ),
        migrations.RemoveField(
            model_name='runinfohistory',
            name='landing',
        ),
        migrations.RemoveField(
            model_name='runinfohistory',
            name='questionnaire',
        ),
        migrations.RemoveField(
            model_name='runinfohistory',
            name='run',
        ),
        migrations.RemoveField(
            model_name='runinfohistory',
            name='subject',
        ),
        migrations.DeleteModel(
            name='Subject',
        ),
        migrations.RemoveField(
            model_name='landing',
            name='questionnaire',
        ),
        migrations.DeleteModel(
            name='Answer',
        ),
        migrations.DeleteModel(
            name='Choice',
        ),
        migrations.DeleteModel(
            name='Question',
        ),
        migrations.DeleteModel(
            name='Questionnaire',
        ),
        migrations.DeleteModel(
            name='QuestionSet',
        ),
        migrations.DeleteModel(
            name='Run',
        ),
        migrations.DeleteModel(
            name='RunInfo',
        ),
        migrations.DeleteModel(
            name='RunInfoHistory',
        ),
    ]
