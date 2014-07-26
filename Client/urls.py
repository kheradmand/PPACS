from django.conf.urls import patterns, url
from Client import views

urlpatterns = patterns('',
    url(r'^$', views.new, name = 'new_request'),
    url(r'^(?P<request_id>\w+)/$', views.index, name = 'request_index'),
    url(r'^(?P<request_id>\w+)/cancel$', views.cancel, name = 'cancel_request'),
    url(r'^(?P<request_id>\w+)/input/add/$', views.input_add, name = 'input_add'),
    url(r'^(?P<request_id>\w+)/input/remove/$', views.input_remove, name = 'input_remove'),
    url(r'^(?P<request_id>\w+)/(?P<target>(pref)|(purp))/add/$', views.user_policy_add, name = 'user_policy_add'),
    url(r'^(?P<request_id>\w+)/(?P<target>(pref)|(purp))/remove/$', views.user_policy_remove, name = 'user_policy_remove'),
    url(r'^(?P<request_id>\w+)/(?P<target>(pref)|(purp))/(?P<target_id>\w+)/purpose/add$', views.purpose_add, name = 'rule_add'),
    url(r'^(?P<request_id>\w+)/(?P<target>(pref)|(purp))/(?P<target_id>\w+)/purpose/remove', views.purpose_remove, name = 'rule_remove'),
    # url(r'^(?P<provider_id>\w+)/$', views.provider_index, name = 'provider_index'),
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
