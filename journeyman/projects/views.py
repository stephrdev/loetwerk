from tempfile import mkdtemp

from django import forms
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from formwizard.forms import SessionFormWizard

from journeyman.projects.models import Project
from journeyman.projects.forms import RegisterRepository, BuildProcess, UploadJourneyConfig, JourneyConfiguration

template_config = """
build:
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

class ProjectWizard(SessionFormWizard):
    def get_template(self):
        return ['projects/wizard_%s.html' % self.determine_step(),]
    
    def process_step(self, form):
        if isinstance(form, RegisterRepository):
            self.update_extra_context({"name": form.cleaned_data["name"]})
        if isinstance(form, BuildProcess):
            build_steps = ymlize_list(form.cleaned_data["build_steps"])
            test_steps = ymlize_list(form.cleaned_data["test_steps"])
            deps = form.cleaned_data.get("dependencies", "")
            conf = template_config % {"install": build_steps, 
                                      "test": test_steps, 
                                      "test_xmls": form.cleaned_data["test_xmls"],
                                      "dependencies": deps}
            self.update_extra_context({"config_file": conf})
        return self.get_form_step_data(form)
    
    def done(self, request, form_list):
        all_attrs = self.get_all_cleaned_data()
        project = Project(**dict((k,v) for k,v in all_attrs.items() if k in Project._meta.get_all_field_names())).save()
        return render_to_response(
            'projects/done.html',
            {'object': project},
            context_instance=RequestContext(request)
        )

create = ProjectWizard([RegisterRepository, BuildProcess, UploadJourneyConfig, JourneyConfiguration])

def list(request):
    return render_to_response(
        'projects/list.html',
        {'object_list': Project.objects.filter(active=True)},
        context_instance=RequestContext(request)
    )

def detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return render_to_response(
        'projects/detail.html',
        {'object': project,
        'build_list': project.build_set.all().order_by('-started')},
        context_instance=RequestContext(request)
    )