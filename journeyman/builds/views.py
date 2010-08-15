from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext

from journeyman.builds.models import Build, BuildResult, BuildState
from journeyman.builds.tasks import BuildTask

from journeyman.workers.models import BuildNode
from journeyman.projects.models import Project

from lxml import etree
from StringIO import StringIO

def create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    for node in BuildNode.objects.filter(active=True):
        build = Build.objects.create(
            project=project,
            node=node
        )
        BuildTask.delay(build.pk)
        build.state = BuildState.QUEUED
        build.save()

    return redirect('projects_detail', project_id=project_id)

def detail(request, build_id):
    build = get_object_or_404(Build, pk=build_id)

    return render_to_response('builds/detail.html', {
        'object': build
    }, context_instance=RequestContext(request))

class TestSuite(object):
    def __init__(self, attrs):
        self.testcases = []
        self.__dict__.update(**attrs)

    def __unicode__(self):
        return str(self.__dict__)

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
        
def detail_tests(request, build_id):
    build = get_object_or_404(Build, pk=build_id)
    suites = []
    results = BuildResult.objects.filter(build=build)
    for result in results:
        s = StringIO(str(result.body))
        root = etree.parse(s)
        print etree.tostring(root, pretty_print=True)
        for item in root.findall('.'):
            ts = TestSuite(item.attrib)
            suites.append(ts)
            for test in item.iterchildren():
                t = Test(test.attrib)
                ts.testcases.append(t)
                for message in test.iterchildren():
                    if message.tag == "error":
                        t.error = True
                    elif message.tag == "failure":
                        t.failure = True
                    m = Message(message.text, message.attrib)
                    t.messages.append(m)

    return render_to_response('builds/detail_tests.html', {
        'suites': suites
    }, context_instance=RequestContext(request))

def delete(request, build_id):
    build = get_object_or_404(Build, pk=build_id)
    project_id = build.project.pk
    build.delete()

    return redirect('projects_detail', project_id=project_id)
