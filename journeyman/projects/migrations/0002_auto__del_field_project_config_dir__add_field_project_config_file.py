# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Project.config_dir'
        db.delete_column('projects_project', 'config_dir')

        # Adding field 'Project.config_file'
        db.add_column('projects_project', 'config_file', self.gf('django.db.models.fields.CharField')(default='journey.conf/config', max_length=255), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'Project.config_dir'
        db.add_column('projects_project', 'config_dir', self.gf('django.db.models.fields.CharField')(default='journey.conf', max_length=255), keep_default=False)

        # Deleting field 'Project.config_file'
        db.delete_column('projects_project', 'config_file')


    models = {
        'projects.project': {
            'Meta': {'object_name': 'Project'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'config_file': ('django.db.models.fields.CharField', [], {'default': "'journey.conf/config'", 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'repository': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ssh_key': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['projects']
