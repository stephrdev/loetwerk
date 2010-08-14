from django.db import models
from journeyman.workers.models import BuildNode
from journeyman.projects.models import Project
from journeyman.utils import JSONField, Options

class BUILD_STATES(Options):
    FAILED = "failed"
    UNSTABLE = "unstable"
    STABLE = "stable"
    UNKNOWN = "unknown"

class Build(models.Model):
    project = models.ForeignKey(Project)
    node = models.ForeignKey(BuildNode)
    revision = models.CharField(max_length=255, blank=True)
    
    started = models.DateTimeField(null=True, blank=True)
    finished = models.DateTimeField(null=True, blank=True)
    
    state = models.CharField(max_length=20, default=BUILD_STATES.UNKNOWN, choices=BUILD_STATES.choices())
    
class BuildStep(models.Model):
    build = models.ForeignKey(Build)
    
    name = models.CharField(max_length=255)
    successful = models.BooleanField()
    extra = JSONField()
    
    