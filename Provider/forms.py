from __builtin__ import set
from django          import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import Textarea
from PPACS import constraint
from Provider.models import Provider, Service, DataType, ServicePrivacyPolicyRule, Purpose, Goal, Expression, \
    TypeSet
import re


# cleaned data is a models.TypeSet object
from Repository.models import Repository, Record


class TypeSetField(forms.Field):
    def __init__(self, *args, **kwargs):
        super(TypeSetField, self).__init__(*args, **kwargs)
        self.initial = '{}'

    def to_python(self, value):
        striped = value.strip()
        if striped[0] != '{' or striped[-1] != '}':
            raise ValidationError(('set should start with { and end with }'))
        striped = striped[1:-1]
        splited = striped.split(',')
        ret = set()
        if len(splited) == 0 or (len(splited) == 1 and not splited[0].strip()):
            if self.required:
                raise ValidationError(('set can not be empty'))
            else:
                return ret

        for val in splited:
            striped = val.strip()
            if not striped:
                continue
            if re.match('[a-zA-Z0-9_]\w*',striped) is None:
                raise ValidationError(('invalid type name: "%(name)s"'),
                                          params={'name': striped}
                )
            ret.add(striped)
        return ret

    def clean(self, value):
        cleaned = super(TypeSetField, self).clean(value)
        set = TypeSet()
        set.save()
        for type in cleaned:
            set.types.add(DataType.objects.get_or_create(name=type)[0])
        set.save()
        return set



class ServiceForm(forms.ModelForm):
    output = TypeSetField()

    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        try:
            self.fields['output'].initial = self.instance.output
        except:
            pass

    class Meta:
        model = Service
        fields = ('name', 'function')


    def save(self, provider):
        service = super(ServiceForm, self).save(commit = False)
        service.provider = provider
        service.output = self.cleaned_data['output']
        service.save()
        return service


class ProviderForm(forms.ModelForm):
    class Meta:
        model = Provider

# class TypeListForm(forms.ModelForm):
#     class Meta:
#         model = TypeList
#
#     def save(self, service):
#         list = super(TypeListForm, self).save(commit = False)
#         list.save()
#         service.inputs.add(list)
#         service.save()
#         return list

class ServiceInputForm(forms.Form):
    set = TypeSetField()

    def __init__(self,service, *args, **kwargs):
        super(ServiceInputForm, self).__init__(*args, **kwargs)
        self.service = service

    def clean_set(self):
        sett = self.cleaned_data['set']
        if not set(sett.types.all()).isdisjoint(self.service.output.types.all()):
            raise ValidationError("input set must be disjoint from output set")
        return sett

    def save(self):
        set = self.cleaned_data['set']
        self.service.inputs.add(set)
        self.service.save()
        return set

class PrivacyPolicyForm(forms.ModelForm):
    type = forms.ChoiceField()

    def __init__(self, service, *args, **kwargs):
        super(PrivacyPolicyForm, self).__init__(*args, **kwargs)
        self.service = service
        unq = set()
        for sett in service.inputs.all():
            for type in sett.types.all():
                unq.add(type)
        for type in service.output.types.all():
            unq.add(type)
        #removing the ones that are currently added
        for rule in service.service_privacy_policy_rule_set.all():
            unq.remove(rule.dataType)
        choices = []

        for type in unq:
            choices.append((type, str(type)))
        print(choices)
        self.fields['type'].choices = choices
        try:
            self.fields['type'].initial = self.instance.dataType.name
        except:
            pass

    class Meta:
        model = ServicePrivacyPolicyRule
        fields = ('ttl',)
        labels = {
            'ttl': 'Time to live',
            }

    def clean_type(self):
        name = self.cleaned_data['type']
        return DataType.objects.get_or_create(name=name)[0]

    def save(self):
        rule = super(PrivacyPolicyForm, self).save(commit = False)
        rule.service = self.service
        rule.dataType = self.cleaned_data['type']
        rule.save()
        return rule

class PurposeForm(forms.ModelForm):
    goal = forms.CharField()

    def __init__(self, policy, *args, **kwargs):
        super(PurposeForm, self).__init__(*args, **kwargs)
        self.policy = policy
        try:
            self.fields['goal'].initial = self.instance.goal.name
        except:
            pass

    class Meta:
        model = Purpose
        fields = ('onlyFor',)
        labels = {
            'onlyFor': 'Type',
            }

    def clean_goal(self):
        name = self.cleaned_data['goal']
        goal = Goal.objects.get_or_create(name=name)[0]
        if self.policy.purpose.filter(goal=goal).exists():
            raise ValidationError(('already have this one'),)
        return goal

    def clean_onlyFor(self):
        choice = self.cleaned_data['onlyFor']
        if self.policy.purpose.filter().exists() and self.policy.purpose.all()[0].onlyFor != choice:
            raise ValidationError(('all rules for this datatype should only be all OF or all NF'),)
        return choice


    def save(self):
        rule = super(PurposeForm, self).save(commit = False)
        rule.goal = self.cleaned_data['goal']
        rule.save()
        self.policy.purpose.add(rule)
        self.policy.save()
        return rule

class ExpressionForm(forms.ModelForm):

    def __init__(self, element, target, *args, **kwargs):
        super(ExpressionForm, self).__init__(*args, **kwargs)
        self.element = element
        self.target = target

    class Meta:
        model = Expression

    def clean_variable(self):
        var = self.cleaned_data['variable']
        if self.target == 'user':
            if var in constraint.ConstraintChecker.RESERVED:
                raise ValidationError('%s is an environment variable, can not use it here' % var)
        else:
            if var not in constraint.ConstraintChecker.RESERVED:
                raise ValidationError('%s is not an environment variable, can not use it here' % var)
        return var


    def save(self):
        expr = super(ExpressionForm, self).save(commit = False)
        expr.save()
        if self.target == 'user':
            self.element.userRules.add(expr)
        else:
            self.element.environmentRules.add(expr)
        self.element.save()
        return expr


class ServiceRegisterForm(forms.ModelForm):
    repository = forms.ChoiceField()
    mandatory_input = TypeSetField()
    optional_input = TypeSetField(required=False)

    def __init__(self, *args, **kwargs):
        super(ServiceRegisterForm, self).__init__(*args, **kwargs)
        choices = map(lambda x: (x, str(x)), Repository.objects.all())
        self.fields['repository'].choices = choices
    class Meta:
        model = Service
        fields = ()

    def clean_repository(self):
        repository = Repository.objects.get(name=self.cleaned_data['repository'])
        if (repository.record_set.filter(service=self.instance)).exists():
            raise ValidationError("already registered on this repository")
        return repository

    def save(self):
        record = Record()
        record.service = self.instance
        record.repository = self.cleaned_data['repository']
        record.reputation = 0
        record.mandatory_input = self.cleaned_data['mandatory_input']
        record.optional_input = self.cleaned_data['optional_input']
        record.output = self.instance.output
        record.save()
        return record