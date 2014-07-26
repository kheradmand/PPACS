


# cleaned data is a models.TypeSet object
from sets import Set
from django import forms
from django.core.exceptions import ValidationError
from Client.models import Request, Assignment, UserPrivacyPrefRule, UserPrivacyPolicyRule
from Provider.forms import TypeSetField, PurposeForm
from Provider.models import DataType, Purpose, Goal


class RequestForm(forms.ModelForm):
    output = TypeSetField()

    def __init__(self, *args, **kwargs):
        super(RequestForm, self).__init__(*args, **kwargs)
        try:
            self.fields['output'].initial = self.instance.output
        except:
            pass

    class Meta:
        model = Request
        fields = ('key', 'certificate', 'blender')
        labels = {
            'certificate': 'Certificate URL'
        }

    def save(self):
        request = super(RequestForm, self).save(commit = False)
        request.output = self.cleaned_data['output']
        request.save()
        return request


class ClientInputForm(forms.ModelForm):

    def __init__(self, request, *args, **kwargs):
        super(ClientInputForm, self).__init__(*args, **kwargs)
        self.request = request

    class Meta:
        model = Assignment
        exclude = ('request',)

    def clean_variable(self):
        variable = self.cleaned_data['variable']
        if Assignment.objects.filter(variable=variable, request=self.request).exists():
            raise ValidationError(('already have this one'),)
        return variable


    def save(self):
        assignment = super(ClientInputForm, self).save(commit = False)
        assignment.request = self.request
        assignment.save()
        return assignment




class PrivacyForm(forms.ModelForm):
    type = forms.ChoiceField()

    def eligible_choice_set(self):
        unq = Set()
        return unq

    def __init__(self, request, *args, **kwargs):
        super(PrivacyForm, self).__init__(*args, **kwargs)
        self.request = request

        unq = self.eligible_choice_set()


        choices = []

        for type in unq:
            choices.append((type, type))
        print(choices)
        self.fields['type'].choices = choices
        try:
            self.fields['type'].initial = self.instance.dataType.name
        except:
            pass

    class Meta:
        model = UserPrivacyPrefRule
        fields = ('sensitivity',)

    def clean_type(self):
        name = self.cleaned_data['type']
        return DataType.objects.get_or_create(name=name)[0]

    def save(self, request):
        rule = super(PrivacyForm, self).save(commit = False)
        rule.request = request
        rule.dataType = self.cleaned_data['type']
        rule.save()
        return rule


class PrivacyPrefForm(PrivacyForm):
    def eligible_choice_set(self):
        unq = Set()
        for input in self.request.assignment_set.all():
            unq.add(input.variable)
        #removing the ones that are currently added
        for rule in self.request.userprivacyprefrule_set.all():
            unq.remove(rule.dataType.name)
        return unq

class PrivacyPurpForm(PrivacyForm):
    def eligible_choice_set(self):
        unq = Set()
        for type in self.request.output.types.all():
            unq.add(type.name)
        #removing the ones that are currently added
        for rule in self.request.userprivacypolicyrule_set.all():
            unq.remove(rule.dataType.name)
        return unq
    class Meta:
        model = UserPrivacyPolicyRule
        fields = ()
