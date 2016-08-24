# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models

class Migration(migrations.Migration):

    def add_ebooks_to_ebfs(apps, schema_editor):
        EbookFile = apps.get_model('core', 'EbookFile')
        Ebook = apps.get_model('core', 'Ebook')
        for ebf in EbookFile.objects.all():
            for ebook in Ebook.objects.filter(edition=ebf.edition, format=ebf.format).exclude(provider='Unglue.it'):
                ebf.ebook = ebook
                ebf.save()
            for ebook in Ebook.objects.filter(url=ebf.file.url):
                ebf.ebook = ebook
                ebf.save()
            if not ebf.ebook:
                if ebf.edition.work.campaigns.filter(type=3):
                    ebf.ebook = Ebook.objects.create(
                        edition=ebf.edition,
                        active=False,
                        url=ebf.file.url,
                        provider='Unglue.it',
                        format=ebf.format,
                        rights=ebf.edition.work.campaigns.order_by('-created')[0].license
                    )
                    ebf.save()
                elif ebf.edition.work.campaigns.filter(type=2):
                    pass
                else:
                    print 'ebf {} is dangling'.format(ebf.id)
                  
    def noop(apps, schema_editor):
        pass

    dependencies = [
        ('core', '0005_ebookfile_ebook'),
    ]

    operations = [
        migrations.RunPython(add_ebooks_to_ebfs, reverse_code=noop, hints={'core': 'EbookFile'}),
    ]
