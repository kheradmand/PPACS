from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

# Create your views here.
from Blender.forms import BlenderForm
from Blender.models import Blenderrr


def index(request):
    print('here')
    context = {'blender_list': Blenderrr.objects.all()}
    print(Blenderrr.objects.all())
    return render(request, 'blender.html', context)


def blender_add(request):
    if request.method == 'POST':
        form = BlenderForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('blenders'))
    else:
        form = BlenderForm()
    return render(request, 'add.html', {'form': form, 'cancel': reverse('blenders')})

def blender_index(request, blender_id):
    blender = get_object_or_404(Blenderrr, id=blender_id)
    if request.method == 'POST':
        form = BlenderForm(request.POST, instance=blender)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('blenders'))
    else:
        form = BlenderForm(instance=blender)
    return render(request, 'add.html', {'form': form, 'cancel': reverse('blenders')})

def blender_remove(request):
    if 'id' in request.GET.keys():
        id = request.GET['id']
        blender = get_object_or_404(Blenderrr, id=id)
        blender.delete()
    return HttpResponseRedirect(reverse('blenders'))

