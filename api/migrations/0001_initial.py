# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AllowedRepo'
        db.create_table('api_allowedrepo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('org', self.gf('django.db.models.fields.CharField')(max_length=39)),
            ('repo_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('api', ['AllowedRepo'])


    def backwards(self, orm):
        # Deleting model 'AllowedRepo'
        db.delete_table('api_allowedrepo')


    models = {
        'api.allowedrepo': {
            'Meta': {'object_name': 'AllowedRepo'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'org': ('django.db.models.fields.CharField', [], {'max_length': '39'}),
            'repo_name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['api']