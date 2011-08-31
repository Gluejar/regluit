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
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=10000)),
            ('target', self.gf('django.db.models.fields.FloatField')()),
            ('deadline', self.gf('django.db.models.fields.DateTimeField')()),
            ('paypal_receiver', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('amazon_receiver', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('work', self.gf('django.db.models.fields.related.ForeignKey')(related_name='campaign', to=orm['core.Work'])),
        ))
        db.send_create_signal('core', ['Campaign'])

        # Adding model 'Work'
        db.create_table('core_work', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('core', ['Work'])

        # Adding model 'Edition'
        db.create_table('core_edition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('publisher', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('year', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('work', self.gf('django.db.models.fields.related.ForeignKey')(related_name='editions', to=orm['core.Work'])),
        ))
        db.send_create_signal('core', ['Edition'])

        # Adding model 'Identifier'
        db.create_table('core_identifier', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('edition', self.gf('django.db.models.fields.related.ForeignKey')(related_name='identifiers', to=orm['core.Edition'])),
        ))
        db.send_create_signal('core', ['Identifier'])

        # Adding model 'Author'
        db.create_table('core_author', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('edition', self.gf('django.db.models.fields.related.ForeignKey')(related_name='authors', to=orm['core.Edition'])),
        ))
        db.send_create_signal('core', ['Author'])


    def backwards(self, orm):
        
        # Deleting model 'Campaign'
        db.delete_table('core_campaign')

        # Deleting model 'Work'
        db.delete_table('core_work')

        # Deleting model 'Edition'
        db.delete_table('core_edition')

        # Deleting model 'Identifier'
        db.delete_table('core_identifier')

        # Deleting model 'Author'
        db.delete_table('core_author')


    models = {
        'core.author': {
            'Meta': {'object_name': 'Author'},
            'edition': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'authors'", 'to': "orm['core.Edition']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'core.campaign': {
            'Meta': {'object_name': 'Campaign'},
            'amazon_receiver': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '10000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'paypal_receiver': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'target': ('django.db.models.fields.FloatField', [], {}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'campaign'", 'to': "orm['core.Work']"})
        },
        'core.edition': {
            'Meta': {'object_name': 'Edition'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'publisher': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'editions'", 'to': "orm['core.Work']"}),
            'year': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'core.identifier': {
            'Meta': {'object_name': 'Identifier'},
            'edition': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'identifiers'", 'to': "orm['core.Edition']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'core.work': {
            'Meta': {'object_name': 'Work'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        }
    }

    complete_apps = ['core']
