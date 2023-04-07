from django import forms

from .models import Assembly


class AssemblyTitleForm(forms.ModelForm):
    class Meta:
        model = Assembly
        fields = ['name', 'description_short']
