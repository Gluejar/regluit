# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):
    depends_on = (
        ("survey", "0001_initial"),
    )
    needed_by = (
        ("survey", "0002_auto__del_landing"),
    )

    def forwards(self, orm):
        oldLanding=orm['survey.Landing'] 
        Landing=orm['questionnaire.Landing'] 
        for landing in oldLanding.objects.all():
            Landing.objects.create(nonce=landing.nonce, label=landing.label, content_type=landing.content_type, object_id=landing.object_id)

    def backwards(self, orm):
        pass

    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
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
        'questionnaire.landing': {
            'Meta': {'object_name': 'Landing'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'landings'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'nonce': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
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
        },
        'survey.landing': {
            'Meta': {'object_name': 'Landing'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'nonce': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['survey', 'questionnaire']
    symmetrical = True
