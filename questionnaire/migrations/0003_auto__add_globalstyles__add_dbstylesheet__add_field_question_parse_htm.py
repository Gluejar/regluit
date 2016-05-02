# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GlobalStyles'
        db.create_table('questionnaire_globalstyles', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('questionnaire', ['GlobalStyles'])

        # Adding model 'DBStylesheet'
        db.create_table('questionnaire_dbstylesheet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('inclusion_tag', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('content', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('questionnaire', ['DBStylesheet'])

        # Adding field 'Question.parse_html'
        db.add_column('questionnaire_question', 'parse_html',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Questionnaire.html'
        db.add_column('questionnaire_questionnaire', 'html',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Questionnaire.parse_html'
        db.add_column('questionnaire_questionnaire', 'parse_html',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Questionnaire.admin_access_only'
        db.add_column('questionnaire_questionnaire', 'admin_access_only',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # Changing field 'RunInfoHistory.completed'
        db.alter_column('questionnaire_runinfohistory', 'completed', self.gf('django.db.models.fields.DateTimeField')())
        # Adding field 'QuestionSet.parse_html'
        db.add_column('questionnaire_questionset', 'parse_html',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'GlobalStyles'
        db.delete_table('questionnaire_globalstyles')

        # Deleting model 'DBStylesheet'
        db.delete_table('questionnaire_dbstylesheet')

        # Deleting field 'Question.parse_html'
        db.delete_column('questionnaire_question', 'parse_html')

        # Deleting field 'Questionnaire.html'
        db.delete_column('questionnaire_questionnaire', 'html')

        # Deleting field 'Questionnaire.parse_html'
        db.delete_column('questionnaire_questionnaire', 'parse_html')

        # Deleting field 'Questionnaire.admin_access_only'
        db.delete_column('questionnaire_questionnaire', 'admin_access_only')


        # Changing field 'RunInfoHistory.completed'
        db.alter_column('questionnaire_runinfohistory', 'completed', self.gf('django.db.models.fields.DateField')())
        # Deleting field 'QuestionSet.parse_html'
        db.delete_column('questionnaire_questionset', 'parse_html')


    models = {
        'questionnaire.answer': {
            'Meta': {'object_name': 'Answer'},
            'answer': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['questionnaire.Question']"}),
            'runid': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['questionnaire.Subject']"})
        },
        'questionnaire.choice': {
            'Meta': {'object_name': 'Choice'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['questionnaire.Question']"}),
            'sortid': ('django.db.models.fields.IntegerField', [], {}),
            'tags': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'text_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'questionnaire.dbstylesheet': {
            'Meta': {'object_name': 'DBStylesheet'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inclusion_tag': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'questionnaire.globalstyles': {
            'Meta': {'object_name': 'GlobalStyles'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'questionnaire.question': {
            'Meta': {'object_name': 'Question'},
            'checks': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'extra_en': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'footer_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'parse_html': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'questionset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['questionnaire.QuestionSet']"}),
            'sort_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'text_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'questionnaire.questionnaire': {
            'Meta': {'object_name': 'Questionnaire'},
            'admin_access_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'parse_html': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'redirect_url': ('django.db.models.fields.CharField', [], {'default': "'/static/complete.html'", 'max_length': '128'})
        },
        'questionnaire.questionset': {
            'Meta': {'object_name': 'QuestionSet'},
            'checks': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'heading': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parse_html': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'questionnaire': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['questionnaire.Questionnaire']"}),
            'sortid': ('django.db.models.fields.IntegerField', [], {}),
            'text_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'questionnaire.runinfo': {
            'Meta': {'object_name': 'RunInfo'},
            'cookies': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'emailcount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'emailsent': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastemailerror': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'questionset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['questionnaire.QuestionSet']", 'null': 'True', 'blank': 'True'}),
            'random': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'runid': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'skipped': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['questionnaire.Subject']"}),
            'tags': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'questionnaire.runinfohistory': {
            'Meta': {'object_name': 'RunInfoHistory'},
            'completed': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'questionnaire': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['questionnaire.Questionnaire']"}),
            'runid': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'skipped': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['questionnaire.Subject']"}),
            'tags': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'questionnaire.subject': {
            'Meta': {'object_name': 'Subject'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'formtype': ('django.db.models.fields.CharField', [], {'default': "'email'", 'max_length': '16'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "'unset'", 'max_length': '8', 'blank': 'True'}),
            'givenname': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en-us'", 'max_length': '5'}),
            'nextrun': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'inactive'", 'max_length': '16'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['questionnaire']