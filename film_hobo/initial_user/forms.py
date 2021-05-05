from django import forms
from django.forms import ModelMultipleChoiceField
from django.utils.translation import ugettext_lazy as _

from .models import Designation, InitialIntrestedUsers


class MyMultipleModelChoiceField(ModelMultipleChoiceField):

    def label_from_instance(self, obj):
        return obj


class InitialUserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100,
                                 help_text='')
    middle_name = forms.CharField(max_length=100, required=False,
                                  help_text='')
    last_name = forms.CharField(max_length=100,
                                help_text='')
    email = forms.EmailField(max_length=254,
                             help_text='')
    phone = forms.CharField(max_length=20,
                            help_text='')
    phone.error_messages['invalid'] = _(
        'Please enter a valid US contact number')
    designation = forms.ModelMultipleChoiceField(
        label="Are you",
        queryset=Designation.objects.all(),
        widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = InitialIntrestedUsers
        fields = ('first_name', 'middle_name', 'last_name', 'email',
                  'phone', 'designation')
