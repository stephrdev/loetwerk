from django.db import models
from journeyman.workers.models import BuildNode
from journeyman.projects.models import Project
from journeyman.utils import JSONField, Options
from journeyman.builds.tasks import BuildTask

from lxml import etree
from collections import defaultdict
from StringIO import StringIO

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
        # Determine the correct css class
        if self.state == BuildState.STABLE:
            return 'success'
        elif self.state in [BuildState.QUEUED, BuildState.RUNNING]:
            return 'notice'
        else: 
            return 'error'

    def __unicode__(self):
        return u'%s/%s/%s (%s)' % (self.project, self.node, self.state,
            self.started)

    def queue_build(self):
        # Create a celery task and set the state to QUEUED
        BuildTask.delay(self.pk)
        self.state = BuildState.QUEUED
        self.save()

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
        # Return a css class according to state of the step
        if self.successful:
            return 'success'
        else:
            return 'error'

    @property
    def state(self):
        # Return a name according to the state
        return 'successful' if self.successful else 'failed'

    def return_code(self):
        # Return the return_code or None
        return dict(self.extra).get('return_code', None)

    def stdout(self):
        # Return the stdout buffer or None
        return dict(self.extra).get('stdout', None)

    def stderr(self):
        # Return the stderr buffer or None
        return dict(self.extra).get('stderr', None)

    def exception_message(self):
        # Return the exception message of the step or None
        return dict(self.extra).get('exception_message', None)

class BuildResult(models.Model):
    build = models.ForeignKey(Build)
    name = models.CharField(max_length=255)
    body = models.TextField(blank=True)

    def __unicode__(self):
        return '%s - %s' % (self.build, self.name)

    @property
    def buildstate(self):
        # The build state should be FAILED of anything went wrong.
        if int(self.get_testsuites()[0].failures) > 0 \
            or int(self.get_testsuites()[0].failures) > 0:
            return BuildState.FAILED
        else:
            return BuildState.STABLE

    def get_testsuites(self):
        # Create a list of testsuites.
        suites = []
        # Create a stream of xml data.
        s = StringIO(str(self.body))
        # Parse the xml stream.
        root = etree.parse(s)
        # Walk through the xml tree
        for item in root.findall('.'):
            # New testsuite.
            ts = TestSuite(item.attrib)
            suites.append(ts)
            # Walk through tests
            for test in item.iterchildren():
                t = Test(test.attrib)
                ts.testclasses.setdefault(
                    test.attrib['classname'],   
                    TestClass(test.attrib['classname'])
                )
                tc = ts.testclasses[test.attrib['classname']]
                tc.tests.append(t)
                tc.test += 1
                # Append errors and messages.
                for message in test.iterchildren():
                    if message.tag == "error":
                        t.error = True
                        tc.error += 1
                    elif message.tag == "failure":
                        t.failure = True
                        tc.failure += 1
                    m = Message(message.text, message.attrib)
                    t.messages.append(m)
        # Return a list of test suites.
        return suites

class TestSuite(object):
    def __init__(self, attrs):
        self.testclasses = {}
        self.__dict__.update(**attrs)

    def __unicode__(self):
        return str(self.__dict__)

class TestClass(object):
    def __init__(self, name):
        self.name = name
        self.tests = []
        self.error = 0
        self.failure = 0
        self.test = 0
    
class Test(object):
    def __init__(self, attrs):
        self.messages = []
        self.error = False
        self.failure = False
        self.__dict__.update(**attrs)

class Message(object):
    def __init__(self, content, attrs):
        self.content = content
        self.__dict__.update(**attrs)

    def __unicode__(self):
        return str(self.__dict__)
