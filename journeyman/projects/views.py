from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect

from formwizard.forms import SessionFormWizard

from journeyman.projects.models import Project
from journeyman.projects.forms import RepositoryForm, BuildProcessForm, \
    JourneyConfigOutputForm, JourneyConfigFileForm, ProjectForm

template_config = """build:
- dependencies
- install
- test

install:
%(install)s

test:
%(test)s

options:
- unittest-xml-results: %(test_xmls)s
- pip-dependencies: %(dependencies)s
"""

def ymlize_list(text):
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
                'install': build_steps, 
                'test': test_steps, 
                'test_xmls': form.cleaned_data['test_xmls'],
                'dependencies': form.cleaned_data['dependencies']
            }
            self.update_extra_context({'config_file': conf})

        return self.get_form_step_data(form)

    def done(self, request, form_list):
        project = Project.objects.create(**dict(
            (k,v) for k,v in self.get_all_cleaned_data().items() 
            if k in Project._meta.get_all_field_names()
        ))

        return render_to_response('projects/create_done.html', {
            'object': project
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
