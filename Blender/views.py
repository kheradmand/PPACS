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
from Client.models import Request, Message, UserPrivacyPrefRule, ChainElement
from PPACS import constraint
from PPACS.constraint import ConstraintChecker
from Provider.models import Purpose


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


        def chain_str(chain):
            ret = ""
            for service in chain:
                ret += "%s::%s -> " % (service.provider.name, service.name)
            return ret[:-4]

        def edit():
            return HttpResponseRedirect(reverse('request_index', kwargs={'request_id': rqst.id}))

        def confirm():
            return HttpResponseRedirect(reverse('request_confirm', kwargs={'request_id': rqst.id}))




        #checking whether blender is correct
        if rqst.blender != blender:
            rqst.add_msg(Message.ERROR, "this is a wrong blender!")
            return edit()

        #loading credentials
        try:
            data = urllib2.urlopen(rqst.certificate).read()
            data = json.loads(data)
        except:
            rqst.add_msg(Message.ERROR, "problem in loading credentials")
            return edit()

        #checking that the signature is correct
        signature = data['signature']
        data['signature'] = ""
        hash = hashlib.sha1(dumps(data, sort_keys=True, indent=4, separators=(',', ': '))).hexdigest()
        if signature != hash:
            rqst.add_msg(Message.ERROR, "certificate is broken")
            return edit()

        #check whether at least one repository is registered
        if len(blender.repos.all()) == 0:
            rqst.add_msg(Message.ERROR, "this blender has no registered repositories")
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
                new_set.add(frozenset(new_need))
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

        if len(need & have) != 0:
            rqst.add_msg(Message.ERROR, "input and output sets must be disjoint")
            return edit()

        if len(need) == 0:
            rqst.add_msg(Message.ERROR, "the output need is currently satisfied")
            return edit()


        # check whether services and the request have fully defined privacy policies for their data usage
        class PolicyCompletenessChecker:
            @staticmethod
            def check_service(rqst, service):
                oks = set([])
                for policy in service.service_privacy_policy_rule_set.all():
                    if len(policy.purpose.all()) > 0:
                        oks.add(policy.dataType)
                not_oks = set([])
                for input in service.inputs.all():
                    for type in set(input.types.all())-not_oks:
                        if type not in oks:
                            rqst.add_msg(Message.WARNING, "service %s::%s have not defined privacy policy for input %s" % (
                                service.name, service.provider.name, type.name
                                                                                       ))
                            not_oks.add(type)
                if not_oks:
                    return False
                else:
                    return True
            @staticmethod
            def clean_services(rqst, services):
                ret = set([])
                for service in services:
                    if PolicyCompletenessChecker.check_service(rqst, service):
                        ret.add(service)
                    else:
                        rqst.add_msg(Message.WARNING, "omitting service %s::%s due to the incompleteness of its privacy policies for its inputs" % (
                                service.name, service.provider.name
                                                                                       ))
                return ret

            @staticmethod
            def check_request(rqst):
                oks = set([])
                for policy in rqst.userprivacypolicyrule_set.all():
                    if len(policy.purpose.all()) > 0:
                       oks.add(policy.dataType)
                ret = True
                for type in rqst.output.types.all():
                    if type not in oks:
                        rqst.add_msg(Message.WARNING, "request did not define any privacy policy for output %s" % type.name)
                        ret = False
                if not ret:
                    rqst.add_msg(Message.ERROR, "can not process request due to incompleteness of its required outputs")
                return ret


        if not PolicyCompletenessChecker.check_request(rqst):
            return edit()
        services = PolicyCompletenessChecker.clean_services(rqst, services)


        #searching for all possible chains
        recurse([], have, need, services)



        rqst.add_msg(Message.INFO, 'analysed %d service chains' % ((stats['failed']+stats['successful']),))
        rqst.add_msg(Message.INFO, '%d failed chains' % stats['failed'])

        #check whether there is any successful service_chain
        if stats['successful'] == 0:
            rqst.add_msg(Message.ERROR, "no service chain can satisfy the output need")
            if len(additional_need_set[0]) > 0:
                msg = "you can add one of the following input sets to your current input set " \
                      "in order to find service chains that can satisfy your output need: "
                count = 0
                for ad_need in additional_need_set[0]:
                    pure_need = ad_need - need
                    if len(pure_need) > 0:
                        count = count + 1
                        msg = msg + repr(pure_need) + " or "

                if (count > 0):
                    msg = msg[:-4]
                    rqst.add_msg(Message.WARNING, msg)
                else:
                    rqst.add_msg(Message.ERROR, "it is impossible to satisfy the request's output need, use a different blender")

            return edit()
        else:
            rqst.add_msg(Message.INFO, '%d successful chains (%d unique chains)' % (stats['successful'], len(service_chains)))


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
        rqst.add_msg(Message.INFO, msg % ('minimum', evaluated_chains[0][0]))
        rqst.add_msg(Message.INFO, msg % ('maximum', evaluated_chains[-1][0]))


        #checking access control constraints
        def check_access_control(service_chain, constraints_stack):
            if len(service_chain) == 0:
                try:
                    print("checking %s" % str(constraints_stack))
                    checker = constraint.ConstraintChecker()
                    for rule in constraints_stack:
                        checker.add_constraints(rule)
                except ConstraintChecker.Error as e:
                    print(e)
                    return False
                return True
            else:
                service = service_chain[0]
                if len(service.access_control_element_set.all()) == 0:
                    return check_access_control(service_chain[1:0], constraints_stack)
                for element in service.access_control_element_set.all():
                    try:
                        constraints = [ConstraintChecker.Constraint(expr.variable, expr.operator, expr.value)
                        for expr in element.userRules.all()] + [ConstraintChecker.Constraint(expr.variable, expr.operator, expr.value)
                        for expr in element.environmentRules.all()]
                    except ConstraintChecker.Error:
                        constraints = []
                        continue
                    constraints_stack.append(tuple(constraints))
                    if check_access_control(service_chain[1:], constraints_stack):
                        return True
                    constraints_stack.pop()
                return False

        user_constraints = []
        try:
            for attr in data['attributes']:
                user_constraints.append(ConstraintChecker.Constraint(attr['variable'], attr['operator'], attr['value']))
        except ConstraintChecker.Error as error:
            rqst.add_msg(Message.ERROR, 'error in user attributes: %s. please check your certificate' % str(error))
        constraints_stack = [tuple(user_constraints)]

        while len(evaluated_chains) > 0:
            if check_access_control(evaluated_chains[0][1], constraints_stack):
                print("this constraints stack was accepted %s", str(constraints_stack))
                break
            else:
                rqst.add_msg(Message.WARNING,
                        'service chain %s with leak value %d was rejected due to violation of access control rules' %
                        (chain_str(evaluated_chains[0][1]), evaluated_chains[0][0])
                        )
                evaluated_chains.pop(0)

        if len(evaluated_chains) == 0:
            rqst.add_msg(Message.ERROR, "no service chain can process your request due to violation of "
                                   "access control rules, use a different blender")
            return edit()


        rqst.add_msg(Message.INFO, 'chose service chain %s with leak value %d' %
                (chain_str(evaluated_chains[0][1]), evaluated_chains[0][0])
        )

        selected_chain = evaluated_chains[0][1]

        #blending service chain privacy policies
        class Policy:

            def __init__(self):
                self.rules = {}

            def __str__(self):
                return str(self.rules)

            def get_types(self):
                return self.rules.keys()

            def add(self, rule):
                var = rule.dataType.name
                if rule.rule_type is None:
                    return
                if var in self.rules.keys():
                    if self.rules[var]['type'] == rule.rule_type:
                        if rule.rule_type == Purpose.ONLY_FOR:
                            self.rules[var]['goals'] &= rule.goal_set()
                        else:
                            self.rules[var]['goals'] |= rule.goal_set()
                    elif not self.rules[var]['goals'].isdisjoint(rule.goal_set()):
                        if rule.rule_type == Purpose.ONLY_FOR:
                           self.rules[var]['goals'] = rule.goal_set()
                        else:
                            pass
                    else:
                        if rule.rule_type == blender.pref:
                            self.rules[var]['goals'] = rule.goal_set()
                        else:
                            pass
                else:
                    self.rules[var] = {'type': rule.rule_type(), 'goals': rule.goal_set()}

            def get_type(self, var):
                if var not in self.rules.keys() or len(self.rules[var]) == 0:
                    return None
                else:
                    return self.rules[var]['type']

            def get_set(self, var):
                if var not in self.rules.keys() or len(self.rules[var]) == 0:
                    return None
                else:
                    return self.rules[var]['goals']


        ok = [True]
        def check_policy(var, p1, p2, name1, name2, io, change_first):
            t1 = p1.get_type(var)
            t2 = p2.get_type(var)
            s1 = p1.get_set(var)
            s2 = p2.get_set(var)

            def error(id1, w1, id2, w2):
                ok[0] = False
                rqst.add_msg(Message.ERROR, "%s conflicts with %s on %s: %s (error #%d)" %
                             (name1, name2, io, var, id1 if change_first else id2))
                if change_first:
                    rqst.add_msg(Message.WARNING, 'try %s for %s: %s' % (w1, io, var))
                else:
                    rqst.add_msg(Message.WARNING, 'try %s for %s: %s' % (w2, io, var))


            if t1 is None:
                pass
            elif t1 == Purpose.ONLY_FOR:
                if t2 is None:
                    error(1,'removing only for %s from %s' % (s1, name1),
                          7, 'adding a subset of only for %s to %s' % (s1, name2)
                    )
                elif t2 == Purpose.ONLY_FOR:
                    if s1 >= s2:
                        pass
                    else:
                        error(2,'adding a subset of only for %s to %s' % (s2-s1, name1, s1-s2, name2),
                          8, 'removing only for %s from %s' % (s2-s1, name2, s1-s2, name2),
                        )
                else:
                    error(3, 'removing only for %s from %s' % (s1, name1),
                          9, 'removing not for %s from %s and adding a subset of only for %s to %s' % (s2, name2, s1, name2)
                    )
            else:
                if t2 is None:
                    error(4, 'removing only for %s from %s' % (s1, name1),
                          10, 'adding an only for a disjoint from %s to %s OR adding a superset of not for %s to %s' % (s1, name2, s1, name2),
                    )
                elif t2 == Purpose.ONLY_FOR:
                    if s1.isdisjoint(s2):
                        pass
                    else:
                       error(5,'removing not for %s from %s' % (s1&s2, name1),
                          11, 'removing only for %s from %s' % (s1&s2, name2),
                        )
                else:
                    if s1 <= s2:
                        pass
                    else:
                        error(6, 'removing not for %s from %s' % (s1-s2, name1),
                          12, 'adding not for %s to %s' % (s1-s2, name2),
                        )


        service_chain_policy = Policy()
        for service in selected_chain:
            for rule in service.service_privacy_policy_rule_set.all():
                service_chain_policy.add(rule)

        user_policy = Policy()
        for rule in rqst.userprivacyprefrule_set.all():
            user_policy.add(rule)

        for input in rqst.assignment_set.all():
            check_policy(input.variable, user_policy, service_chain_policy,
                         "user privacy preferences", "service chain privacy policy",
                         "input", True)


        user_policy = Policy()
        for rule in rqst.userprivacypolicyrule_set.all():
            user_policy.add(rule)

        for output in rqst.output.types.all():
            check_policy(output.name, service_chain_policy, user_policy,
                         "service chain privacy policy", "user privacy policy",
                         "output", False)

        if not ok[0]:
            rqst.add_msg(Message.ERROR, "can not use the service chain due to conflicts between "
                                   "service chain privacy policies and user privacy preferences and policies")
            return edit()



        #everything is ok just need confirmation
        rqst.add_msg(Message.INFO, "service chain %s was finally accepted" % chain_str(selected_chain))
        idx = 0
        for service in selected_chain:
            element = ChainElement()
            element.index = idx
            element.request = rqst
            element.service = service
            element.save()
            idx += 1

        return confirm()


    else:
        return HttpResponseRedirect(reverse('home'))




def confirm(request, blender_id):
    blender = get_object_or_404(Blenderrr, id=blender_id)
    if 'request_id' in request.GET.keys():
        rqst = get_object_or_404(Request, id=request.GET['request_id'])
        if len(rqst.message_set.all()) == 0:
            return HttpResponseServerError()
        chain = [x.service for x in rqst.chainelement_set.order_by('index')]
        rqst.chainelement_set.all().delete()
        rqst.delete()
        return render(request, 'success.html', {'chain': chain})
    else:
        return HttpResponseRedirect(reverse('home'))

