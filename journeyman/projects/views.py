from django.conf import settings
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponse
from formwizard.forms import SessionFormWizard

from journeyman.projects.models import Project
from journeyman.projects.forms import RepositoryForm, BuildProcessForm, \
    JourneyConfigOutputForm, JourneyConfigFileForm, ProjectForm

from journeyman.workers.models import BuildNode
from django.views.decorators.csrf import csrf_exempt
from django.utils.safestring import mark_safe
def ymlize_list(text):
    if not text:
        return u''
    yml_steps = []
    for line in text.split('\r\n'):
        yml_steps.append('- ' + line)
    return mark_safe(u'\n'.join(yml_steps))

ugly_global = None

class CreateProjectWizard(SessionFormWizard):
    def get_template(self):
        # Return template name based on wizard step
        return ['projects/create_wizard_%s.html' % self.determine_step(),]
        
    def __call__(self, request, *args, **kwargs):
        result = super(CreateProjectWizard, self).__call__(request, *args, **kwargs)
        global ugly_global
        if ugly_global:
            r, ugly_global = ugly_global, None
            return redirect('projects_edit', r)
            
        return result

    def process_step(self, form):
        # If repository form, add the name to extra_context (for use in
        # template.
        if isinstance(form, RepositoryForm):
            if "config" in self.request.POST:
                project = Project.objects.create(**dict(
                    (k,v) for k,v in form.cleaned_data.items()
                ))
                project.save()
                global ugly_global
                ugly_global = project.id
                                
        # If BuildProcess form, we need to generate a config.
        if isinstance(form, BuildProcessForm):
            build_steps = ymlize_list(form.cleaned_data['build_steps'])
            test_steps = ymlize_list(form.cleaned_data['test_steps'])
            # Render a config.
            conf = render_to_string('projects/config', {
                'install': ymlize_list(form.cleaned_data['build_steps']),
                'test': ymlize_list(form.cleaned_data['test_steps']),
                'test_xmls': ymlize_list(form.cleaned_data['test_xmls']),
                'dependencies': ymlize_list(form.cleaned_data['dependencies']),
            })
            print conf
            # Write the config to extra context.
            self.update_extra_context({'config_file': conf})

        # Proceed.
        return self.get_form_step_data(form)

    def done(self, request, form_list):
        # Create a project using every form field with is available in the
        # model.
        project = Project.objects.create(**dict(
            (k,v) for k,v in self.get_all_cleaned_data().items() 
            if k in Project._meta.get_all_field_names()
        ))

        # And add the config data + save.
        project.config_data = self.get_extra_context().get('config_file', '')
        print project.config_data
        project.save()

        # Return a nice info page.
        return render_to_response('projects/create_done.html', {
            'project': project
        }, context_instance=RequestContext(request))

# Create a instance of the project wizard.
create = CreateProjectWizard([RepositoryForm, BuildProcessForm, \
    JourneyConfigOutputForm, JourneyConfigFileForm])

def list(request):
    # List of all active projects and workers.
    return render_to_response('projects/list.html', {
        'object_list': Project.objects.filter(active=True),
        'worker_object_list': BuildNode.objects.filter(active=True),
        'readme': settings.README_HTML,
    }, context_instance=RequestContext(request))

def detail(request, project_id):
    # Try to get the project object
    project = get_object_or_404(Project, pk=project_id)

    # Return template.
    return render_to_response('projects/detail.html', {
        'object': project,
        'outstanding_build_list': project.outstanding_builds,
        'build_list': project.builds.order_by('-started'),
    }, context_instance=RequestContext(request))

def delete(request, project_id):
    # Get the project and delete, then return to overview.
    project = get_object_or_404(Project, pk=project_id)
    project.delete()
    return redirect('projects_list')

def edit(request, project_id):
    # Load the project
    project = get_object_or_404(Project, pk=project_id)

    # Post request?
    if request.method == 'POST':
        # Load and validate the form.
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            # It's valid. Save and return to detail page!
            form.save()
            return redirect('projects_detail', project_id=project.pk)
    else:
        form = ProjectForm(instance=project)

    # Show edit page.
    return render_to_response('projects/edit.html', {
        'object': project,
        'form': form,
    }, context_instance=RequestContext(request))

@csrf_exempt
def wh_post_commit(request, project_id):
    # Get the project.
    project = get_object_or_404(Project, pk=project_id)

    # Create a build for every node.
    for node in BuildNode.objects.filter(active=True):
        build = project.build_set.create(
            node=node
        )
        # Queue the build.
        build.queue_build()

    # At the moment, no more work to do. Return success.
    return HttpResponse('{"status": "success"}', mimetype='application/json')
