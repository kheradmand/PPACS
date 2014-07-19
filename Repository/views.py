from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

# Create your views here.
from Repository.forms import RepositoryForm
from Repository.models import Repository, Record


def index(request):
    context = {'repository_list': Repository.objects.all()}
    return render(request, 'repo_index.html', context)

def repository_add(request):
    if request.method == 'POST':
        form = RepositoryForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('indexx'))
    else:
        form = RepositoryForm()

    return render(request, 'add.html', {'form': form, 'cancel': reverse('index')})

def repository_remove(request):
    if 'id' in request.GET.keys():
        pid = request.GET['id']
        Repository.objects.get(pk=pid).delete()
    return HttpResponseRedirect(reverse('indexx'))


def repository_index(request, repository_id):
    repository = get_object_or_404(Repository, pk=repository_id)
    records = {}
    for record in repository.record_set.all():
        if record.service.name not in records.keys():
            records[record.service.name] = [record,]
        else:
            records[record.service.name].append(record)
    print(records)
    context = {'repository': repository, 'records':records}
    return render(request, 'repository.html', context)


def record_remove(request, repository_id):
    if 'id' in request.GET.keys():
        pid = request.GET['id']
        Record.objects.get(pk=pid).delete()
    return HttpResponseRedirect(reverse('repository_index', kwargs={'repository_id': repository_id}))


