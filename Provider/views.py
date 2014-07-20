from django.core.urlresolvers   import reverse
from django.views.generic       import ListView
from django.shortcuts           import render, get_object_or_404, HttpResponseRedirect
from django.forms               import *
from django.http                import HttpResponse

from Provider.models import Provider, Service, DataType, ServicePrivacyPolicyRule, Purpose, AccessControlElement,Expression, \
    TypeSet
from Provider.forms  import ProviderForm, ServiceForm, PrivacyPolicyForm, PurposeForm, ExpressionForm, \
    ServiceInputForm, ServiceRegisterForm


def index(request):
    context = {'provider_list': Provider.objects.all()}
    return render(request, 'index.html', context)


def provider_index(request, provider_id):
    provider = get_object_or_404(Provider, pk=provider_id)
    context = {'provider': provider,}
    return render(request, 'provider.html', context)

def provider_add(request):
    if request.method == 'POST':
        form = ProviderForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('index'))
    else:
        form = ProviderForm()

    return render(request, 'add.html', {'form': form, 'cancel': reverse('index')})

def provider_remove(request):
    if 'id' in request.GET.keys():
        pid = request.GET['id']
        Provider.objects.get(pk=pid).delete()
    return HttpResponseRedirect(reverse('index'))

def service_add(request, provider_id, service_id=None):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        try:
            provider = Provider.objects.get(pk=provider_id)
        except Provider.DoesNotExist:
            provider = None

        if form.is_valid() and provider:
            form.save(provider=provider)
            return HttpResponseRedirect(reverse('provider_index', kwargs={'provider_id': provider_id}))
    else:
        if service_id:
            service = get_object_or_404(Service, pk=service_id, provider__id=provider_id)
            form = ServiceForm(instance = service)
        else:
            form = ServiceForm()
    return render(request, 'add.html', {'form': form, 'cancel': reverse('provider_index', kwargs={'provider_id': provider_id})})

def service_remove(request, provider_id):
    if 'id' in request.GET.keys():
        sid = request.GET['id']
        Service.objects.get(pk=sid,provider=Provider.objects.get(pk=provider_id)).delete()
    return HttpResponseRedirect(reverse('provider_index', kwargs={'provider_id': provider_id}))

def service_index(request, provider_id, service_id):
    provider = get_object_or_404(Provider, pk=provider_id)
    service = get_object_or_404(Service, pk=service_id, provider__id=provider_id)
    if request.method == "POST":
        form = ServiceForm(request.POST, instance = service)
        if form.is_valid():
            form.save(provider=provider)
            return HttpResponseRedirect(reverse('provider_index', kwargs={'provider_id': provider_id})) 
    else:
        form = ServiceForm(instance = service)
        context = {'service': service, 'form': form,}
    return render(request, 'service.html', context)


def input_add(request, provider_id, service_id):
    if request.method == 'POST':
        form = ServiceInputForm(request.POST)
        try:
            service = Service.objects.get(pk=service_id)
        except Service.DoesNotExist:
            service = None

        if form.is_valid() and service:
            form.save(service=service)
            return HttpResponseRedirect(reverse('service_index', kwargs={'provider_id': provider_id, 'service_id': service_id}))
    else:
        form = ServiceInputForm()
    return render(request, 'add.html', {'form': form, 'cancel': reverse('service_index', kwargs={'provider_id': provider_id, 'service_id': service_id})})

def input_remove(request, provider_id, service_id):
    if 'id' in request.GET.keys():
        id = request.GET['id']
        service = Service.objects.get(pk=service_id)
        list = TypeSet.objects.get(pk=id)
        service.inputs.remove(list)
        list.delete()
        service.save()
    return HttpResponseRedirect(reverse('service_index', kwargs={'provider_id': provider_id, 'service_id': service_id}))


def policy_add(request, provider_id, service_id):
    if request.method == 'POST':
        try:
            service = Service.objects.get(pk=service_id)
        except Service.DoesNotExist:
            service = None

        form = PrivacyPolicyForm(service, request.POST)

        if form.is_valid() and service:
            form.save()
            return HttpResponseRedirect(reverse('service_index', kwargs={'provider_id': provider_id, 'service_id': service_id}))
    else:
        form = PrivacyPolicyForm(Service.objects.get(pk=service_id))
    return render(request, 'add.html', {'form': form, 'cancel': reverse('service_index', kwargs={'provider_id': provider_id, 'service_id': service_id})})

def policy_remove(request, provider_id, service_id):
    if 'id' in request.GET.keys():
        id = request.GET['id']
        ServicePrivacyPolicyRule.objects.get(pk=id,service=Service.objects.get(pk=service_id)).delete()
    return HttpResponseRedirect(reverse('service_index', kwargs={'provider_id': provider_id, 'service_id': service_id}))

def purpose_add(request, provider_id, service_id, policy_id):
    if request.method == 'POST':
        try:
            policy = ServicePrivacyPolicyRule.objects.get(pk=policy_id)
        except ServicePrivacyPolicyRule.DoesNotExist:
            policy = None
        form = PurposeForm(policy, request.POST)
        if form.is_valid() and policy:
            form.save()
            return HttpResponseRedirect(reverse('service_index', kwargs={'provider_id': provider_id, 'service_id': service_id}))
    else:
        form = PurposeForm(ServicePrivacyPolicyRule.objects.get(pk=policy_id))
    return render(request, 'add.html', {'form': form, 'cancel': reverse('service_index', kwargs={'provider_id': provider_id, 'service_id': service_id})})

def purpose_remove(request, provider_id, service_id, policy_id):
    if 'id' in request.GET.keys():
        id = request.GET['id']
        policy = ServicePrivacyPolicyRule.objects.get(pk=policy_id,service=Service.objects.get(pk=service_id))
        policy.purpose.remove(Purpose.objects.get(pk=id))
    return HttpResponseRedirect(reverse('service_index', kwargs={'provider_id': provider_id, 'service_id': service_id}))

def element_add(request, provider_id, service_id):
    service = Service.objects.get(pk=service_id)
    element = AccessControlElement(service=service)
    element.save()
    return HttpResponseRedirect(reverse('service_index', kwargs={'provider_id': provider_id, 'service_id': service_id}))

def element_remove(request, provider_id, service_id):
    if 'id' in request.GET.keys():
        id = request.GET['id']
        AccessControlElement.objects.get(pk=id,service=Service.objects.get(pk=service_id)).delete()
    return HttpResponseRedirect(reverse('service_index', kwargs={'provider_id': provider_id, 'service_id': service_id}))

def expr_add(request, provider_id, service_id, element_id, target):
    if request.method == 'POST':
        form = ExpressionForm(request.POST)
        try:
            element = AccessControlElement.objects.get(pk=element_id)
        except AccessControlElement.DoesNotExist:
            element = None

        if form.is_valid() and element:
            form.save(element, target)
            return HttpResponseRedirect(reverse('service_index', kwargs={'provider_id': provider_id, 'service_id': service_id}))
    else:
        form = ExpressionForm()
    return render(request, 'add.html', {'form': form, 'cancel': reverse('service_index', kwargs={'provider_id': provider_id, 'service_id': service_id})})


def expr_remove(request, provider_id, service_id, element_id, target):
    if 'id' in request.GET.keys():
        id = request.GET['id']
        element = AccessControlElement.objects.get(pk=element_id)
        expr = Expression.objects.get(pk=id)
        if target == 'user':
            element.userRules.remove(expr)
        else:
            element.environmentRules.remove(expr)
        element.save()
    return HttpResponseRedirect(reverse('service_index', kwargs={'provider_id': provider_id, 'service_id': service_id}))





def service_register(request, provider_id, service_id):
    provider = get_object_or_404(Provider, pk=provider_id)
    service = get_object_or_404(Service, pk=service_id, provider__id=provider_id)
    if request.method == "POST":
        form = ServiceRegisterForm(request.POST, instance = service)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('service_index', kwargs={'provider_id': provider_id, 'service_id': service_id}))
    else:
        form = ServiceRegisterForm(instance = service)

    return render(request, 'add.html', {'form': form, 'cancel': reverse('service_index', kwargs={'provider_id': provider_id, 'service_id': service_id})})

