from django.conf.urls.defaults import *

urlpatterns = patterns('projects.views',
    url(r'^$', 'list', name='projects_list'),
    url(r'^create/$', 'create', name='projects_create'),
    url(r'^(?P<project_id>\d+)/$', 'detail', name='projects_detail'),
)
