# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Boox'
        db.create_table('booxtream_boox', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('download_link_epub', self.gf('django.db.models.fields.URLField')(max_length=200, null=True)),
            ('download_link_mobi', self.gf('django.db.models.fields.URLField')(max_length=200, null=True)),
            ('referenceid', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('downloads_remaining', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('expirydays', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('booxtream', ['Boox'])


    def backwards(self, orm):
        # Deleting model 'Boox'
        db.delete_table('booxtream_boox')


    models = {
        'booxtream.boox': {
            'Meta': {'object_name': 'Boox'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'download_link_epub': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'download_link_mobi': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'downloads_remaining': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'expirydays': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'referenceid': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['booxtream']