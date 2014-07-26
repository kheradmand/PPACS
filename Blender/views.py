import hashlib
import json
from json import dumps
import urllib2
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render, get_object_or_404

# Create your views here.
from Blender.forms import BlenderForm
from Blender.models import Blenderrr
from Client.models import Request, Message


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



def blend(request, blender_id):

    blender = get_object_or_404(Blenderrr, id=blender_id)
    if 'request_id' in request.GET.keys():
        id = request.GET['request_id']
        if not Request.objects.filter(id=id).exists():
            return HttpResponseServerError(request)
        rqst = get_object_or_404(Request, id=id)

        def edit():
            return HttpResponseRedirect(reverse('request_index', kwargs={'request_id': rqst.id}))
        def add_msg(type, msg):
            message = Message()
            message.type = type
            message.msg = msg
            message.request = rqst
            message.save()

        #checking whether blender is correct
        if rqst.blender != blender:
            add_msg(Message.ERROR, "this is a wrong blender!")
            return edit()

        #loading credentials
        data = urllib2.urlopen(rqst.certificate).read()
        data = json.loads(data)

        #checking that the signature is correct
        signature = data['signature']
        data['signature'] = ""
        hash = hashlib.sha1(dumps(data, sort_keys=True, indent=4, separators=(',', ': '))).hexdigest()
        if signature != hash:
            add_msg(Message.ERROR, "certificate is broken")
            return edit()

        #check that at least a repository is registered
        if len(blender.repos.all()) == 0:
            add_msg(Message.ERROR, "this blender has no registered repositories")
            return edit()

        ############ now get to work ############
        all_services =





        print(data)
    else:
        return HttpResponseRedirect(reverse('home'))




