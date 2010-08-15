from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from journeyman.workers.models import BuildNode
from journeyman.workers.forms import WorkerForm

def create(request):
    # Post request?
    if request.method == 'POST':
        # Load the form
        form = WorkerForm(request.POST)
        # Check if the form is valid.
        if form.is_valid():
            # Save the node and return to detail page.
            node = form.save()
            return redirect('workers_detail', worker_id=node.pk)
    else:
        form = WorkerForm()

    # Render template.
    return render_to_response('workers/create.html', {
        'form' : form,
    }, context_instance=RequestContext(request))

def list(request):
    return redirect('projects_list')

# Protect the detail page because of plain visible ssh private keys.
@login_required
def detail(request, worker_id=None):
    # Get the node.
    node = get_object_or_404(BuildNode, pk=worker_id)

    # Return info page.
    return render_to_response('workers/detail.html', {
        'object': node,
    }, context_instance=RequestContext(request))

def delete(request, worker_id):
    # Load the node and remove.
    node = get_object_or_404(BuildNode, pk=worker_id)
    node.delete()
    return redirect('workers_list')

@login_required
def edit(request, worker_id):
    # Load the node.
    node = get_object_or_404(BuildNode, pk=worker_id)
    # Post request?
    if request.method == 'POST':
        # Load and validate form.
        form = WorkerForm(request.POST, instance=node)
        if form.is_valid():
            # Its valid, save and redirect.
            form.save()
            return redirect('workers_detail', worker_id=node.pk)
    else:
        # create a new form.
        form = WorkerForm(instance=node)

    # Render template.
    return render_to_response('workers/edit.html', {
        'object': node,
        'form': form,
    }, context_instance=RequestContext(request))
