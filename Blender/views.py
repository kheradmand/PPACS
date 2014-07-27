import hashlib
import json
from json import dumps
import urllib2
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, HttpResponseServerError, HttpResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
import sys
from Blender.forms import BlenderForm
from Blender.models import Blenderrr
from Client.models import Request, Message, UserPrivacyPrefRule


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
        try:
            data = urllib2.urlopen(rqst.certificate).read()
            data = json.loads(data)
        except:
            add_msg(MemoryError, "problem in loading credentials")
            return edit()

        #checking that the signature is correct
        signature = data['signature']
        data['signature'] = ""
        hash = hashlib.sha1(dumps(data, sort_keys=True, indent=4, separators=(',', ': '))).hexdigest()
        if signature != hash:
            add_msg(Message.ERROR, "certificate is broken")
            return edit()

        #check whether at least one repository is registered
        if len(blender.repos.all()) == 0:
            add_msg(Message.ERROR, "this blender has no registered repositories")
            return edit()

        ############ now get to work ############

        service_chains = set()
        stats = {'failed': 0, 'successful': 0}
        additional_need_set = [set()]

        def add_additional_need(new_need):
            new_set = set()
            add_new_need = True
            for the_need in additional_need_set[0]:
                if new_need < the_need:
                    continue
                else:
                    new_set.add(the_need)
                    if new_need > the_need:
                        add_new_need = False
            if add_new_need:
                new_set.add(new_need)
            additional_need_set[0] = new_set



        def recurse(chain, have, need, services):
            pure_need = need-have
            print (' in chain %s pure need is %s' % ( (str(chain), str(pure_need))))
            if len(pure_need) == 0:
                stats['successful'] += 1
                service_chains.add(tuple(reversed(chain)))
                return
            failed = True
            for service in services:
                if not need.isdisjoint(service.outputs()):
                    failed = False
                    for inputs in service.inputs_set():
                        new_have = have | service.outputs()
                        new_need = need | inputs
                        new_services = services - {service}
                        chain.append(service)
                        recurse(chain, new_have, new_need, new_services)
                        chain.pop()
            if failed:
                stats['failed'] += 1
                add_additional_need(pure_need)


        services = set()
        for repo in blender.repos.all():
            for record in repo.record_set.all():
                services.add(record.service)

        have = set()
        for input in rqst.assignment_set.all():
            have.add(input.variable)

        need = set()
        for output in rqst.output.types.all():
            need.add(output.name)

        if len(need-have) == 0:
            add_msg(Message.ERROR, "the output need is currently satisfied with input")
            return edit()

        #searching for all possible chains
        recurse([], have, need, services)



        add_msg(Message.INFO, 'analysed %d service chains' % ((stats['failed']+stats['successful']),))
        add_msg(Message.INFO, '%d failed chains' % stats['failed'])

        #check if there is any successful service_chain
        if stats['successful'] == 0:
            add_msg(Message.ERROR, "no service chain can satisfy the output need")
            if len(additional_need_set) > 0:
                msg = "you can add one of the following input sets to your current input set " \
                      "in order to find service chains that can satisfy your output need: "
                for need in additional_need_set:
                    msg = msg + str(need) + " or "
                msg = msg[:-4]
                add_msg(Message.WARNING, msg)
            return edit()
        else:
            add_msg(Message.INFO, '%d successful chains (%d unique chains)' % (stats['successful'], len(service_chains)))


        #evaluating the possible chains
        def chain_eval(chain):
            print('evaluating ',str(chain))
            current_have = have.copy()
            print('current have', current_have)
            leak = [0, 0, 0] #high, medium, low
            sensitive_data = (
                rqst.get_sensitive_data(UserPrivacyPrefRule.HIGH),
                rqst.get_sensitive_data(UserPrivacyPrefRule.MEDIUM),
                rqst.get_sensitive_data(UserPrivacyPrefRule.LOW),
            )
            for service in chain:
                min_leak = (sys.maxint, sys.maxint, sys.maxint, sys.maxint)
                for input in service.inputs_set():
                    if input <= current_have:
                        min_leak = min(min_leak,
                                       (
                                            len((input | service.outputs()) & sensitive_data[0]),
                                            len((input | service.outputs()) & sensitive_data[1]),
                                            len((input | service.outputs()) & sensitive_data[2]),
                                            len(input),
                                       ),
                        )
                if min_leak == (sys.maxint, sys.maxint, sys.maxint, sys.maxint):
                    raise Exception('the service chain is invalid')
                current_have |= service.outputs()
                for i in range(3):
                    leak[i] += min_leak[i]
            print('eval is %s' % str(leak))
            return leak[0]*blender.wh+leak[1]*blender.wm+leak[2]*blender.wl

        evaluated_chains = map(lambda chain: (chain_eval(chain), chain), service_chains)
        #sorting by comparing leak values and chain length in case of tie
        evaluated_chains.sort(key=lambda x: (x[0], len(x[1])))
        print(evaluated_chains)

        msg = '%s sensitive data leakage value ' \
              '(with the applied weights for various levels of sensitivity) is %d'
        add_msg(Message.INFO, msg % ('minimum', evaluated_chains[0][0]))
        add_msg(Message.INFO, msg % ('maximum', evaluated_chains[-1][0]))







        #return HttpResponse(str(evaluated_chains))
        return edit()


    else:
        return HttpResponseRedirect(reverse('home'))




