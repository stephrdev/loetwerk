from django.conf.urls.defaults import *

urlpatterns = patterns('builds.views',
    url(r'^create/(?P<project_id>\d+)$', 'create', name='builds_create'),
    url(r'^delete/(?P<build_id>\d+)$', 'delete', name='builds_delete'),
    url(r'^(?P<build_id>\d+)$', 'detail', name='builds_detail'),
    url(r'^(?P<build_id>\d+)/tests/$', 'detail_tests', name='builds_detail_tests'),
)
