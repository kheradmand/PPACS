from django          import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import Textarea
from Provider.models import Provider, Service, DataType, ServicePrivacyPolicyRule, Purpose, Goal, Expression, \
    TypeSet
import re


# cleaned data is a models.TypeSet object
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
        ret = []
        if len(splited) == 0:
            raise ValidationError(('set can not be empty'))
        for val in splited:
            striped = val.strip()
            if re.match('[a-zA-Z0-9_]\w*',striped) is None:
                raise ValidationError(('invalid type name: %(name)s'),
                                     params={'name': striped}
                )
            ret.append(striped)
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

    def save(self, service):
        set = self.cleaned_data['set']
        service.inputs.add(set)
        service.save()
        return set

class PrivacyPolicyForm(forms.ModelForm):
    dataType = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(PrivacyPolicyForm, self).__init__(*args, **kwargs)
        try:
            self.fields['dataType'].initial = self.instance.dataType.name
        except:
            pass

    class Meta:
        model = ServicePrivacyPolicyRule
        fields = ('ttl',)
        widgets = {'dataType': forms.TextInput,}
        labels = {
            'ttl': 'Time to live',
        }

    def clean_dataType(self):
        name = self.cleaned_data['dataType']
        return DataType.objects.get_or_create(name=name)[0]

    def save(self, service):
        rule = super(PrivacyPolicyForm, self).save(commit = False)
        rule.service = service
        rule.dataType = self.cleaned_data['dataType']
        rule.save()
        return rule

class PurposeForm(forms.ModelForm):
    goal = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(PurposeForm, self).__init__(*args, **kwargs)
        try:
            self.fields['goal'].initial = self.instance.goal.name
        except:
            pass

    class Meta:
        model = Purpose
        fields = ('onlyFor',)
        widgets = {'dataType': forms.TextInput,}
        labels = {
            'onlyFor': 'Type',
        }

    def clean_goal(self):
        name = self.cleaned_data['goal']
        return Goal.objects.get_or_create(name=name)[0]

    def save(self, policy):
        rule = super(PurposeForm, self).save(commit = False)
        rule.goal = self.cleaned_data['goal']
        rule.save()
        policy.purpose.add(rule)
        policy.save()
        return rule

class ExpressionForm(forms.ModelForm):
    class Meta:
        model = Expression
    def save(self, element, target):
        expr = super(ExpressionForm, self).save(commit = False)
        expr.save()
        if target == 'user':
            element.userRules.add(expr)
        else:
            element.environmentRules.add(expr)
        element.save()
        return expr