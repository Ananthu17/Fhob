from django import forms
from .models import Help


class HelpForm(forms.ModelForm):
    class Meta:
        model = Help
        fields = ('subject', 'description', 'screenshot')