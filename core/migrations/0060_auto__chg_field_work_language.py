# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Work.language'
        db.alter_column('core_work', 'language', self.gf('django.db.models.fields.CharField')(max_length=5))

    def backwards(self, orm):

        # Changing field 'Work.language'
        db.alter_column('core_work', 'language', self.gf('django.db.models.fields.CharField')(max_length=2))

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'booxtream.boox': {
            'Meta': {'object_name': 'Boox'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'download_link_epub': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'download_link_mobi': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'downloads_remaining': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'expirydays': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'referenceid': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.acq': {
            'Meta': {'object_name': 'Acq'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'expires': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lib_acq': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'loans'", 'null': 'True', 'to': "orm['core.Acq']"}),
            'license': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'nonce': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'refreshed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'refreshes': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 6, 6, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'acqs'", 'to': "orm['auth.User']"}),
            'watermarked': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['booxtream.Boox']", 'null': 'True'}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'acqs'", 'to': "orm['core.Work']"})
        },
        'core.author': {
            'Meta': {'object_name': 'Author'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'editions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'authors'", 'symmetrical': 'False', 'to': "orm['core.Edition']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'core.badge': {
            'Meta': {'object_name': 'Badge'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '72', 'blank': 'True'})
        },
        'core.campaign': {
            'Meta': {'object_name': 'Campaign'},
            'activated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'amazon_receiver': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'cc_date_initial': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'description': ('ckeditor.fields.RichTextField', [], {'null': 'True'}),
            'details': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'do_watermark': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'dollar_per_day': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'edition': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'campaigns'", 'null': 'True', 'to': "orm['core.Edition']"}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'left': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'license': ('django.db.models.fields.CharField', [], {'default': "'CC BY-NC-ND'", 'max_length': '255'}),
            'managers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'campaigns'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'paypal_receiver': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'publisher': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'campaigns'", 'null': 'True', 'to': "orm['core.Publisher']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'INITIALIZED'", 'max_length': '15', 'null': 'True'}),
            'target': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'campaigns'", 'to': "orm['core.Work']"})
        },
        'core.campaignaction': {
            'Meta': {'object_name': 'CampaignAction'},
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actions'", 'to': "orm['core.Campaign']"}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        },
        'core.celerytask': {
            'Meta': {'object_name': 'CeleryTask'},
            'active': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 6, 6, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True'}),
            'function_args': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'function_name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'task_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tasks'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'core.claim': {
            'Meta': {'object_name': 'Claim'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rights_holder': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'claim'", 'to': "orm['core.RightsHolder']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'pending'", 'max_length': '7'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'claim'", 'to': "orm['auth.User']"}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'claim'", 'to': "orm['core.Work']"})
        },
        'core.ebook': {
            'Meta': {'object_name': 'Ebook'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'download_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'edition': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ebooks'", 'to': "orm['core.Edition']"}),
            'format': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'provider': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'rights': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'db_index': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '1024'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        },
        'core.ebookfile': {
            'Meta': {'object_name': 'EbookFile'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'edition': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ebook_files'", 'to': "orm['core.Edition']"}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'format': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'core.edition': {
            'Meta': {'object_name': 'Edition'},
            'cover_image': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'publication_date': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'publisher_name': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'editions'", 'null': 'True', 'to': "orm['core.PublisherName']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'unglued': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'editions'", 'null': 'True', 'to': "orm['core.Work']"})
        },
        'core.hold': {
            'Meta': {'object_name': 'Hold'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'library': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'holds'", 'to': "orm['libraryauth.Library']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'holds'", 'to': "orm['auth.User']"}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'holds'", 'to': "orm['core.Work']"})
        },
        'core.identifier': {
            'Meta': {'unique_together': "(('type', 'value'),)", 'object_name': 'Identifier'},
            'edition': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'identifiers'", 'null': 'True', 'to': "orm['core.Edition']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '31'}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'identifiers'", 'to': "orm['core.Work']"})
        },
        'core.key': {
            'Meta': {'object_name': 'Key'},
            'encrypted_value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'core.libpref': {
            'Meta': {'object_name': 'Libpref'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marc_link_target': ('django.db.models.fields.CharField', [], {'default': "'UNGLUE'", 'max_length': '6'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'libpref'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'core.marcrecord': {
            'Meta': {'object_name': 'MARCRecord'},
            'edition': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'MARCrecords'", 'null': 'True', 'to': "orm['core.Edition']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link_target': ('django.db.models.fields.CharField', [], {'default': "'DIRECT'", 'max_length': '6'})
        },
        'core.offer': {
            'Meta': {'object_name': 'Offer'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'license': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2'}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'offers'", 'to': "orm['core.Work']"})
        },
        'core.premium': {
            'Meta': {'object_name': 'Premium'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '0'}),
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'premiums'", 'null': 'True', 'to': "orm['core.Campaign']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'limit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        'core.press': {
            'Meta': {'object_name': 'Press'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'highlight': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '140', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '140'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '140'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'core.publisher': {
            'Meta': {'object_name': 'Publisher'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo_url': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'key_publisher'", 'to': "orm['core.PublisherName']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'})
        },
        'core.publishername': {
            'Meta': {'object_name': 'PublisherName'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'publisher': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'alternate_names'", 'null': 'True', 'to': "orm['core.Publisher']"})
        },
        'core.rightsholder': {
            'Meta': {'object_name': 'RightsHolder'},
            'can_sell': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rights_holder'", 'to': "orm['auth.User']"}),
            'rights_holder_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.subject': {
            'Meta': {'ordering': "['name']", 'object_name': 'Subject'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'works': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'subjects'", 'symmetrical': 'False', 'to': "orm['core.Work']"})
        },
        'core.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'avatar_source': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1', 'null': 'True'}),
            'badges': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'holders'", 'symmetrical': 'False', 'to': "orm['core.Badge']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'facebook_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'goodreads_auth_secret': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'goodreads_auth_token': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'goodreads_user_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'goodreads_user_link': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'goodreads_user_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'home_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kindle_email': ('django.db.models.fields.EmailField', [], {'max_length': '254', 'blank': 'True'}),
            'librarything_id': ('django.db.models.fields.CharField', [], {'max_length': '31', 'blank': 'True'}),
            'pic_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'tagline': ('django.db.models.fields.CharField', [], {'max_length': '140', 'blank': 'True'}),
            'twitter_id': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'profile'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'core.waswork': {
            'Meta': {'object_name': 'WasWork'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moved': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'was': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Work']"})
        },
        'core.wishes': {
            'Meta': {'object_name': 'Wishes', 'db_table': "'core_wishlist_works'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
            'wishlist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Wishlist']"}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'wishes'", 'to': "orm['core.Work']"})
        },
        'core.wishlist': {
            'Meta': {'object_name': 'Wishlist'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'wishlist'", 'unique': 'True', 'to': "orm['auth.User']"}),
            'works': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'wishlists'", 'symmetrical': 'False', 'through': "orm['core.Wishes']", 'to': "orm['core.Work']"})
        },
        'core.work': {
            'Meta': {'ordering': "['title']", 'object_name': 'Work'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'earliest_publication': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '5'}),
            'num_wishes': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'openlibrary_lookup': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'selected_edition': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'selected_works'", 'null': 'True', 'to': "orm['core.Edition']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        },
        'libraryauth.library': {
            'Meta': {'object_name': 'Library'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'backend': ('django.db.models.fields.CharField', [], {'default': "'ip'", 'max_length': '10'}),
            'group': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'library'", 'unique': 'True', 'null': 'True', 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '80'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'libraries'", 'to': "orm['auth.User']"}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'library'", 'unique': 'True', 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['core']