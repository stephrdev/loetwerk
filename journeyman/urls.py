from django.conf.urls.defaults import *
from settings import MEDIA_ROOT
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^projects/', include("projects.urls")),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': MEDIA_ROOT}),
    
)
