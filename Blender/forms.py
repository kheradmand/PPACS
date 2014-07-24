from django import forms
from Blender.models import Blenderrr


class BlenderForm(forms.ModelForm):
    class Meta:
        model = Blenderrr
