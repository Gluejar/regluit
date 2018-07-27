# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('libraryauth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('booxtream', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='hold',
            name='library',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='holds', to='libraryauth.Library'),
        ),
        migrations.AddField(
            model_name='hold',
            name='user',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='holds', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='hold',
            name='work',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='holds', to='core.Work'),
        ),
        migrations.AddField(
            model_name='gift',
            name='acq',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='gifts', to='core.Acq'),
        ),
        migrations.AddField(
            model_name='gift',
            name='giver',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='gifts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='edition',
            name='publisher_name',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='editions', to='core.PublisherName', null=True),
        ),
        migrations.AddField(
            model_name='edition',
            name='work',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='editions', to='core.Work', null=True),
        ),
        migrations.AddField(
            model_name='ebookfile',
            name='edition',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='ebook_files', to='core.Edition'),
        ),
        migrations.AddField(
            model_name='ebook',
            name='edition',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='ebooks', to='core.Edition'),
        ),
        migrations.AddField(
            model_name='ebook',
            name='user',
            field=models.ForeignKey(on_delete=models.CASCADE, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='claim',
            name='rights_holder',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='claim', to='core.RightsHolder'),
        ),
        migrations.AddField(
            model_name='claim',
            name='user',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='claim', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='claim',
            name='work',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='claim', to='core.Work'),
        ),
        migrations.AddField(
            model_name='celerytask',
            name='user',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='tasks', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='campaignaction',
            name='campaign',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='actions', to='core.Campaign'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='edition',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='campaigns', to='core.Edition', null=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='managers',
            field=models.ManyToManyField(related_name='campaigns', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='campaign',
            name='publisher',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='campaigns', to='core.Publisher', null=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='work',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='campaigns', to='core.Work'),
        ),
        migrations.AddField(
            model_name='author',
            name='editions',
            field=models.ManyToManyField(related_name='authors', through='core.Relator', to='core.Edition'),
        ),
        migrations.AddField(
            model_name='acq',
            name='lib_acq',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='loans', to='core.Acq', null=True),
        ),
        migrations.AddField(
            model_name='acq',
            name='user',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='acqs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='acq',
            name='watermarked',
            field=models.ForeignKey(on_delete=models.CASCADE, to='booxtream.Boox', null=True),
        ),
        migrations.AddField(
            model_name='acq',
            name='work',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='acqs', to='core.Work'),
        ),
        migrations.AlterUniqueTogether(
            name='identifier',
            unique_together=set([('type', 'value')]),
        ),
    ]
