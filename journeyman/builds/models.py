from django.db import models
from journeyman.workers.models import BuildNode
from journeyman.projects.models import Project
from journeyman.utils import JSONField, Options

class BUILD_STATES(Options):
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

    state = models.CharField(max_length=20, default=BUILD_STATES.UNKNOWN,
        choices=BUILD_STATES.choices())

    def state_css_class(self):
        if self.state == BUILD_STATES.STABLE:
            return "success"
        elif self.state in [BUILD_STATE.QUEUED, BUILD_STATE.RUNNING]:
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
        return '%s/%s' % (self.build,
            'successful' if self.successful else 'failed')

    def return_code(self):
        return self.extra.get('return_code', None)

    def stdout(self):
        return self.extra.get('stdout', None)

    def exception_message(self):
        return self.extra.get('exception_message', None)
