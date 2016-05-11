# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'Choice', fields ['value']
        db.create_index(u'questionnaire_choice', ['value'])

        # Adding index on 'Question', fields ['number', 'questionset']
        db.create_index(u'questionnaire_question', ['number', 'questionset_id'])

        # Adding index on 'Subject', fields ['givenname', 'surname']
        db.create_index(u'questionnaire_subject', ['givenname', 'surname'])

        # Adding index on 'RunInfo', fields ['random']
        db.create_index(u'questionnaire_runinfo', ['random'])

        # Adding index on 'Answer', fields ['subject', 'runid', u'id']
        db.create_index(u'questionnaire_answer', ['subject_id', 'runid', u'id'])

        # Adding index on 'Answer', fields ['subject', 'runid']
        db.create_index(u'questionnaire_answer', ['subject_id', 'runid'])

        # Adding index on 'QuestionSet', fields ['questionnaire', 'sortid']
        db.create_index(u'questionnaire_questionset', ['questionnaire_id', 'sortid'])

        # Adding index on 'QuestionSet', fields ['sortid']
        db.create_index(u'questionnaire_questionset', ['sortid'])


    def backwards(self, orm):
        # Removing index on 'QuestionSet', fields ['sortid']
        db.delete_index(u'questionnaire_questionset', ['sortid'])

        # Removing index on 'QuestionSet', fields ['questionnaire', 'sortid']
        db.delete_index(u'questionnaire_questionset', ['questionnaire_id', 'sortid'])

        # Removing index on 'Answer', fields ['subject', 'runid']
        db.delete_index(u'questionnaire_answer', ['subject_id', 'runid'])

        # Removing index on 'Answer', fields ['subject', 'runid', u'id']
        db.delete_index(u'questionnaire_answer', ['subject_id', 'runid', u'id'])

        # Removing index on 'RunInfo', fields ['random']
        db.delete_index(u'questionnaire_runinfo', ['random'])

        # Removing index on 'Subject', fields ['givenname', 'surname']
        db.delete_index(u'questionnaire_subject', ['givenname', 'surname'])

        # Removing index on 'Question', fields ['number', 'questionset']
        db.delete_index(u'questionnaire_question', ['number', 'questionset_id'])

        # Removing index on 'Choice', fields ['value']
        db.delete_index(u'questionnaire_choice', ['value'])


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'questionnaire.answer': {
            'Meta': {'object_name': 'Answer', 'index_together': "[['subject', 'runid'], ['subject', 'runid', 'id']]"},
            'answer': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['questionnaire.Question']"}),
            'runid': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['questionnaire.Subject']"})
        },
        u'questionnaire.choice': {
            'Meta': {'object_name': 'Choice', 'index_together': "[['value']]"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['questionnaire.Question']"}),
            'sortid': ('django.db.models.fields.IntegerField', [], {}),
            'tags': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'text_en': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'questionnaire.dbstylesheet': {
            'Meta': {'object_name': 'DBStylesheet'},
            'content': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inclusion_tag': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'questionnaire.globalstyles': {
            'Meta': {'object_name': 'GlobalStyles'},
            'content': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'questionnaire.landing': {
            'Meta': {'object_name': 'Landing'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'landings'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'nonce': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'questionnaire': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'landings'", 'null': 'True', 'to': u"orm['questionnaire.Questionnaire']"})
        },
        u'questionnaire.question': {
            'Meta': {'object_name': 'Question', 'index_together': "[['number', 'questionset']]"},
            'checks': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'extra_en': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'footer_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'parse_html': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'questionset': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['questionnaire.QuestionSet']"}),
            'sort_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'text_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'questionnaire.questionnaire': {
            'Meta': {'object_name': 'Questionnaire'},
            'admin_access_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'html': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'parse_html': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'redirect_url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'})
        },
        u'questionnaire.questionset': {
            'Meta': {'object_name': 'QuestionSet', 'index_together': "[['questionnaire', 'sortid'], ['sortid']]"},
            'checks': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'heading': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parse_html': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'questionnaire': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['questionnaire.Questionnaire']"}),
            'sortid': ('django.db.models.fields.IntegerField', [], {}),
            'text_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'questionnaire.runinfo': {
            'Meta': {'object_name': 'RunInfo', 'index_together': "[['random']]"},
            'cookies': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'emailcount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'emailsent': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'landing': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['questionnaire.Landing']", 'null': 'True', 'blank': 'True'}),
            'lastemailerror': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'questionset': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['questionnaire.QuestionSet']", 'null': 'True', 'blank': 'True'}),
            'random': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'runid': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'skipped': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['questionnaire.Subject']"}),
            'tags': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'questionnaire.runinfohistory': {
            'Meta': {'object_name': 'RunInfoHistory'},
            'completed': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'landing': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['questionnaire.Landing']", 'null': 'True', 'blank': 'True'}),
            'questionnaire': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['questionnaire.Questionnaire']"}),
            'runid': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'skipped': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['questionnaire.Subject']"}),
            'tags': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'questionnaire.subject': {
            'Meta': {'object_name': 'Subject', 'index_together': "[['givenname', 'surname']]"},
            'anonymous': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'formtype': ('django.db.models.fields.CharField', [], {'default': "'email'", 'max_length': '16'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "'unset'", 'max_length': '8', 'blank': 'True'}),
            'givenname': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39', 'null': 'True', 'blank': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en-us'", 'max_length': '5'}),
            'nextrun': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'inactive'", 'max_length': '16'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['questionnaire']