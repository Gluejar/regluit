# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    no_dry_run = True
    def forwards(self, orm):
        import regluit.core.isbn
        for edition in orm.Edition.objects.all():
            if edition.isbn_10 and not edition.isbn_13:
                edition.isbn_13 = regluit.core.isbn.convert_10_to_13(edition.isbn_10)
                edition.save()


    def backwards(self, orm):
        pass


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
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.author': {
            'Meta': {'object_name': 'Author'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'editions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'authors'", 'symmetrical': 'False', 'to': "orm['core.Edition']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'core.campaign': {
            'Meta': {'object_name': 'Campaign'},
            'activated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'amazon_receiver': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'details': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'left': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'managers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'campaigns'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'paypal_receiver': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'INITIALIZED'", 'max_length': '15', 'null': 'True'}),
            'target': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
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
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 19, 17, 56, 32, 351053)', 'auto_now_add': 'True', 'blank': 'True'}),
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
            'edition': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ebooks'", 'to': "orm['core.Edition']"}),
            'format': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'provider': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'rights': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        'core.edition': {
            'Meta': {'object_name': 'Edition'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True'}),
            'goodreads_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'googlebooks_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isbn_10': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'isbn_13': ('django.db.models.fields.CharField', [], {'max_length': '13', 'null': 'True'}),
            'librarything_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'oclc': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True'}),
            'public_domain': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'publication_date': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'publisher': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'editions'", 'null': 'True', 'to': "orm['core.Work']"})
        },
        'core.premium': {
            'Meta': {'object_name': 'Premium'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '0'}),
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'premiums'", 'null': 'True', 'to': "orm['core.Campaign']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        'core.rightsholder': {
            'Meta': {'object_name': 'RightsHolder'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rights_holder'", 'to': "orm['auth.User']"}),
            'rights_holder_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
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
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'facebook_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'goodreads_auth_secret': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'goodreads_auth_token': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'goodreads_user_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'goodreads_user_link': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'goodreads_user_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'home_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'librarything_id': ('django.db.models.fields.CharField', [], {'max_length': '31', 'blank': 'True'}),
            'pic_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'tagline': ('django.db.models.fields.CharField', [], {'max_length': '140', 'blank': 'True'}),
            'twitter_id': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'profile'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'core.wishes': {
            'Meta': {'object_name': 'Wishes', 'db_table': "'core_wishlist_works'"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
            'wishlist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Wishlist']"}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Work']"})
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '2'}),
            'librarything_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'openlibrary_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'openlibrary_lookup': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        }
    }

    complete_apps = ['core']
