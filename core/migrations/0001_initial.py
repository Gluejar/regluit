# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Campaign'
        db.create_table('core_campaign', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500, null=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True)),
            ('target', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=2)),
            ('deadline', self.gf('django.db.models.fields.DateTimeField')()),
            ('activated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('suspended', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('withdrawn', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('suspended_reason', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('withdrawn_reason', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('paypal_receiver', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('amazon_receiver', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('work', self.gf('django.db.models.fields.related.ForeignKey')(related_name='campaigns', to=orm['core.Work'])),
        ))
        db.send_create_signal('core', ['Campaign'])

        # Adding model 'Work'
        db.create_table('core_work', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('openlibrary_id', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
        ))
        db.send_create_signal('core', ['Work'])

        # Adding model 'Author'
        db.create_table('core_author', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal('core', ['Author'])

        # Adding M2M table for field editions on 'Author'
        db.create_table('core_author_editions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('author', models.ForeignKey(orm['core.author'], null=False)),
            ('edition', models.ForeignKey(orm['core.edition'], null=False))
        ))
        db.create_unique('core_author_editions', ['author_id', 'edition_id'])

        # Adding model 'Subject'
        db.create_table('core_subject', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal('core', ['Subject'])

        # Adding M2M table for field editions on 'Subject'
        db.create_table('core_subject_editions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('subject', models.ForeignKey(orm['core.subject'], null=False)),
            ('edition', models.ForeignKey(orm['core.edition'], null=False))
        ))
        db.create_unique('core_subject_editions', ['subject_id', 'edition_id'])

        # Adding model 'Edition'
        db.create_table('core_edition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('googlebooks_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', null=True)),
            ('publisher', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('publication_date', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('isbn_10', self.gf('django.db.models.fields.CharField')(max_length=10, null=True)),
            ('isbn_13', self.gf('django.db.models.fields.CharField')(max_length=13, null=True)),
            ('work', self.gf('django.db.models.fields.related.ForeignKey')(related_name='editions', null=True, to=orm['core.Work'])),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=2, null=True)),
        ))
        db.send_create_signal('core', ['Edition'])

        # Adding model 'Wishlist'
        db.create_table('core_wishlist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='wishlist', unique=True, to=orm['auth.User'])),
        ))
        db.send_create_signal('core', ['Wishlist'])

        # Adding M2M table for field works on 'Wishlist'
        db.create_table('core_wishlist_works', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('wishlist', models.ForeignKey(orm['core.wishlist'], null=False)),
            ('work', models.ForeignKey(orm['core.work'], null=False))
        ))
        db.create_unique('core_wishlist_works', ['wishlist_id', 'work_id'])

        # Adding model 'UserProfile'
        db.create_table('core_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='profile', unique=True, to=orm['auth.User'])),
            ('tagline', self.gf('django.db.models.fields.CharField')(max_length=140, blank=True)),
        ))
        db.send_create_signal('core', ['UserProfile'])


    def backwards(self, orm):
        
        # Deleting model 'Campaign'
        db.delete_table('core_campaign')

        # Deleting model 'Work'
        db.delete_table('core_work')

        # Deleting model 'Author'
        db.delete_table('core_author')

        # Removing M2M table for field editions on 'Author'
        db.delete_table('core_author_editions')

        # Deleting model 'Subject'
        db.delete_table('core_subject')

        # Removing M2M table for field editions on 'Subject'
        db.delete_table('core_subject_editions')

        # Deleting model 'Edition'
        db.delete_table('core_edition')

        # Deleting model 'Wishlist'
        db.delete_table('core_wishlist')

        # Removing M2M table for field works on 'Wishlist'
        db.delete_table('core_wishlist_works')

        # Deleting model 'UserProfile'
        db.delete_table('core_userprofile')


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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'paypal_receiver': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'suspended': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'suspended_reason': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'target': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'withdrawn': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'withdrawn_reason': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'campaigns'", 'to': "orm['core.Work']"})
        },
        'core.edition': {
            'Meta': {'object_name': 'Edition'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True'}),
            'googlebooks_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isbn_10': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'isbn_13': ('django.db.models.fields.CharField', [], {'max_length': '13', 'null': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True'}),
            'publication_date': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'publisher': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'editions'", 'null': 'True', 'to': "orm['core.Work']"})
        },
        'core.subject': {
            'Meta': {'object_name': 'Subject'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'editions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'subjects'", 'symmetrical': 'False', 'to': "orm['core.Edition']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'core.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tagline': ('django.db.models.fields.CharField', [], {'max_length': '140', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'profile'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'core.wishlist': {
            'Meta': {'object_name': 'Wishlist'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'wishlist'", 'unique': 'True', 'to': "orm['auth.User']"}),
            'works': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'wishlists'", 'symmetrical': 'False', 'to': "orm['core.Work']"})
        },
        'core.work': {
            'Meta': {'object_name': 'Work'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'openlibrary_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        }
    }

    complete_apps = ['core']
