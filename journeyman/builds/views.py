from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext

from journeyman.builds.models import Build, BUILD_STATES
from journeyman.builds.tasks import BuildTask

from journeyman.workers.models import BuildNode
from journeyman.projects.models import Project

def create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    for node in BuildNode.objects.filter(active=True):
        build = Build.objects.create(
            project=project,
            node=node
        )
        BuildTask.delay(build.pk)
        build.state = BUILD_STATES.QUEUED
        build.save()

    return redirect('projects_detail', project_id=project_id)

def detail(request, build_id):
    build = get_object_or_404(Build, pk=build_id)

    return render_to_response('builds/detail.html', {
        'object': build
    }, context_instance=RequestContext(request))

def delete(request, build_id):
    build = get_object_or_404(Build, pk=build_id)
    project_id = build.project.pk
    build.delete()

    return redirect('projects_detail', project_id=project_id)
