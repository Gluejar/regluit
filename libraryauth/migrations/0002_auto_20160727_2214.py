# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models

#import social

# this migration repaired the state of our database so that social auth migrations can be applied
# after application, it should never do anything more

class Migration(migrations.Migration):

    dependencies =[
        ('libraryauth', '0001_initial'),
    ]

    operations = [] if settings.TESTING else  [
#        migrations.CreateModel(
#            name='Code',
#            fields=[
#                ('id', models.AutoField(
#                    verbose_name='ID', serialize=False, auto_created=True,
#                    primary_key=True)),
#                ('email', models.EmailField(max_length=75)),
#                ('code', models.CharField(max_length=32, db_index=True)),
#                ('verified', models.BooleanField(default=False)),
#            ],
#            options={
#                'db_table': 'social_auth_code',
#            },
#            bases=(models.Model, social.storage.django_orm.DjangoCodeMixin),
#        ),
    ]
