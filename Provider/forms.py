from django          import forms
from Provider.models import Provider, Service, DataType, ServicePrivacyPolicyRule, Purpose, Goal, Expression, \
    TypeSet


class ServiceForm(forms.ModelForm):
    output = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        try:
            self.fields['output'].initial = self.instance.output
        except:
            self.fields['output'].initial = '{}'

    class Meta:
        model = Service
        fields = ('name', 'function')
        widgets = {'output': forms.TextInput,}

    # def clean_output(self):
    #     output = self.cleaned_data['output']
    #     return TypeList.objects.get_or_create(list=output)[0]

    def clean_output(self):
        output = self.cleaned_data['output']
        output = output[1:-1]
        print ("output is now "+output)
        set = TypeSet()
        for type in output.split(', '):
            print("adding "+type)
            set.types.add(DataType.objects().get_or_create(name=type))
            print("done")
        set.save()
        print("hehe")
        return set

    def save(self, provider):
        service = super(ServiceForm, self).save(commit = False)
        service.provider = provider
        #service.output = TypeList.objects.get_or_create(list=self.cleaned_data['output'])[0]
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

class TypeSetForm(forms.Form):
    set = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(TypeSetForm, self).__init__(*args, **kwargs)
        try:
            self.fields['set'].initial = '{}'
        except:
            pass

    def clean_set(self):
        set_str = self.cleaned_data['set']
        set_str = set_str[1:-1]
        print ("set_Str is now "+set_str)
        set = TypeSet()
        for type in set_str.split(', '):
            print("adding "+type)
            set.types.add(DataType.objects().get_or_create(name=type))
        set.save()
        return set

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