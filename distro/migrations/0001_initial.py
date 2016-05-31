# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Target'
        db.create_table(u'distro_target', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('host', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('pw', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('protocol', self.gf('django.db.models.fields.CharField')(default='ftp', max_length=10)),
        ))
        db.send_create_signal(u'distro', ['Target'])

        # Adding M2M table for field formats on 'Target'
        m2m_table_name = db.shorten_name(u'distro_target_formats')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('target', models.ForeignKey(orm[u'distro.target'], null=False)),
            ('format', models.ForeignKey(orm[u'distro.format'], null=False))
        ))
        db.create_unique(m2m_table_name, ['target_id', 'format_id'])

        # Adding model 'Deposit'
        db.create_table(u'distro_deposit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('target', self.gf('django.db.models.fields.related.ForeignKey')(related_name='deposits', to=orm['distro.Target'])),
            ('isbn', self.gf('django.db.models.fields.CharField')(max_length=13)),
            ('format', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'distro', ['Deposit'])

        # Adding model 'Format'
        db.create_table(u'distro_format', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=4)),
        ))
        db.send_create_signal(u'distro', ['Format'])


    def backwards(self, orm):
        # Deleting model 'Target'
        db.delete_table(u'distro_target')

        # Removing M2M table for field formats on 'Target'
        db.delete_table(db.shorten_name(u'distro_target_formats'))

        # Deleting model 'Deposit'
        db.delete_table(u'distro_deposit')

        # Deleting model 'Format'
        db.delete_table(u'distro_format')


    models = {
        u'distro.deposit': {
            'Meta': {'object_name': 'Deposit'},
            'format': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isbn': ('django.db.models.fields.CharField', [], {'max_length': '13'}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'deposits'", 'to': u"orm['distro.Target']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'distro.format': {
            'Meta': {'object_name': 'Format'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '4'})
        },
        u'distro.target': {
            'Meta': {'object_name': 'Target'},
            'formats': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'targets'", 'symmetrical': 'False', 'to': u"orm['distro.Format']"}),
            'host': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'protocol': ('django.db.models.fields.CharField', [], {'default': "'ftp'", 'max_length': '10'}),
            'pw': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['distro']