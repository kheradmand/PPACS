import hashlib
import random
from json import dumps
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from CredentialManager.forms import ExpressionForm
from CredentialManager.models import User
from Provider.models import Expression


def index(request):
    context = {'user_list': User.objects.all()}
    return render(request, 'manager.html', context)


def user_add(request):
    try:
        user = User()
        user.key = hashlib.sha1(str(random.random())).hexdigest()
        user.save()
    except:
        pass
    return HttpResponseRedirect(reverse('manager_index'))


def user_remove(request):
    if 'id' in request.GET.keys():
        user = get_object_or_404(User, id=request.GET['id'])
        user.delete()
    return HttpResponseRedirect(reverse('manager_index'))

def user_index(request, user_id):
    user = get_object_or_404(User, id=user_id)
    context = {'user': user}
    return render(request, 'user.html', context)


def expr_add(request, user_id):
    if request.method == 'POST':
        form = ExpressionForm(request.POST)
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            user = None

        if form.is_valid() and user:
            form.save(user)
            return HttpResponseRedirect(reverse('user_index', kwargs={'user_id': user_id}))
    else:
        form = ExpressionForm()
    return render(request, 'add.html', {'form': form, 'cancel': reverse('user_index', kwargs={'user_id': user_id})})


def expr_remove(request, user_id):
    if 'id' in request.GET.keys():
        id = request.GET['id']
        expr = get_object_or_404(Expression, id=id)
        user = get_object_or_404(User, id=user_id)
        user.attributes.remove(expr)
        user.save()
    return HttpResponseRedirect(reverse('user_index', kwargs={'user_id': user_id}))


def certificate(request, user_id):
    user = get_object_or_404(User, id=user_id)
    data = {}
    data['key'] = user.key
    data['signature'] = ""
    list = []
    for attr in user.attributes.all():
        list.append(
            {'variable': attr.variable,
             'operator': attr.operator,
             'value': attr.value}
        )
    data['attributes'] = list
    hash = hashlib.sha1(dumps(data, sort_keys=True, indent=4, separators=(',', ': '))).hexdigest()
    data['signature'] = hash #TOOD: encrypt it
    return HttpResponse(dumps(data, sort_keys=True, indent=4, separators=(',', ': ')), content_type="application/json")