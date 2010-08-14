# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Build'
        db.create_table('builds_build', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'])),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['workers.BuildNode'])),
            ('revision', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('started', self.gf('django.db.models.fields.DateTimeField')()),
            ('finished', self.gf('django.db.models.fields.DateTimeField')()),
            ('state', self.gf('django.db.models.fields.CharField')(default='unknown', max_length=20)),
        ))
        db.send_create_signal('builds', ['Build'])

        # Adding model 'BuildStep'
        db.create_table('builds_buildstep', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('build', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['builds.Build'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('successful', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('extra', self.gf('journeyman.utils.jsonfield.JSONField')()),
        ))
        db.send_create_signal('builds', ['BuildStep'])


    def backwards(self, orm):
        
        # Deleting model 'Build'
        db.delete_table('builds_build')

        # Deleting model 'BuildStep'
        db.delete_table('builds_buildstep')


    models = {
        'builds.build': {
            'Meta': {'object_name': 'Build'},
            'finished': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['workers.BuildNode']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['projects.Project']"}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'started': ('django.db.models.fields.DateTimeField', [], {}),
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
            'ssh_key': ('django.db.models.fields.TextField', [], {})
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
