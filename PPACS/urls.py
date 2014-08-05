from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'PPACS.views.home', name='home'),
    url(r'^log/$', 'PPACS.views.log', name='log'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^provider/', include('Provider.urls')),
    url(r'^repository/', include('Repository.urls')),
    url(r'^credentials/', include('CredentialManager.urls')),
    url(r'^blender/', include('Blender.urls')),
    url(r'^client/', include('Client.urls')),
    url(r'^admin/', include(admin.site.urls)),

)
