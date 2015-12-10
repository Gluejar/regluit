# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BisacHeading'
        db.create_table('bisac_bisacheading', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('full_label', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('notation', self.gf('django.db.models.fields.CharField')(max_length=9)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='children', null=True, to=orm['bisac.BisacHeading'])),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('bisac', ['BisacHeading'])


    def backwards(self, orm):
        # Deleting model 'BisacHeading'
        db.delete_table('bisac_bisacheading')


    models = {
        'bisac.bisacheading': {
            'Meta': {'object_name': 'BisacHeading'},
            'full_label': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'notation': ('django.db.models.fields.CharField', [], {'max_length': '9'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['bisac.BisacHeading']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['bisac']