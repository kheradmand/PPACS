from django import forms
from Repository.models import Repository


class RepositoryForm(forms.ModelForm):
    class Meta:
        model = Repository