# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Subject'
        db.create_table('questionnaire_subject', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('state', self.gf('django.db.models.fields.CharField')(default='inactive', max_length=16)),
            ('surname', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('givenname', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(default='unset', max_length=8, blank=True)),
            ('nextrun', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('formtype', self.gf('django.db.models.fields.CharField')(default='email', max_length=16)),
            ('language', self.gf('django.db.models.fields.CharField')(default='en-us', max_length=2)),
        ))
        db.send_create_signal('questionnaire', ['Subject'])

        # Adding model 'Questionnaire'
        db.create_table('questionnaire_questionnaire', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('redirect_url', self.gf('django.db.models.fields.CharField')(default='/static/complete.html', max_length=128)),
        ))
        db.send_create_signal('questionnaire', ['Questionnaire'])

        # Adding model 'QuestionSet'
        db.create_table('questionnaire_questionset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('questionnaire', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['questionnaire.Questionnaire'])),
            ('sortid', self.gf('django.db.models.fields.IntegerField')()),
            ('heading', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('checks', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('text_en', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('questionnaire', ['QuestionSet'])

        # Adding model 'RunInfo'
        db.create_table('questionnaire_runinfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['questionnaire.Subject'])),
            ('random', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('runid', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('questionset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['questionnaire.QuestionSet'], null=True, blank=True)),
            ('emailcount', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('emailsent', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('lastemailerror', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('cookies', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('tags', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('skipped', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('questionnaire', ['RunInfo'])

        # Adding model 'RunInfoHistory'
        db.create_table('questionnaire_runinfohistory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['questionnaire.Subject'])),
            ('runid', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('completed', self.gf('django.db.models.fields.DateField')()),
            ('tags', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('skipped', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('questionnaire', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['questionnaire.Questionnaire'])),
        ))
        db.send_create_signal('questionnaire', ['RunInfoHistory'])

        # Adding model 'Question'
        db.create_table('questionnaire_question', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('questionset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['questionnaire.QuestionSet'])),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('sort_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('text_en', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('extra_en', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('checks', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('footer_en', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('questionnaire', ['Question'])

        # Adding model 'Choice'
        db.create_table('questionnaire_choice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['questionnaire.Question'])),
            ('sortid', self.gf('django.db.models.fields.IntegerField')()),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('text_en', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('tags', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
        ))
        db.send_create_signal('questionnaire', ['Choice'])

        # Adding model 'Answer'
        db.create_table('questionnaire_answer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['questionnaire.Subject'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['questionnaire.Question'])),
            ('runid', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('answer', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('questionnaire', ['Answer'])


    def backwards(self, orm):
        # Deleting model 'Subject'
        db.delete_table('questionnaire_subject')

        # Deleting model 'Questionnaire'
        db.delete_table('questionnaire_questionnaire')

        # Deleting model 'QuestionSet'
        db.delete_table('questionnaire_questionset')

        # Deleting model 'RunInfo'
        db.delete_table('questionnaire_runinfo')

        # Deleting model 'RunInfoHistory'
        db.delete_table('questionnaire_runinfohistory')

        # Deleting model 'Question'
        db.delete_table('questionnaire_question')

        # Deleting model 'Choice'
        db.delete_table('questionnaire_choice')

        # Deleting model 'Answer'
        db.delete_table('questionnaire_answer')


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
        'questionnaire.question': {
            'Meta': {'object_name': 'Question'},
            'checks': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'extra_en': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'footer_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'questionset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['questionnaire.QuestionSet']"}),
            'sort_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'text_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'questionnaire.questionnaire': {
            'Meta': {'object_name': 'Questionnaire'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'redirect_url': ('django.db.models.fields.CharField', [], {'default': "'/static/complete.html'", 'max_length': '128'})
        },
        'questionnaire.questionset': {
            'Meta': {'object_name': 'QuestionSet'},
            'checks': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'heading': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'completed': ('django.db.models.fields.DateField', [], {}),
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
            'language': ('django.db.models.fields.CharField', [], {'default': "'en-us'", 'max_length': '2'}),
            'nextrun': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'inactive'", 'max_length': '16'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['questionnaire']