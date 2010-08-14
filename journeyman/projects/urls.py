from django.conf.urls.defaults import *

urlpatterns = patterns('projects.views',
    url(r'create/$', 'create', name="projects_create"),
    url(r'(\d+)/', 'detail', name="projects_detail"),
    url(r'^$', 'overview', name="projects_overview"),
)
