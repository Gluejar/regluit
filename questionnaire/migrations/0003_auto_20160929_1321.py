# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def models_to_migrate(apps):
    return [
        apps.get_model('questionnaire', 'RunInfo'),
        apps.get_model('questionnaire', 'RunInfoHistory'),
        apps.get_model('questionnaire', 'Answer'),
    ]

class Migration(migrations.Migration):
        
    def move_runids(apps, schema_editor):
        Run = apps.get_model('questionnaire', 'Run')
        for model in models_to_migrate(apps):
            for instance in model.objects.all():
                (run, created) = Run.objects.get_or_create(runid=instance.runid)
                instance.run = run
                instance.save()

    def unmove_runids(apps, schema_editor):
        for model in models_to_migrate(apps):
            for instance in model.objects.all():
                instance.runid = instance.run.runid
                instance.save()
                
    dependencies = [
        ('questionnaire', '0002_auto_20160929_1320'),
    ]

    operations = [
       migrations.RunPython(move_runids, reverse_code=unmove_runids, hints={'questionnaire': 'Run'}),
    ]
