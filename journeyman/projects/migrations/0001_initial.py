# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Project'
        db.create_table('projects_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('repository', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ssh_key', self.gf('django.db.models.fields.TextField')()),
            ('config_dir', self.gf('django.db.models.fields.CharField')(default='journey.conf', max_length=255)),
        ))
        db.send_create_signal('projects', ['Project'])


    def backwards(self, orm):
        
        # Deleting model 'Project'
        db.delete_table('projects_project')


    models = {
        'projects.project': {
            'Meta': {'object_name': 'Project'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'config_dir': ('django.db.models.fields.CharField', [], {'default': "'journey.conf'", 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'repository': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ssh_key': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['projects']
