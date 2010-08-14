from django.conf.urls.defaults import *

urlpatterns = patterns('builds.views',
    url(r'^create/(?P<project_id>\d+)$', 'create', name='builds_create'),
    url(r'^(?P<build_id>\d+)$', 'detail', name='builds_detail'),
)
