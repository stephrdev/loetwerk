from .models import BuildNode
from django import forms

class WorkerForm(forms.ModelForm):
    class Meta:
        model = BuildNode