from django.conf.urls import patterns, url
from Blender import views

urlpatterns = patterns('',
    url(r'^$', views.index, name = 'blenders'),
    url(r'^add/$', views.blender_add, name = 'blender_add'),
    url(r'^remove/$', views.blender_remove, name = 'blender_remove'),
    url(r'^(?P<blender_id>\w+)/$', views.blender_index, name = 'blender_index'),
    url(r'^(?P<blender_id>\w+)/blend/$', views.blend, name = 'blender_blend'),
    url(r'^(?P<blender_id>\w+)/blend/confirm$', views.confirm, name = 'blender_confirm'),
    #url(r'^(?P<user_id>\w+)/expr/add/$', views.expr_add, name = 'expr_add'),
    #url(r'^(?P<user_id>\w+)/expr/remove/$', views.expr_remove, name = 'expr_remove'),
    # url(r'^(?P<provider_id>\w+)/add/$', views.service_add, name = 'service_add'),
    # url(r'^(?P<provider_id>\w+)/remove/$', views.service_remove, name = 'service_remove'),
    # url(r'^(?P<provider_id>\w+)/(?P<service_id>\w+)/$', views.service_index, name = 'service_index'),
    # url(r'^(?P<provider_id>\w+)/(?P<service_id>\w+)/input/add/$', views.input_add, name = 'input_add'),
    # url(r'^(?P<provider_id>\w+)/(?P<service_id>\w+)/input/remove/$', views.input_remove, name = 'input_remove'),
    # url(r'^(?P<provider_id>\w+)/(?P<service_id>\w+)/policy/add/$', views.policy_add, name = 'policy_add'),
    # url(r'^(?P<provider_id>\w+)/(?P<service_id>\w+)/policy/remove/$', views.policy_remove, name = 'policy_remove'),
    # url(r'^(?P<provider_id>\w+)/(?P<service_id>\w+)/(?P<policy_id>\w+)/purpose/add/$', views.purpose_add, name = 'purpose_add'),
    # url(r'^(?P<provider_id>\w+)/(?P<service_id>\w+)/(?P<policy_id>\w+)/purpose/remove/$', views.purpose_remove, name = 'purpose_remove'),
    # url(r'^(?P<provider_id>\w+)/(?P<service_id>\w+)/element/add/$', views.element_add, name = 'element_add'),
    # url(r'^(?P<provider_id>\w+)/(?P<service_id>\w+)/element/remove/$', views.element_remove, name = 'element_remove'),
    # url(r'^(?P<provider_id>\w+)/(?P<service_id>\w+)/(?P<element_id>\w+)/(?P<target>(user)|(env))/expr/add/$', views.expr_add, name = 'expr_add'),
    # url(r'^(?P<provider_id>\w+)/(?P<service_id>\w+)/(?P<element_id>\w+)/(?P<target>(user)|(env))/expr/remove/$', views.expr_remove, name = 'expr_remove'),
    #
    # url(r'^(?P<provider_id>\w+)/(?P<service_id>\w+)/register$', views.service_register, name = 'service_register'),

)
