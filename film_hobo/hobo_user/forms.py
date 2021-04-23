from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from bootstrap_datepicker_plus import DateTimePickerInput
from phonenumber_field.formfields import PhoneNumberField


from .models import CustomUser, GuildMembership
from django.contrib.auth.forms import PasswordChangeForm

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


class SignUpIndieForm(UserCreationForm):
    i_agree = forms.BooleanField(widget=forms.CheckboxInput())

    class Meta:
        model = CustomUser
        fields = ('first_name', 'middle_name', 'last_name', 'email',
                  'password1', 'password2', 'phone_number',
                  'address', 'i_agree', 'date_of_birth', 'country')

        def __init__(self, *args, **kwargs):
            super(SignUpIndieForm, self).__init__(*args, **kwargs)
            self.fields['date_of_birth'].widget.attrs['id'] = 'date_of_birth'
            self.fields['i_agree'].required = True
            self.fields['first_name'].required = True
            self.fields['last_name'].required = True
            self.fields['email'].required = True
            self.fields['password1'].required = True
            self.fields['password2'].required = True
            self.fields['phone_number'].required = True
            self.fields['address'].required = True
            self.fields['date_of_birth'].required = True
            self.fields['country'].required = True

        widgets = {
                    'date_of_birth': DateTimePickerInput(format='%Y-%m-%d'),
                }


class SignUpProForm(UserCreationForm):
    i_agree = forms.BooleanField(widget=forms.CheckboxInput())
    # guild_membership = forms.ModelMultipleChoiceField(
    #         queryset=GuildMembership.objects.all(),
    #         widget=forms.CheckboxSelectMultiple,
    #         required=False)
    guild_membership_id = forms.ModelMultipleChoiceField(
        label="Guild Membership",
        queryset=GuildMembership.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'middle_name', 'last_name', 'email',
                  'password1', 'password2', 'phone_number',
                  'address', 'i_agree', 'date_of_birth', 'country',
                  'guild_membership_id')

        def __init__(self, *args, **kwargs):
            super(SignUpProForm, self).__init__(*args, **kwargs)
            self.fields['date_of_birth'].widget.attrs['id'] = 'date_of_birth'
            self.fields['i_agree'].required = True
            self.fields['first_name'].required = True
            self.fields['last_name'].required = True
            self.fields['email'].required = True
            self.fields['password1'].required = True
            self.fields['password2'].required = True
            self.fields['phone_number'].required = True
            self.fields['address'].required = True
            self.fields['date_of_birth'].required = True
            self.fields['country'].required = True

        widgets = {
                    'date_of_birth': DateTimePickerInput(format='%Y-%m-%d'),
                }


class SignUpFormCompany(forms.Form):
    """
    company details
    """
    company_name = forms.CharField(label="Company Name", max_length=150,
                                   required=False, help_text='')
    company_address = forms.CharField(label="Address", help_text="",
                                      widget=forms.Textarea())
    company_website = forms.URLField(label="Website")
    company_phone = forms.CharField(label="Phone")
    """
    personal details
    """
    first_name = forms.CharField(max_length=150, required=True,
                                 help_text='')
    middle_name = forms.CharField(max_length=150, required=False,
                                  help_text='')
    last_name = forms.CharField(max_length=150, required=False,
                                help_text='')
    user_title = forms.CharField(label="Your Title", max_length=150)
    email = forms.EmailField(label="Email", max_length=254,
                             help_text='Required. Inform a ' +
                             'valid email address.')
    phone_number = PhoneNumberField(label="Phone")
    date_of_birth = forms.DateField(
         widget=DateTimePickerInput(format='%m/%d/%Y')
     )
    user_address = forms.CharField(label="Address", help_text="",
                                   widget=forms.Textarea())
    country = forms.ChoiceField(label="Country")
    password1 = forms.CharField(label="Password", max_length=150)
    password2 = forms.CharField(label="Repeat Password", max_length=150)


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput())
    new_password1 = forms.CharField(widget=forms.PasswordInput())
    new_password2 = forms.CharField(widget=forms.PasswordInput())

