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

    class Meta:
        model = CustomUser
        fields = ('first_name', 'middle_name', 'last_name', 'email',
                  'password1', 'password2', 'phone_number', 
                  'date_of_birth', 'address', 'country')
        
        def __init__(self, *args, **kwargs):
            super(SignUpIndieProForm, self).__init__(*args, **kwargs)
            self.fields['date_of_birth'].widget.attrs['id'] = 'date_of_birth'

        widgets = {
                    'date_of_birth': DateTimePickerInput(format='%Y-%m-%d'),
                }

