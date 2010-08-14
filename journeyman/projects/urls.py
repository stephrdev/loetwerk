from django.conf.urls.defaults import *

urlpatterns = patterns('projects.views',
    url(r'create/$', 'create'),
)
