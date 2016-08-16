# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models, transaction
from django.db.utils import IntegrityError


class Migration(migrations.Migration):
    
    def url_to_doi(apps, schema_editor):
        Indentifier = apps.get_model('core', 'Identifier')
        for doi in Indentifier.objects.filter(type='http', value__icontains='dx.doi.org'):
            if doi.value.startswith('http://dx.doi.org/10.'):
                doi.value = doi.value[18:]
            elif doi.value.startswith('https://dx.doi.org/10.'):
                doi.value = doi.value[19:]
            else:
                continue
            doi.type = 'doi'
            try:
                with transaction.atomic():
                    doi.save()
            except IntegrityError:
                continue
        
    def doi_to_url(apps, schema_editor):
        Indentifier = apps.get_model('core', 'Identifier')
        for doi in Indentifier.objects.filter(type='doi'):
            doi.value = 'https://dx.doi.org/{}'.format(doi.value)
            doi.type = 'http'
            try:
                with transaction.atomic():
                    doi.save()
            except IntegrityError:
                continue
        
        
    dependencies = [
        ('core', '0003_auto_20160816_1645'),
    ]

    operations = [
        migrations.RunPython(url_to_doi, reverse_code=doi_to_url, hints={'core': 'Identifier'}),
    ]
