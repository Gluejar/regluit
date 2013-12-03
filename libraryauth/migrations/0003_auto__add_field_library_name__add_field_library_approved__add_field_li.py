# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Library.name'
        db.add_column('libraryauth_library', 'name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=80),
                      keep_default=False)

        # Adding field 'Library.approved'
        db.add_column('libraryauth_library', 'approved',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Library.owner'
        db.add_column('libraryauth_library', 'owner',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=10, related_name='libraries', to=orm['auth.User']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Library.name'
        db.delete_column('libraryauth_library', 'name')

        # Deleting field 'Library.approved'
        db.delete_column('libraryauth_library', 'approved')

        # Deleting field 'Library.owner'
        db.delete_column('libraryauth_library', 'owner_id')


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
        'libraryauth.block': {
            'Meta': {'ordering': "['lower']", 'object_name': 'Block'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'library': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ip_auths'", 'to': "orm['libraryauth.Library']"}),
            'lower': ('regluit.libraryauth.models.IPAddressModelField', [], {'unique': 'True', 'db_index': 'True'}),
            'upper': ('regluit.libraryauth.models.IPAddressModelField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        'libraryauth.cardpattern': {
            'Meta': {'object_name': 'CardPattern'},
            'checksum': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'library': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cardnum_auths'", 'to': "orm['libraryauth.Library']"}),
            'pattern': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'libraryauth.emailpattern': {
            'Meta': {'object_name': 'EmailPattern'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'library': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'email_auths'", 'to': "orm['libraryauth.Library']"}),
            'pattern': ('django.db.models.fields.CharField', [], {'max_length': '20'})
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
        },
        'libraryauth.libraryuser': {
            'Meta': {'object_name': 'LibraryUser'},
            'credential': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'library': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'library_users'", 'to': "orm['libraryauth.Library']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_libraries'", 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['libraryauth']