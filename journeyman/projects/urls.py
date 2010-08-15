from django.conf.urls.defaults import *

urlpatterns = patterns('projects.views',
    url(r'^$', 'list', name='projects_list'),
    url(r'^create/$', 'create', name='projects_create'),
    url(r'^(?P<project_id>\d+)/$', 'detail', name='projects_detail'),
    url(r'^delete/(?P<project_id>\d+)/$', 'delete', name='projects_delete'),
    url(r'^edit/(?P<project_id>\d+)/$', 'edit', name='projects_edit'),
    url(r'^post-commit-hook/(?P<project_id>\d+)/$', 'wh_post_commit', name='projects_wh_post_commit'),
)
