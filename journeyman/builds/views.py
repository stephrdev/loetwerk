from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext

from journeyman.builds.models import Build, BuildResult, BuildState
from journeyman.builds.tasks import BuildTask
from journeyman.workers.models import BuildNode
from journeyman.projects.models import Project

from django.contrib import messages

def create(request, project_id):
    # Try to get the project
    project = get_object_or_404(Project, pk=project_id)
    
    build = None
    print dir(request)
    # Look for available nodes.
    for node in BuildNode.objects.filter(active=True):
        # Add a build for every node.
        build = Build.objects.create(
            project=project,
            node=node
        )
        # Queue the build.
        build.queue_build()
    
    if not build:
        messages.add_message(request, messages.ERROR, "No build server available")
        print request._messages
        return redirect('projects_detail', project.pk)
    # Return to the build detail page.
    return redirect('builds_detail', build_id=build.pk)

def detail(request, build_id):
    # Try to get the build.
    build = get_object_or_404(Build, pk=build_id)

    # Return a nice rendered page.
    return render_to_response('builds/detail.html', {
        'object': build
    }, context_instance=RequestContext(request))

def detail_tests(request, build_id):
    # Get the build.
    build = get_object_or_404(Build, pk=build_id)

    # Load all test suites and stick them together.
    suites = []
    results = BuildResult.objects.filter(build=build)
    for result in results:
        suites.extend(result.get_testsuites())

    # Return a template.
    return render_to_response('builds/detail_tests.html', {
        'suites': suites,
        'object': build
    }, context_instance=RequestContext(request))

def delete(request, build_id):
    # Load the build.
    build = get_object_or_404(Build, pk=build_id)

    # Remember the project id.
    project_id = build.project.pk

    # Delete the build.
    build.delete()

    # Return to project detail page.
    return redirect('projects_detail', project_id=project_id)
