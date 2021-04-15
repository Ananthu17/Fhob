from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from bootstrap_datepicker_plus import DateTimePickerInput, DatePickerInput


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=False,
                                 help_text='')
    middle_name = forms.CharField(max_length=100, required=False,
                                  help_text='')
    last_name = forms.CharField(max_length=100, required=False,
                                help_text='')
    email = forms.EmailField(max_length=254,
                             help_text='Required. Inform a ' +
                             'valid email address.')
    i_agree = forms.BooleanField(required=True, widget=forms.CheckboxInput())

    class Meta:
        model = CustomUser
        fields = ('first_name', 'middle_name', 'last_name', 'email',
                  'password1', 'password2', 'i_agree')


class LoginForm(AuthenticationForm):

    class Meta:
        model = CustomUser
        fields = ('email', 'password1')


class SignUpIndieProForm(UserCreationForm):
    i_agree = forms.BooleanField(widget=forms.CheckboxInput())

    class Meta:
        model = CustomUser
        fields = ('first_name', 'middle_name', 'last_name', 'email',
                  'password1', 'password2', 'phone_number', 
                  'address','i_agree','date_of_birth', 'country')
        
        def __init__(self, *args, **kwargs):
            super(SignUpIndieProForm, self).__init__(*args, **kwargs)
            self.fields['date_of_birth'].widget.attrs['id'] = 'date_of_birth'
            self.fields['i_agree'].required = True

        widgets = {
                    'date_of_birth': DateTimePickerInput(format='%Y-%m-%d'),
                }


class SignUpFormCompany(forms.Form):
    company_name = forms.CharField(max_length=150, required=False,
                                   help_text='')
    comapny_address = forms.Textarea()
    comapny_website = forms.URLField()
    company_phone = forms.CharField()

    first_name = forms.CharField(max_length=150, required=True,
                                 help_text='')
    middle_name = forms.CharField(max_length=150, required=False,
                                  help_text='')
    last_name = forms.CharField(max_length=150, required=False,
                                help_text='')
    date_of_birth = forms.DateField()
    user_address = forms.Textarea()

