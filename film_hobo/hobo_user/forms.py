from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django_select2.forms import Select2Widget

from bootstrap_datepicker_plus import DateTimePickerInput
from phonenumber_field.formfields import PhoneNumberField

from .models import CustomUser, GuildMembership, DisabledAccount, \
    CustomUserSettings, AthleticSkill

from .models import GuildMembership, Country



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

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['password1'].required = True
        self.fields['password2'].required = True
        self.fields['first_name'].widget.attrs['class'] = 'inp-line'
        self.fields['first_name'].widget.attrs['placeholder'] = 'First'
        self.fields['middle_name'].widget.attrs['class'] = 'inp-line'
        self.fields['middle_name'].widget.attrs['placeholder'] = 'Middle'
        self.fields['last_name'].widget.attrs['class'] = 'inp-line'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last'
        self.fields['email'].widget.attrs['class'] = 'inp-line'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['password1'].widget.attrs['class'] = 'form-control form-control-input'
        self.fields['password2'].widget.attrs['class'] = 'form-control form-control-input'


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
        widgets = {
            'date_of_birth': DateTimePickerInput(format='%Y-%m-%d'),
        }

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
        self.fields['first_name'].widget.attrs['class'] = 'inp-line'
        self.fields['first_name'].widget.attrs['placeholder'] = 'First'
        self.fields['middle_name'].widget.attrs['class'] = 'inp-line'
        self.fields['middle_name'].widget.attrs['placeholder'] = 'Middle'
        self.fields['last_name'].widget.attrs['class'] = 'inp-line'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last'
        self.fields['email'].widget.attrs['class'] = 'inp-line'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['phone_number'].widget.attrs['class'] = 'inp-line'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Phone'
        self.fields['date_of_birth'].widget.attrs['class'] = 'inp-line'
        self.fields['date_of_birth'].widget.attrs['placeholder'] = 'Date of Birth'
        self.fields['country'].widget.attrs['class'] = 'form-control form-control-input'
        self.fields['password1'].widget.attrs['class'] = 'form-control form-control-input'
        self.fields['password2'].widget.attrs['class'] = 'form-control form-control-input'
        self.fields['address'].widget.attrs['class'] = 'inp-line'
        self.fields['address'].widget.attrs['placeholder'] = 'Address'


class SignUpProForm(UserCreationForm):
    i_agree = forms.BooleanField(widget=forms.CheckboxInput())
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

        widgets = {
            'date_of_birth': DateTimePickerInput(format='%Y-%m-%d'),
        }

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
        self.fields['first_name'].widget.attrs['class'] = 'inp-line'
        self.fields['first_name'].widget.attrs['placeholder'] = 'First'
        self.fields['middle_name'].widget.attrs['class'] = 'inp-line'
        self.fields['middle_name'].widget.attrs['placeholder'] = 'Middle'
        self.fields['last_name'].widget.attrs['class'] = 'inp-line'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last'
        self.fields['email'].widget.attrs['class'] = 'inp-line'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['phone_number'].widget.attrs['class'] = 'inp-line'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Phone'
        self.fields['date_of_birth'].widget.attrs['class'] = 'inp-line'
        self.fields['date_of_birth'].widget.attrs['placeholder'] = 'Date of Birth'
        self.fields['address'].widget.attrs['class'] = 'inp-line'
        self.fields['address'].widget.attrs['placeholder'] = 'Address'
        self.fields['country'].widget.attrs['class'] = 'form-control form-control-input'
        self.fields['password1'].widget.attrs['class'] = 'form-control form-control-input'
        self.fields['password2'].widget.attrs['class'] = 'form-control form-control-input'
        self.fields['guild_membership_id'].widget.attrs['class'] = 'custom_check_box '


class SignUpFormCompany(UserCreationForm):
    i_agree = forms.BooleanField(widget=forms.CheckboxInput())

    class Meta:
        model = CustomUser
        fields = ('first_name', 'middle_name', 'last_name', 'email',
                  'password1', 'password2', 'phone_number',
                  'address', 'i_agree', 'date_of_birth', 'country',
                  'title', 'company_name', 'company_address',
                  'company_phone', 'company_website')

        widgets = {
            'date_of_birth': DateTimePickerInput(format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super(SignUpFormCompany, self).__init__(*args, **kwargs)
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
        self.fields['company_name'].required = True
        self.fields['company_address'].required = True
        self.fields['company_phone'].required = True
        self.fields['title'].required = True
        self.fields['company_website'].required = False

        self.fields['first_name'].widget.attrs['class'] = 'inp-line'
        self.fields['first_name'].widget.attrs['placeholder'] = 'First'
        self.fields['middle_name'].widget.attrs['class'] = 'inp-line'
        self.fields['middle_name'].widget.attrs['placeholder'] = 'Middle'
        self.fields['last_name'].widget.attrs['class'] = 'inp-line'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last'
        self.fields['email'].widget.attrs['class'] = 'inp-line'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['phone_number'].widget.attrs['class'] = 'inp-line'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Phone'
        self.fields['date_of_birth'].widget.attrs['class'] = 'inp-line'
        self.fields['date_of_birth'].widget.attrs['placeholder'] = 'Date of Birth'
        self.fields['address'].widget.attrs['class'] = 'inp-line'
        self.fields['address'].widget.attrs['placeholder'] = 'Address'
        self.fields['title'].widget.attrs['class'] = 'inp-line'
        self.fields['title'].widget.attrs['placeholder'] = 'Your Title'

        self.fields['company_name'].widget.attrs['class'] = 'inp-line'
        self.fields['company_name'].widget.attrs['placeholder'] = 'Company Name'
        self.fields['company_address'].widget.attrs['class'] = 'inp-line'
        self.fields['company_address'].widget.attrs['placeholder'] = 'Address'
        self.fields['company_phone'].widget.attrs['class'] = 'inp-line'
        self.fields['company_phone'].widget.attrs['placeholder'] = 'Phone'
        self.fields['company_website'].widget.attrs['class'] = 'inp-line'
        self.fields['company_website'].widget.attrs['placeholder'] = 'Website'

        self.fields['country'].widget.attrs['class'] = 'form-control form-control-input'
        self.fields['password1'].widget.attrs['class'] = 'form-control form-control-input'
        self.fields['password2'].widget.attrs['class'] = 'form-control form-control-input'



# class SignUpFormCompany(forms.Form):
#     """
#     company details
#     """
#     company_name = forms.CharField(label="Company Name", max_length=150,
#                                    required=False, help_text='')
#     company_address = forms.CharField(label="Address", help_text="",
#                                       max_length=250,)
#     company_website = forms.URLField(label="Website")
#     company_phone = forms.CharField(label="Phone")
#     """
#     personal details
#     """
#     first_name = forms.CharField(max_length=150, required=True,
#                                  help_text='')
#     middle_name = forms.CharField(max_length=150, required=False,
#                                   help_text='')
#     last_name = forms.CharField(max_length=150, required=False,
#                                 help_text='')
#     user_title = forms.CharField(label="Your Title", max_length=150)
#     email = forms.EmailField(label="Email", max_length=254,
#                              help_text='Required. Inform a ' +
#                              'valid email address.')
#     phone_number = PhoneNumberField(label="Phone")
#     date_of_birth = forms.DateField(
#          widget=DateTimePickerInput(format='%m/%d/%Y')
#      )
#     user_address = forms.CharField(label="Address", help_text="",
#                                    max_length=250,)
#     country = forms.ModelChoiceField(
#         label="Country", queryset=Country.objects.all())
#     password1 = forms.CharField(label="Password", max_length=150)
#     password2 = forms.CharField(label="Repeat Password", max_length=150)

#     def __init__(self, *args, **kwargs):
#         super(SignUpFormCompany, self).__init__(*args, **kwargs)
#         self.fields['date_of_birth'].widget.attrs['class'] = 'inp-line'
#         self.fields['date_of_birth'].widget.attrs['placeholder'] = 'Date of Birth'
#         self.fields['company_address'].widget.attrs['class'] = 'inp-line'
#         self.fields['company_address'].widget.attrs['placeholder'] = 'Address'
#         self.fields['user_address'].widget.attrs['class'] = 'inp-line'
#         self.fields['user_address'].widget.attrs['placeholder'] = 'Address'



class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput())
    new_password1 = forms.CharField(widget=forms.PasswordInput())
    new_password2 = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs['class'] = 'inp-line'
        self.fields['old_password'].widget.attrs['placeholder'] = 'Old Password'
        self.fields['new_password1'].widget.attrs['class'] = 'inp-line'
        self.fields['new_password1'].widget.attrs['placeholder'] = 'New Password'
        self.fields['new_password2'].widget.attrs['class'] = 'inp-line'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Confirm New Password'


class ForgotPasswordEmailForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254,
                             help_text='Enter your email address.')


class ResetPasswordForm(forms.Form):
    new_password1 = forms.CharField(widget=forms.PasswordInput())
    new_password2 = forms.CharField(widget=forms.PasswordInput())


class PersonalDetailsForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ('gender', 'feet', 'inch', 'lbs', 'start_age',
                  'stop_age', 'physique', 'hair_color', 'hair_length',
                  'eyes')
