# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'BuildResult'
        db.create_table('builds_buildresult', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('build', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['builds.Build'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('body', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('builds', ['BuildResult'])


    def backwards(self, orm):
        
        # Deleting model 'BuildResult'
        db.delete_table('builds_buildresult')


    models = {
        'builds.build': {
            'Meta': {'object_name': 'Build'},
            'finished': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['workers.BuildNode']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projects.Project']"}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'started': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '20'})
        },
        'builds.buildresult': {
            'Meta': {'object_name': 'BuildResult'},
            'body': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'build': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['builds.Build']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'builds.buildstep': {
            'Meta': {'object_name': 'BuildStep'},
            'build': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['builds.Build']"}),
            'extra': ('journeyman.utils.jsonfield.JSONField', [], {}),
            'finished': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'started': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'successful': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'projects.project': {
            'Meta': {'object_name': 'Project'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'config_file': ('django.db.models.fields.CharField', [], {'default': "'journey.conf/config'", 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'repository': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ssh_key': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'workers.buildnode': {
            'Meta': {'object_name': 'BuildNode'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'host': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ssh_key': ('django.db.models.fields.TextField', [], {}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['builds']
