# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Build.started'
        db.alter_column('builds_build', 'started', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'Build.finished'
        db.alter_column('builds_build', 'finished', self.gf('django.db.models.fields.DateTimeField')(null=True))


    def backwards(self, orm):
        
        # Changing field 'Build.started'
        db.alter_column('builds_build', 'started', self.gf('django.db.models.fields.DateTimeField')())

        # Changing field 'Build.finished'
        db.alter_column('builds_build', 'finished', self.gf('django.db.models.fields.DateTimeField')())


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
        'builds.buildstep': {
            'Meta': {'object_name': 'BuildStep'},
            'build': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['builds.Build']"}),
            'extra': ('journeyman.utils.jsonfield.JSONField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'successful': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'projects.project': {
            'Meta': {'object_name': 'Project'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'config_dir': ('django.db.models.fields.CharField', [], {'default': "'journey.conf'", 'max_length': '255'}),
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
