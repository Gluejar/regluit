# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Landing'
        db.create_table('survey_landing', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nonce', self.gf('django.db.models.fields.CharField')(max_length=32, null=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=64, null=True)),
        ))
        db.send_create_signal('survey', ['Landing'])


    def backwards(self, orm):
        # Deleting model 'Landing'
        db.delete_table('survey_landing')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'survey.landing': {
            'Meta': {'object_name': 'Landing'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'nonce': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'})
        }
    }

    complete_apps = ['survey']