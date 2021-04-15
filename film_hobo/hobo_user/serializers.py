from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _

try:
    from allauth.account import app_settings as allauth_settings
    from allauth.utils import (email_address_exists,
                               get_username_max_length)
    from allauth.account.adapter import get_adapter
    from allauth.account.utils import setup_user_email
except ImportError:
    raise ImportError("allauth needs to be added to INSTALLED_APPS.")

from .adapters import CustomUserAccountAdapter
from .models import CustomUser, Country


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = ['id','name']


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=100,
        style={'placeholder': 'Email', 'autofocus': True}
    )
    password = serializers.CharField(
        max_length=100,
        style={'input_type': 'password', 'placeholder': 'Password'}
    )
    remember_me = serializers.BooleanField()


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email',]


# overide default registerserializer
class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=get_username_max_length(),
        min_length=allauth_settings.USERNAME_MIN_LENGTH,
        required=allauth_settings.USERNAME_REQUIRED
    )
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    first_name = serializers.CharField(
        max_length=150,
        required=True,
    )
    middle_name = serializers.CharField(
        max_length=150,
        allow_blank=True,
    )
    last_name = serializers.CharField(
        max_length=150,
        required=True,
    )

    class Meta:
        model = CustomUser
        fields = ['email','username','first_name','middle_name','last_name',
        'password1', 'password2']

    # def validate_first_name(self, first_name):
    #     return first_name

    # def validate_middle_name(self, middle_name):
    #     return middle_name

    # def validate_last_name(self, last_name):
    #     return last_name

    def validate_username(self, username):
        username = get_adapter().clean_username(username)
        return username

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(_(
                    "A user is already registered with this e-mail address."))
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)


    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(
                _("The two password fields didn't match."))
        return data

    def custom_signup(self, request, user):
        pass

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'middle_name': self.validated_data.get('middle_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
        }

    def save(self, request):
        adapter = CustomUserAccountAdapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


# overide default registerserializer
class RegisterIndieProSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=get_username_max_length(),
        min_length=allauth_settings.USERNAME_MIN_LENGTH,
        required=allauth_settings.USERNAME_REQUIRED
    )
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    first_name = serializers.CharField(
        max_length=150,
        required=True,
    )
    middle_name = serializers.CharField(
        max_length=150,
        allow_blank=True,
    )
    last_name = serializers.CharField(
        max_length=150,
        required=True,
    )
    phone_number = serializers.CharField(
        max_length=15,
    )
    date_of_birth = serializers.DateField(format="%Y-%m-%d")
    # country = CountrySerializer(read_only=True)
    membership = serializers.StringRelatedField()
    address = serializers.CharField()
    i_agree = serializers.BooleanField( required=True)

    class Meta:
        model = CustomUser
        fields = ['email','username','first_name','middle_name','last_name',
        'password1', 'password2', 'phone_number', 'address', 'date_of_birth',
        'membership','i_agree']

    # def validate_first_name(self, first_name):
    #     return first_name

    # def validate_middle_name(self, middle_name):
    #     return middle_name

    # def validate_last_name(self, last_name):
    #     return last_name

    def validate_username(self, username):
        username = get_adapter().clean_username(username)
        return username

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(_(
                    "A user is already registered with this e-mail address."))
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate_i_agree(self, i_agree):
        if i_agree != True:
            print("You must accept our terms and conditions!!")
            raise serializers.ValidationError(
                _("You must accept our terms and conditions!!"))
        return i_agree

    def validate_i_agree(self, i_agree):
        if i_agree != True:
            print("You must accept our terms and conditions!!")
            raise serializers.ValidationError(
                _("You must accept our terms and conditions!!"))
        return i_agree

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(
                _("The two password fields didn't match."))
        return data

    def custom_signup(self, request, user):
        pass

    def get_cleaned_data(self):
        print("country----: ",self.validated_data.get('country', ''))
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'middle_name': self.validated_data.get('middle_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'phone_number': self.validated_data.get('phone_number', ''),
            'address': self.validated_data.get('address', ''),
            'date_of_birth': self.validated_data.get('date_of_birth', ''),
            # 'country': self.validated_data.get('country', ''),
            'membership': self.validated_data.get('membership', ''),
            'i_agree': self.validated_data.get('i_agree', ''),
        }

    def save(self, request):
        adapter = CustomUserAccountAdapter()
        user = adapter.new_user(request)
        print("______self.get_cleaned_data()___: ",self.get_cleaned_data())
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user
