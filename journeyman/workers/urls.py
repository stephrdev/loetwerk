from django.conf.urls.defaults import *

urlpatterns = patterns('workers.views',
    url(r'^$', 'list', name='workers_list'),
    url(r'^create/$', 'create', name='workers_create'),
    url(r'^(?P<worker_id>\d+)/$', 'detail', name='workers_detail'),
    url(r'^delete/(?P<worker_id>\d+)/$', 'delete', name='workers_delete'),
    url(r'^edit/(?P<worker_id>\d+)/$', 'edit', name='workers_edit'),
)
