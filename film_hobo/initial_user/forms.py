from django import forms
from .models import Designation, InitialIntrestedUsers


class InitialUserForm(forms.Form):
    first_name = forms.CharField(max_length=100,
                                 help_text='')
    middle_name = forms.CharField(max_length=100, required=False,
                                  help_text='')
    last_name = forms.CharField(max_length=100,
                                help_text='')
    email = forms.EmailField(max_length=254,
                             help_text='')
    phone = forms.CharField(max_length=50)
    designation_id = forms.ModelMultipleChoiceField(
        queryset=Designation.objects.all(),
        widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = InitialIntrestedUsers
        fields = ('first_name', 'middle_name', 'last_name', 'email',
                  'phone', 'designation_id')
