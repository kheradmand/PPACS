from CodeWarrior.CodeWarrior_suite import target
from django          import forms
from Provider.models import Provider, Service, DataType, ServicePrivacyPolicyRule, Purpose, Goal, Expression

class ServiceForm(forms.ModelForm):
    output = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        try:
            self.fields['output'].initial = self.instance.output.name
        except:
            pass

    class Meta:
        model = Service
        exclude = ('provider', 'output')
        widgets = {'output': forms.TextInput,}

    def clean_output(self):
        output_name = self.cleaned_data['output']
        return DataType.objects.get_or_create(name=output_name)[0]

    def save(self, provider):
        service = super(ServiceForm, self).save(commit = False)
        service.provider = provider
        service.output = self.cleaned_data['output']
        service.save()

        
class ProviderForm(forms.ModelForm):
    class Meta:
        model = Provider

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
            'onlyFor': 'Only For ?',
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