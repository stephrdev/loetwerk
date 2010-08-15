from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext
from .models import BuildNode
from .forms import WorkerForm

def create(request):
    if request.method == "POST":
        form = WorkerForm(request.POST)
        if form.is_valid:
            node = form.save()
            return redirect('workers_detail', worker_id=node.pk)
    else:
        form = WorkerForm()
    return render_to_response('workers/create.html', {
        'form' : form,
    }, context_instance=RequestContext(request))
            
def list(request):
    return render_to_response('workers/list.html', {
        'object_list': BuildNode.objects.filter(active=True)
    }, context_instance=RequestContext(request))

def detail(request, worker_id=None):
    node = get_object_or_404(BuildNode, pk=worker_id)

    return render_to_response('workers/detail.html', {
        'object': node,
    }, context_instance=RequestContext(request))

def delete(request, worker_id):
    node = get_object_or_404(Project, pk=worker_id)
    node.delete()
    return redirect('workers_list')

def edit(request, worker_id):
    node = get_object_or_404(BuildNode, pk=worker_id)
    if request.method == 'POST':
        form = WorkerForm(request.POST, instance=node)
        if form.is_valid():
            form.save()
            return redirect('workers_detail', worker_id=node.pk)
    else:
        form = WorkerForm(instance=node)

    return render_to_response('workers/edit.html', {
        'object': node,
        'form': form,
    }, context_instance=RequestContext(request))
