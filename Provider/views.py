from django.core.urlresolvers   import reverse
from django.views.generic       import ListView
from django.shortcuts           import render, get_object_or_404, HttpResponseRedirect
from django.forms               import *
from django.http                import HttpResponse

from Provider.models import Provider, Service, DataType
from Provider.forms  import ProviderForm, ServiceForm

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

    return render(request, 'provider_add.html', {'form': form})

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
    return render(request, 'service_add.html', {'form': form})

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



