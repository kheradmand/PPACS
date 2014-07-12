from django.conf.urls import patterns, url
from Provider import views

urlpatterns = patterns('',
    url(r'^$', views.index, name = 'index'),
    url(r'^add/$', views.provider_add, name = 'provider_add'),
    url(r'^remove/$', views.provider_remove, name = 'provider_remove'),
    url(r'^(?P<provider_name>\w+)/$', views.provider_index, name = 'provider_index'),
    url(r'^(?P<provider_name>\w+)/add/$', views.service_add, name = 'service_add'),
    url(r'^(?P<provider_name>\w+)/remove/$', views.service_remove, name = 'service_remove'),
    url(r'^(?P<provider_name>\w+)/(?P<service_name>\w+)/$', views.service_index, name = 'service_index'),
)
