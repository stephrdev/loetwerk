from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponse
from formwizard.forms import SessionFormWizard

from journeyman.projects.models import Project
from journeyman.projects.forms import RepositoryForm, BuildProcessForm, \
    JourneyConfigOutputForm, JourneyConfigFileForm, ProjectForm

from journeyman.workers.models import BuildNode
from django.views.decorators.csrf import csrf_exempt

template_config = """build:
- dependencies[fetch_pip_dependencies]
- install
- test[run_tests]
- testresults[fetch_xuint_results]

dependencies[fetch_pip_dependencies]:
%(dependencies)s

install:
%(install)s

test[run_tests]:
%(test)s

testresults[fetch_xunit_results]:
%(test_xmls)s
"""

def ymlize_list(text):
    if not text:
        return ""
    yml_steps = []
    for line in text.split('\r\n'):
        yml_steps.append("- " + line)
    return "\n".join(yml_steps)

class CreateProjectWizard(SessionFormWizard):
    def get_template(self):
        return ['projects/create_wizard_%s.html' % self.determine_step(),]

    def process_step(self, form):
        if isinstance(form, RepositoryForm):
            self.update_extra_context({'name': form.cleaned_data['name']})

        if isinstance(form, BuildProcessForm):
            build_steps = ymlize_list(form.cleaned_data['build_steps'])
            test_steps = ymlize_list(form.cleaned_data['test_steps'])

            conf = template_config % {
                'install': ymlize_list(form.cleaned_data['build_steps']),
                'test': ymlize_list(form.cleaned_data['test_steps']), 
                'test_xmls': ymlize_list(form.cleaned_data['test_xmls']),
                'dependencies': ymlize_list(form.cleaned_data['dependencies']),
            }
            self.update_extra_context({'config_file': conf})

        return self.get_form_step_data(form)

    def done(self, request, form_list):
        project = Project.objects.create(**dict(
            (k,v) for k,v in self.get_all_cleaned_data().items() 
            if k in Project._meta.get_all_field_names()
        ))
        project.config_data = self.get_extra_context().get('config_file', '')
        project.save()

        return render_to_response('projects/create_done.html', {
            'project': project
        }, context_instance=RequestContext(request))

create = CreateProjectWizard([RepositoryForm, BuildProcessForm, \
    JourneyConfigOutputForm, JourneyConfigFileForm])

def list(request):
    return render_to_response('projects/list.html', {
        'object_list': Project.objects.filter(active=True)
    }, context_instance=RequestContext(request))

def detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    return render_to_response('projects/detail.html', {
        'object': project,
        'outstanding_build_list': project.outstanding_builds,
        'build_list': project.builds.order_by('-started'),
    }, context_instance=RequestContext(request))

def delete(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    project.delete()

    return redirect('projects_list')

def edit(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('projects_detail', project_id=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render_to_response('projects/edit.html', {
        'object': project,
        'form': form,
    }, context_instance=RequestContext(request))

@csrf_exempt
def wh_post_commit(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    for node in BuildNode.objects.filter(active=True):
        build = project.build_set.create(
            node=node
        )
        build.queue_build()
    return HttpResponse('{"status": "success"}', mimetype="application/json")
