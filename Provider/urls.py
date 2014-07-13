from django.conf.urls import patterns, url
from Provider import views

urlpatterns = patterns('',
    url(r'^$', views.index, name = 'index'),
    url(r'^add/$', views.provider_add, name = 'provider_add'),
    url(r'^remove/$', views.provider_remove, name = 'provider_remove'),
    url(r'^(?P<provider_id>\w+)/$', views.provider_index, name = 'provider_index'),
    url(r'^(?P<provider_id>\w+)/add/$', views.service_add, name = 'service_add'),
    url(r'^(?P<provider_id>\w+)/remove/$', views.service_remove, name = 'service_remove'),
    url(r'^(?P<provider_id>\w+)/(?P<service_id>\w+)/$', views.service_index, name = 'service_index'),
    url(r'^(?P<provider_id>\w+)/(?P<service_id>\w+)/policy/add/$', views.policy_add, name = 'policy_add'),
    url(r'^(?P<provider_id>\w+)/(?P<service_id>\w+)/policy/remove/$', views.policy_remove, name = 'policy_remove'),
    url(r'^(?P<provider_id>\w+)/(?P<service_id>\w+)/(?P<policy_id>\w+)/purpose/add/$', views.purpose_add, name = 'purpose_add'),
    url(r'^(?P<provider_id>\w+)/(?P<service_id>\w+)/(?P<policy_id>\w+)/purpose/remove/$', views.purpose_remove, name = 'purpose_remove'),
    url(r'^(?P<provider_id>\w+)/(?P<service_id>\w+)/element/add/$', views.element_add, name = 'element_add'),
    url(r'^(?P<provider_id>\w+)/(?P<service_id>\w+)/element/remove/$', views.element_remove, name = 'element_remove'),
    url(r'^(?P<provider_id>\w+)/(?P<service_id>\w+)/(?P<element_id>\w+)/(?P<target>(user)|(env))/expr/add/$', views.expr_add, name = 'expr_add'),
    url(r'^(?P<provider_id>\w+)/(?P<service_id>\w+)/(?P<element_id>\w+)/(?P<target>(user)|(env))/expr/remove/$', views.expr_remove, name = 'expr_remove'),

)
