from django import forms
from Blender.models import Blenderrr


class BlenderForm(forms.ModelForm):
    class Meta:
        model = Blenderrr
        labels = {
            'wh' : "High sensitivity data weight",
            'wm' : "Medium sensitivity data weight",
            'wl' : "Low sensitivity data weight",
            'repos': "Repositories",
        }
