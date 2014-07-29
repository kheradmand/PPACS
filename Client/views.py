from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render, get_object_or_404

# Create your views here.
from Client.forms import RequestForm, ClientInputForm, PrivacyPrefForm, PrivacyPurpForm
from Client.models import Request, Assignment, UserPrivacyPrefRule, UserPrivacyPolicyRule
from Provider.forms import PurposeForm
from Provider.models import Purpose


def new(request):
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            rqst = form.save()
            return HttpResponseRedirect(reverse('request_index', kwargs={'request_id': rqst.id}))
    else:
        form = RequestForm()
    return render(request, 'add.html', {'form': form, 'cancel': reverse('home')})


def index(request, request_id):
    rqst = get_object_or_404(Request, id=request_id)
    if request.method == "POST":
        form = RequestForm(request.POST, instance=rqst)
        if form.is_valid():
            form.save()
            #clear messages
            rqst.message_set.all().delete()
            #now submit the request to the blender
            url = '%s?request_id=%d' % (reverse('blender_blend', kwargs={'blender_id': rqst.blender.id}), rqst.id)
            return HttpResponseRedirect(url)
    else:
        form = RequestForm(instance=rqst)
    context = {'request': rqst, 'form': form,}
    return render(request, 'client.html', context)


def cancel(request, request_id):
    rqst = get_object_or_404(Request, id=request_id)
    rqst.delete()
    return HttpResponseRedirect(reverse('home'))

def confirm(request, request_id):
    rqst = get_object_or_404(Request, id=request_id)
    if len(rqst.chainelement_set.all()) == 0:
        return HttpResponseServerError()
        rqst.delete()
    url = '%s?request_id=%d' % (reverse('blender_confirm', kwargs={'blender_id': rqst.blender.id}), rqst.id)
    context = {'request': rqst, 'proceed_link': url}
    return render(request, 'confirm.html', context)

def input_add(request, request_id):
    rqst = get_object_or_404(Request, id=request_id)
    if request.method == 'POST':
        form = ClientInputForm(rqst, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('request_index', kwargs={'request_id': request_id}))
    else:
        form = ClientInputForm(rqst)
    return render(request, 'add.html', {'form': form, 'cancel': reverse('request_index', kwargs={'request_id': request_id})})

def input_remove(request, request_id):
    rqst = get_object_or_404(Request, id=request_id)
    if 'id' in request.GET.keys():
        id = request.GET['id']
        input = Assignment.objects.get(pk=id)
        input.delete()
    return HttpResponseRedirect(reverse('request_index', kwargs={'request_id': request_id}))

def user_policy_add(request, request_id, target):
    rqst = get_object_or_404(Request, id=request_id)
    if request.method == 'POST':
        if target == "pref":
            form = PrivacyPrefForm(rqst, request.POST)
        else:
            form = PrivacyPurpForm(rqst, request.POST)
        if form.is_valid():
            form.save(rqst)
            return HttpResponseRedirect(reverse('request_index', kwargs={'request_id': request_id}))
    else:
        if target == "pref":
            form = PrivacyPrefForm(rqst)
        else:
            form = PrivacyPurpForm(rqst)
    return render(request, 'add.html', {'form': form, 'cancel': reverse('request_index', kwargs={'request_id': request_id})})

def user_policy_remove(request, request_id, target):
    rqst = get_object_or_404(Request, id=request_id)
    if 'id' in request.GET.keys():
        id = request.GET['id']
        if target == "pref":
            UserPrivacyPrefRule.objects.get(id=id).delete()
        else:
            UserPrivacyPolicyRule.objects.get(id=id).delete()
    return HttpResponseRedirect(reverse('request_index', kwargs={'request_id': request_id}))

def purpose_add(request, request_id, target, target_id):
    rqst = get_object_or_404(Request, id=request_id)
    if target == "pref":
        policy = get_object_or_404(UserPrivacyPrefRule,id=target_id)
    else:
        policy = get_object_or_404(UserPrivacyPolicyRule,id=target_id)
    if request.method == 'POST':
        form = PurposeForm(policy, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('request_index', kwargs={'request_id': request_id}))
    else:
        form = PurposeForm(policy)
    return render(request, 'add.html', {'form': form, 'cancel': reverse('request_index', kwargs={'request_id': request_id})})

def purpose_remove(request, request_id, target, target_id):
    rqst = get_object_or_404(Request, id=request_id)
    if target == "pref":
        policy = get_object_or_404(UserPrivacyPrefRule,id=target_id)
    else:
        policy = get_object_or_404(UserPrivacyPolicyRule,id=target_id)
    if 'id' in request.GET.keys():
        id = request.GET['id']
        policy.purpose.remove(Purpose.objects.get(pk=id))
    return HttpResponseRedirect(reverse('request_index', kwargs={'request_id': request_id}))