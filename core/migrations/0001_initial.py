# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ckeditor.fields
import regluit.core.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Acq',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('expires', models.DateTimeField(null=True)),
                ('refreshes', models.DateTimeField(auto_now_add=True)),
                ('refreshed', models.BooleanField(default=True)),
                ('license', models.PositiveSmallIntegerField(default=1, choices=[(1, b'Individual license'), (2, b'Library License'), (3, b'Borrowed from Library'), (0, b'Just for Testing'), (4, b'On Reserve'), (5, b'Already Thanked')])),
                ('nonce', models.CharField(max_length=32, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=72, blank=True)),
                ('description', models.TextField(default=b'', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=500, null=True)),
                ('description', ckeditor.fields.RichTextField(null=True)),
                ('details', ckeditor.fields.RichTextField(null=True, blank=True)),
                ('target', models.DecimalField(default=0.0, null=True, max_digits=14, decimal_places=2)),
                ('license', models.CharField(default=b'CC BY-NC-ND', max_length=255, choices=[(b'CC BY-NC-ND', b'Creative Commons Attribution-NonCommercial-NoDerivs 3.0 Unported (CC BY-NC-ND 3.0)'), (b'CC BY-NC-SA', b'Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported (CC BY-NC-SA 3.0)'), (b'CC BY-NC', b'Creative Commons Attribution-NonCommercial 3.0 Unported (CC BY-NC 3.0)'), (b'CC BY-ND', b'Creative Commons Attribution-NoDerivs 3.0 Unported (CC BY-ND 3.0)'), (b'CC BY-SA', b'Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)'), (b'CC BY', b'Creative Commons Attribution 3.0 Unported (CC BY 3.0)'), (b'CC0', b'No Rights Reserved (CC0)'), (b'GFDL', b'GNU Free Documentation License'), (b'LAL', b'Licence Art Libre'), (b'OSI', b'OSI Approved License')])),
                ('left', models.DecimalField(null=True, max_digits=14, decimal_places=2, db_index=True)),
                ('deadline', models.DateTimeField(null=True, db_index=True)),
                ('dollar_per_day', models.FloatField(null=True)),
                ('cc_date_initial', models.DateTimeField(null=True)),
                ('activated', models.DateTimeField(null=True, db_index=True)),
                ('paypal_receiver', models.CharField(max_length=100, blank=True)),
                ('amazon_receiver', models.CharField(max_length=100, blank=True)),
                ('status', models.CharField(default=b'INITIALIZED', max_length=15, null=True, db_index=True)),
                ('type', models.PositiveSmallIntegerField(default=1, choices=[(1, b'Pledge-to-unglue campaign'), (2, b'Buy-to-unglue campaign'), (3, b'Thanks-for-ungluing campaign')])),
                ('email', models.CharField(max_length=100, blank=True)),
                ('do_watermark', models.BooleanField(default=True)),
                ('use_add_ask', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='CampaignAction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(max_length=15)),
                ('comment', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='CeleryTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('task_id', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=2048, null=True)),
                ('function_name', models.CharField(max_length=1024)),
                ('function_args', models.IntegerField(null=True)),
                ('active', models.NullBooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Claim',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default=b'active', max_length=7, choices=[('active', 'Claim has been accepted.'), ('pending', 'Claim is pending acceptance.'), ('release', 'Claim has not been accepted.')])),
            ],
        ),
        migrations.CreateModel(
            name='Ebook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(max_length=1024)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('format', models.CharField(max_length=25, choices=[(b'pdf', b'PDF'), (b'epub', b'EPUB'), (b'html', b'HTML'), (b'text', b'TEXT'), (b'mobi', b'MOBI')])),
                ('provider', models.CharField(max_length=255)),
                ('download_count', models.IntegerField(default=0)),
                ('active', models.BooleanField(default=True)),
                ('filesize', models.PositiveIntegerField(null=True)),
                ('rights', models.CharField(db_index=True, max_length=255, null=True, choices=[(b'CC BY-NC-ND', b'Creative Commons Attribution-NonCommercial-NoDerivs'), (b'CC BY-NC-SA', b'Creative Commons Attribution-NonCommercial-ShareAlike'), (b'CC BY-NC', b'Creative Commons Attribution-NonCommercial'), (b'CC BY-ND', b'Creative Commons Attribution-NoDerivs'), (b'CC BY-SA', b'Creative Commons Attribution-ShareAlike'), (b'CC BY', b'Creative Commons Attribution'), (b'CC0', b'No Rights Reserved (CC0)'), (b'GFDL', b'GNU Free Documentation License'), (b'LAL', b'Licence Art Libre'), (b'OSI', b'OSI Approved License'), (b'PD-US', b'Public Domain, US')])),
            ],
        ),
        migrations.CreateModel(
            name='EbookFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=regluit.core.models.path_for_file)),
                ('format', models.CharField(max_length=25, choices=[(b'pdf', b'PDF'), (b'epub', b'EPUB'), (b'html', b'HTML'), (b'text', b'TEXT'), (b'mobi', b'MOBI')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('asking', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Edition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=1000)),
                ('publication_date', models.CharField(db_index=True, max_length=50, null=True, blank=True)),
                ('cover_image', models.URLField(null=True, blank=True)),
                ('unglued', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Gift',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('to', models.CharField(max_length=75, blank=True)),
                ('message', models.TextField(default=b'', max_length=512)),
                ('used', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Hold',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Identifier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=4)),
                ('value', models.CharField(max_length=250)),
                ('edition', models.ForeignKey(on_delete=models.CASCADE, related_name='identifiers', to='core.Edition', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Key',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('encrypted_value', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Libpref',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('marc_link_target', models.CharField(default=b'UNGLUE', max_length=6, verbose_name=b'MARC record link targets', choices=[(b'DIRECT', b'Raw link'), (b'UNGLUE', b'Unglue.it link')])),
                ('user', models.OneToOneField(on_delete=models.CASCADE, related_name='libpref', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price', models.DecimalField(null=True, max_digits=6, decimal_places=2)),
                ('license', models.PositiveSmallIntegerField(default=1, choices=[(1, b'Individual license'), (2, b'Library License')])),
                ('active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Premium',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(max_length=2, choices=[('00', 'Default'), ('CU', 'Custom'), ('XX', 'Inactive')])),
                ('amount', models.DecimalField(max_digits=10, decimal_places=0)),
                ('description', models.TextField(null=True)),
                ('limit', models.IntegerField(default=0)),
                ('campaign', models.ForeignKey(on_delete=models.CASCADE, related_name='premiums', to='core.Campaign', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Press',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField()),
                ('title', models.CharField(max_length=140)),
                ('source', models.CharField(max_length=140)),
                ('date', models.DateField(db_index=True)),
                ('language', models.CharField(max_length=20, blank=True)),
                ('highlight', models.BooleanField(default=False)),
                ('note', models.CharField(max_length=140, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('url', models.URLField(max_length=1024, null=True, blank=True)),
                ('logo_url', models.URLField(max_length=1024, null=True, blank=True)),
                ('description', models.TextField(default=b'', null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='PublisherName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('publisher', models.ForeignKey(on_delete=models.CASCADE, related_name='alternate_names', to='core.Publisher', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(unique=True, max_length=3, db_index=True)),
                ('name', models.CharField(max_length=30, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Relator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('author', models.ForeignKey(on_delete=models.CASCADE, to='core.Author')),
                ('edition', models.ForeignKey(on_delete=models.CASCADE, related_name='relators', to='core.Edition')),
                ('relation', models.ForeignKey(on_delete=models.CASCADE, default=1, to='core.Relation')),
            ],
            options={
                'db_table': 'core_author_editions',
            },
        ),
        migrations.CreateModel(
            name='RightsHolder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('email', models.CharField(max_length=100, blank=True)),
                ('rights_holder_name', models.CharField(max_length=100)),
                ('can_sell', models.BooleanField(default=False)),
                ('owner', models.ForeignKey(on_delete=models.CASCADE, related_name='rights_holder', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(unique=True, max_length=200)),
                ('is_visible', models.BooleanField(default=True)),
                ('authority', models.CharField(default=b'', max_length=10)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('tagline', models.CharField(max_length=140, blank=True)),
                ('pic_url', models.URLField(blank=True)),
                ('home_url', models.URLField(blank=True)),
                ('twitter_id', models.CharField(max_length=15, blank=True)),
                ('facebook_id', models.BigIntegerField(null=True)),
                ('librarything_id', models.CharField(max_length=31, blank=True)),
                ('kindle_email', models.EmailField(max_length=254, blank=True)),
                ('goodreads_user_id', models.CharField(max_length=32, null=True, blank=True)),
                ('goodreads_user_name', models.CharField(max_length=200, null=True, blank=True)),
                ('goodreads_auth_token', models.TextField(null=True, blank=True)),
                ('goodreads_auth_secret', models.TextField(null=True, blank=True)),
                ('goodreads_user_link', models.CharField(max_length=200, null=True, blank=True)),
                ('avatar_source', models.PositiveSmallIntegerField(default=4, null=True, choices=[(0, b'No Avatar, Please'), (1, b'Gravatar'), (2, b'Twitter'), (3, b'Facebook'), (4, b'Unglueitar')])),
                ('badges', models.ManyToManyField(related_name='holders', to='core.Badge')),
                ('user', models.OneToOneField(on_delete=models.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WasWork',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('was', models.IntegerField(unique=True)),
                ('moved', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=models.CASCADE, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Wishes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('source', models.CharField(db_index=True, max_length=15, blank=True)),
            ],
            options={
                'db_table': 'core_wishlist_works',
            },
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=models.CASCADE, related_name='wishlist', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Work',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('title', models.CharField(max_length=1000)),
                ('language', models.CharField(default=b'en', max_length=5, db_index=True)),
                ('openlibrary_lookup', models.DateTimeField(null=True)),
                ('num_wishes', models.IntegerField(default=0, db_index=True)),
                ('description', models.TextField(default=b'', null=True, blank=True)),
                ('publication_range', models.CharField(max_length=50, null=True)),
                ('featured', models.DateTimeField(db_index=True, null=True, blank=True)),
                ('is_free', models.BooleanField(default=False)),
                ('selected_edition', models.ForeignKey(on_delete=models.CASCADE, related_name='selected_works', to='core.Edition', null=True)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.AddField(
            model_name='wishlist',
            name='works',
            field=models.ManyToManyField(related_name='wishlists', through='core.Wishes', to='core.Work'),
        ),
        migrations.AddField(
            model_name='wishes',
            name='wishlist',
            field=models.ForeignKey(on_delete=models.CASCADE, to='core.Wishlist'),
        ),
        migrations.AddField(
            model_name='wishes',
            name='work',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='wishes', to='core.Work'),
        ),
        migrations.AddField(
            model_name='waswork',
            name='work',
            field=models.ForeignKey(on_delete=models.CASCADE, to='core.Work'),
        ),
        migrations.AddField(
            model_name='subject',
            name='works',
            field=models.ManyToManyField(related_name='subjects', to='core.Work'),
        ),
        migrations.AddField(
            model_name='publisher',
            name='name',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='key_publisher', to='core.PublisherName'),
        ),
        migrations.AddField(
            model_name='offer',
            name='work',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='offers', to='core.Work'),
        ),
        migrations.AddField(
            model_name='identifier',
            name='work',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='identifiers', to='core.Work'),
        ),
    ]
