# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'XFormSurvey'
        db.delete_table('smstouchforms_xformsurvey')

        # Deleting field 'XFormsSession.form'
        db.delete_column('smstouchforms_xformssession', 'form_id')


    def backwards(self, orm):
        
        # Adding model 'XFormSurvey'
        db.create_table('smstouchforms_xformsurvey', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('stats_complete', self.gf('django.db.models.fields.IntegerField')(max_length=6)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('stats_started', self.gf('django.db.models.fields.IntegerField')(max_length=6)),
        ))
        db.send_create_signal('smstouchforms', ['XFormSurvey'])

        # Adding field 'XFormsSession.form'
        db.add_column('smstouchforms_xformssession', 'form', self.gf('django.db.models.fields.related.ForeignKey')(default='2', to=orm['smstouchforms.XFormSurvey']), keep_default=False)


    models = {
        'rapidsms.backend': {
            'Meta': {'object_name': 'Backend'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
        },
        'rapidsms.connection': {
            'Meta': {'unique_together': "(('backend', 'identity'),)", 'object_name': 'Connection'},
            'backend': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rapidsms.Backend']"}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rapidsms.Contact']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identity': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'rapidsms.contact': {
            'Meta': {'object_name': 'Contact'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '6', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'pin': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'primary_backend': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'contact_primary'", 'null': 'True', 'to': "orm['rapidsms.Backend']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'})
        },
        'smstouchforms.xformssession': {
            'Meta': {'object_name': 'XFormsSession'},
            'connection': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'xform_sessions'", 'to': "orm['rapidsms.Connection']"}),
            'current_response': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'ended': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'error_msg': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'possible_answers': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'session_id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'started': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'touch_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['smstouchforms']
