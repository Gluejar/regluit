# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    depends_on = (
        ("questionnaire", "0005_move_nonces"),
    )
    def forwards(self, orm):
        # Deleting model 'Landing'
        db.delete_table('survey_landing')


    def backwards(self, orm):
        # Adding model 'Landing'
        db.create_table('survey_landing', (
            ('nonce', self.gf('django.db.models.fields.CharField')(max_length=32, null=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=64, null=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('survey', ['Landing'])


    models = {
        
    }

    complete_apps = ['survey']