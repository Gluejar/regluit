# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import regluit.libraryauth.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lower', regluit.libraryauth.models.IPAddressModelField(unique=True, db_index=True)),
                ('upper', regluit.libraryauth.models.IPAddressModelField(db_index=True, null=True, blank=True)),
            ],
            options={
                'ordering': ['lower'],
            },
        ),
        migrations.CreateModel(
            name='CardPattern',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pattern', models.CharField(max_length=20)),
                ('checksum', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='EmailPattern',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pattern', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Library',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('backend', models.CharField(default=b'ip', max_length=10, choices=[(b'ip', b'IP authentication'), (b'cardnum', b'Library Card Number check'), (b'email', b'e-mail pattern check')])),
                ('name', models.CharField(default=b'', max_length=80)),
                ('approved', models.BooleanField(default=False)),
                ('group', models.OneToOneField(on_delete=models.CASCADE, related_name='library', null=True, to='auth.Group')),
                ('owner', models.ForeignKey(on_delete=models.CASCADE, related_name='libraries', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(on_delete=models.CASCADE, related_name='library', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LibraryUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('credential', models.CharField(max_length=30, null=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('library', models.ForeignKey(on_delete=models.CASCADE, related_name='library_users', to='libraryauth.Library')),
                ('user', models.ForeignKey(on_delete=models.CASCADE, related_name='user_libraries', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='emailpattern',
            name='library',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='email_auths', to='libraryauth.Library'),
        ),
        migrations.AddField(
            model_name='cardpattern',
            name='library',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='cardnum_auths', to='libraryauth.Library'),
        ),
        migrations.AddField(
            model_name='block',
            name='library',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='ip_auths', to='libraryauth.Library'),
        ),
    ]
