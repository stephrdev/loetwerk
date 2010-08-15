from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import redirect_to

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', redirect_to, {'url': '/projects/'}),
    (r'^admin/', include(admin.site.urls)),

    (r'^projects/', include('journeyman.projects.urls')),
    (r'^builds/', include('journeyman.builds.urls')),
    (r'^workers/', include('journeyman.workers.urls')),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
)
