from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from Provider.models import Provider, Service, DataType
from django.forms import *
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.generic import ListView

# Create your views here.

class ServiceForm(forms.Form):
    output = CharField()
    function = URLField(required=False)


def index(request):
    context = {'provider_list': Provider.objects.all()}
    return render(request, 'index.html', context)


def provider_index(request, provider_name):
    provider = get_object_or_404(Provider, name=provider_name)
    context = {'provider': provider,}
    return render(request, 'provider.html', context)

def provider_add(request):
    if 'name' in request.GET.keys():
        name = request.GET['name']
        try:
            provider = Provider(name=name)
            provider.save()
        except:
            pass
        return HttpResponseRedirect(reverse('index'))
    else:
        class InputForm(forms.Form):
            name = CharField(initial='new_provider')
        form = InputForm()
        return render(request, 'provider_add.html', {'form': form})



def provider_remove(request):
    if 'name' in request.GET.keys():
        name = request.GET['name']
        Provider.objects.get(name=name).delete()
    return HttpResponseRedirect(reverse('index'))

def service_add(request, provider_name):
    if 'name' in request.GET.keys():
        name = request.GET['name']
        try:
            service = Service(name=name,provider=Provider.objects.get(name=provider_name),output=DataType.objects.get(name='null'))
            service.save()
        except:
            print('exception!')
        return HttpResponseRedirect(reverse('provider_index', kwargs={'provider_name': provider_name}))
    else:
        class InputForm(forms.Form):
            name = CharField(initial='new_service')
        form = InputForm()
        return render(request, 'service_add.html', {'form': form})

def service_remove(request, provider_name):
    if 'name' in request.GET.keys():
        name = request.GET['name']
        Service.objects.get(name=name,provider=Provider.objects.get(name=provider_name)).delete()
    return HttpResponseRedirect(reverse('provider_index', kwargs={'provider_name': provider_name}))

def service_index(request, provider_name, service_name):
    provider = get_object_or_404(Provider, name=provider_name)
    service = get_object_or_404(Service, name=service_name, provider=provider)
    form = ServiceForm(initial={'output': service.output.name, 'function': service.function})
    context = {'service': service, 'form': form,}
    return render(request, 'service.html', context)



