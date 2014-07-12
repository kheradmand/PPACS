from django          import forms
from Provider.models import Provider, Service, DataType

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