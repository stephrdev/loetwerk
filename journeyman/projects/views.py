from tempfile import mkdtemp

from django import forms
from django.template import RequestContext
from django.shortcuts import render_to_response
from formwizard.forms import SessionFormWizard

from .models import Project

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


class RegisterRepository(forms.Form):
    name = forms.CharField(help_text="What's the name of your awesome project?")
    repository = forms.CharField(help_text="Please enter a valid repository url (e.g. git+git://github.com/stephrdev/loetwerk.git)")
    
class BuildProcess(forms.Form):
    build_steps = forms.CharField(initial="python setup.py install", widget=forms.Textarea(attrs={'rows':3, 'cols':40}), help_text="Let's start off with the easy stuff, please type in all the commands needed to install your package")
    test_steps = forms.CharField(initial="python setup.py test", widget=forms.Textarea(attrs={'rows':3, 'cols':40}), help_text="Now tell us how to run your tests. If you should have many different test suites, just add another line.")
    
    dependencies = forms.CharField(initial="dependencies.txt", widget=forms.Textarea(attrs={'rows':3, 'cols':40}), help_text="Please enter a list of pip requirement files that you have used to specify your dependencies")
    
    test_xmls = forms.CharField(required=False, help_text="Please enter a whitespace separated list of paths of unit test result xmls.") 

class UploadJourneyConfig(forms.Form):
    pass
    
class JourneyConfiguration(forms.Form):
    config_file = forms.CharField(initial="journey.conf/config")

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
        print dir(Project._meta)
        Project(**dict((k,v) for k,v in all_attrs.items() if k in Project._meta.get_all_field_names())).save()
        return render_to_response(
            'projects/done.html',
            {'form_list': [form.cleaned_data for form in form_list]},
            context_instance=RequestContext(request)
        )

create = ProjectWizard([RegisterRepository, BuildProcess, UploadJourneyConfig, JourneyConfiguration])