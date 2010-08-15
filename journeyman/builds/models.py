from django.db import models
from journeyman.workers.models import BuildNode
from journeyman.projects.models import Project
from journeyman.utils import JSONField, Options

class BuildState(Options):
    QUEUED = 'queued'
    RUNNING = 'running'
    FAILED = 'failed'
    UNSTABLE = 'unstable'
    STABLE = 'stable'
    UNKNOWN = 'unknown'

class Build(models.Model):
    project = models.ForeignKey(Project)
    node = models.ForeignKey(BuildNode)
    revision = models.CharField(max_length=255, blank=True)

    started = models.DateTimeField(null=True, blank=True)
    finished = models.DateTimeField(null=True, blank=True)

    state = models.CharField(max_length=20, default=BuildState.UNKNOWN,
        choices=BuildState.choices())

    def state_css_class(self):
        if self.state == BuildState.STABLE:
            return "success"
        elif self.state in [BuildState.QUEUED, BuildState.RUNNING]:
            return "notice"
        else: 
            return "error"

    def __unicode__(self):
        return u'%s/%s/%s (%s)' % (self.project, self.node, self.state,
            self.started)

    @property
    def build_steps(self):
        return self.buildstep_set.all().order_by('started')

class BuildStep(models.Model):
    build = models.ForeignKey(Build)

    started = models.DateTimeField(null=True, blank=True)
    finished = models.DateTimeField(null=True, blank=True)

    name = models.CharField(max_length=255)
    successful = models.BooleanField()
    extra = JSONField()

    def __unicode__(self):
        return '%s/%s' % (self.build, self.state)
    
    
    def state_css_class(self):
        if self.successful:
            return "success"
        else:
            return "error"

    @property
    def state(self):
        return 'successful' if self.successful else 'failed'

    def return_code(self):
        return dict(self.extra).get('return_code', None)

    def stdout(self):
        return dict(self.extra).get('stdout', None)

    def stderr(self):
        return dict(self.extra).get('stderr', None)

    def exception_message(self):
        return dict(self.extra).get('exception_message', None)

class BuildResult(models.Model):
    build = models.ForeignKey(Build)
    name = models.CharField(max_length=255)
    body = models.TextField(blank=True)

    def __unicode__(self):
        return '%s - %s' % (self.build, self.name)
