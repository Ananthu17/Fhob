from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from django.utils.translation import ugettext_lazy as _

try:
    from allauth.account import app_settings as allauth_settings
    from allauth.utils import (email_address_exists,
                               get_username_max_length)
    from allauth.account.adapter import get_adapter
    from allauth.account.utils import setup_user_email
except ImportError:
    raise ImportError("allauth needs to be added to INSTALLED_APPS.")

from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from rest_framework import exceptions
from rest_auth.serializers import PasswordResetSerializer
from .adapters import CustomUserAccountAdapter, CustomIndieProUserAdapter, \
                      CustomCompanyUserAccountAdapter
from .models import CustomUser, Country, GuildMembership, \
    IndiePaymentDetails, Photo, ProPaymentDetails, PromoCode, \
    DisabledAccount, CustomUserSettings, CompanyPaymentDetails, \
    EthnicAppearance, AthleticSkill, UserAgentManager, UserNotification, UserProfile, CoWorker, \
    UserRating, UserAgentManager, Photo, UserNotification
from authemail.models import SignupCode
from rest_framework.authtoken.models import Token

UserModel = get_user_model()


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = ['id', 'name']


class GuildMembershipSerializer(serializers.ModelSerializer):
    membership = serializers.CharField(required=True)

    class Meta:
        model = GuildMembership
        fields = ['id', 'membership', ]
        read_only_fields = ('pk', 'membership')


# class LoginSerializer(serializers.Serializer):
#     email = serializers.EmailField(
#         max_length=100,
#         style={'placeholder': 'Email', 'autofocus': True}
#     )
#     password = serializers.CharField(
#         max_length=100,
#         style={'input_type': 'password', 'placeholder': 'Password'}
#     )
#     remember_me = serializers.BooleanField()


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', ]


class RegisterSerializer(serializers.Serializer):
    """
    overide the rest-auth RegisterSerializer for hobo user registration
    """
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
        fields = ['email', 'username', 'first_name', 'middle_name',
                  'last_name', 'password1', 'password2']

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



class RegisterIndieSerializer(serializers.Serializer):
    """
    overide the rest-auth RegisterSerializer for indie/pro user registration
    """
    username = serializers.CharField(
        max_length=get_username_max_length(),
        min_length=allauth_settings.USERNAME_MIN_LENGTH,
        required=allauth_settings.USERNAME_REQUIRED
    )
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(
        max_length=150,
        required=True,
    )
    middle_name = serializers.CharField(
        max_length=150,
        allow_blank=True, required=False
    )
    last_name = serializers.CharField(
        max_length=150,
        required=True,
    )
    phone_number = serializers.CharField(
        max_length=15, required=True
    )
    date_of_birth = serializers.DateField(format="%Y-%m-%d", required=True)
    membership = serializers.StringRelatedField()
    address = serializers.CharField(required=True)
    country = serializers.CharField(required=True)
    i_agree = serializers.BooleanField(required=False)

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'first_name', 'middle_name',
                  'last_name', 'password1', 'password2', 'phone_number',
                  'address', 'date_of_birth', 'membership', 'i_agree',
                  'country']

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
            'country': self.validated_data.get('country', ''),
            'membership': self.validated_data.get('membership', ''),
            'i_agree': self.validated_data.get('i_agree', ''),
        }

    def save(self, request):
        adapter = CustomIndieProUserAdapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def authenticate(self, **kwargs):
        return authenticate(self.context['request'], **kwargs)

    def _validate_email(self, email, password):
        user = None

        if email and password:
            user = self.authenticate(email=email, password=password)
        else:
            msg = _('Must include "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username(self, username, password):
        user = None

        if username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _('Must include "username" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username_email(self, username, email, password):
        user = None

        if email and password:
            user = self.authenticate(email=email, password=password)
        elif username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _(
                'Must include "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')

        user = None

        if 'allauth' in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            # Authentication through email
            if app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.EMAIL:
                user = self._validate_email(email, password)

            # Authentication through username
            elif app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.USERNAME:
                user = self._validate_username(username, password)

            # Authentication through either username or email
            else:
                user = self._validate_username_email(username, email, password)

        else:
            # Authentication without using allauth
            if email:
                try:
                    username = UserModel.objects.get(
                        email__iexact=email).get_username()
                except UserModel.DoesNotExist:
                    pass

            if username:
                user = self._validate_username_email(username, '', password)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Unable to log in with provided credentials.')
            raise exceptions.ValidationError(msg)

        # If required, is the email verified?
        if 'rest_auth.registration' in settings.INSTALLED_APPS:
            from allauth.account import app_settings
            if app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY:
                email_address = user.emailaddress_set.get(email=user.email)
                if not email_address.verified:
                    raise serializers.ValidationError(
                        _('E-mail is not verified.'))

        attrs['user'] = user
        return attrs


# overide default registerserializer
class RegisterProSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=get_username_max_length(),
        min_length=allauth_settings.USERNAME_MIN_LENGTH,
        required=allauth_settings.USERNAME_REQUIRED
    )
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(
        max_length=150,
        required=True,
    )
    middle_name = serializers.CharField(
        max_length=150,
        allow_blank=True, required=False
    )
    last_name = serializers.CharField(
        max_length=150,
        required=True,
    )
    phone_number = serializers.CharField(
        max_length=15, required=True
    )

    date_of_birth = serializers.DateField(format="%Y-%m-%d", required=True)
    membership = serializers.StringRelatedField()
    address = serializers.CharField(required=True)
    country = serializers.CharField(required=True)
    i_agree = serializers.BooleanField(required=False)
    guild_membership_id = serializers.PrimaryKeyRelatedField(
        queryset=GuildMembership.objects.all(),
        write_only=True, many=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'first_name', 'middle_name',
                  'last_name', 'password1', 'password2', 'phone_number',
                  'address', 'date_of_birth', 'membership', 'i_agree',
                  'country', 'guild_membership_id']

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
            'country': self.validated_data.get('country', ''),
            'membership': self.validated_data.get('membership', ''),
            'i_agree': self.validated_data.get('i_agree', ''),
            'guild_membership_id': self.validated_data.get(
             'guild_membership_id', ''),
        }

    def save(self, request):
        adapter = CustomIndieProUserAdapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


class TokenSerializer(serializers.ModelSerializer):
    key = serializers.CharField(required=True)

    class Meta:
        model = Token
        fields = ['key', ]


class SignupCodeSerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=True)

    class Meta:
        model = SignupCode
        fields = ['code', ]


class RegisterCompanySerializer(serializers.ModelSerializer):
    """
    overide the rest-auth RegisterSerializer for hobo user registration
    """
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
    phone_number = PhoneNumberField()
    date_of_birth = serializers.DateField()
    address = serializers.CharField()
    country = serializers.CharField()
    company_type = serializers.CharField()

    # company details
    company_name = serializers.CharField()
    company_address = serializers.CharField()
    company_website = serializers.URLField(allow_blank=True)
    company_phone = PhoneNumberField()
    title = serializers.CharField()
    membership = serializers.ChoiceField(choices=CustomUser.MEMBERSHIP_CHOICES)

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'first_name', 'middle_name',
                  'last_name', 'password1', 'password2', 'phone_number',
                  'date_of_birth', 'address', 'country',
                  'company_name', 'company_address', 'company_website',
                  'company_phone', 'title', 'membership', 'company_type']

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

    def validate_phone_number(self, phone_number):
        try:
            match = CustomUser.objects.get(phone_number=phone_number)
            if match:
                raise serializers.ValidationError(_(
                    "A user is already registered with this phone number."))
        except CustomUser.DoesNotExist:
            return phone_number

    def validate_company_phone(self, company_phone):
        try:
            match = CustomUser.objects.get(company_phone=company_phone)
            if match:
                raise serializers.ValidationError(_(
                    "A company is already registered with this phone number."))
        except CustomUser.DoesNotExist:
            return company_phone

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
            'phone_number': self.validated_data.get('phone_number', ''),
            'date_of_birth': self.validated_data.get('date_of_birth', ''),
            'address': self.validated_data.get('address', ''),
            'country': self.validated_data.get('country', ''),
            'company_type': self.validated_data.get('company_type', ''),
            'company_name': self.validated_data.get('company_name', ''),
            'company_address': self.validated_data.get('company_address', ''),
            'company_website': self.validated_data.get('company_website', ''),
            'company_phone': self.validated_data.get('company_phone', ''),
            'title': self.validated_data.get('title', ''),
            'membership': self.validated_data.get('membership', ''),
        }

    def save(self, request):
        adapter = CustomCompanyUserAccountAdapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


class PaymentPlanSerializer(serializers.Serializer):
    payment_plan = serializers.CharField(required=False)
    email = serializers.CharField(required=True)


class IndiePaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = IndiePaymentDetails
        fields = ['free_days', 'annual_amount', 'annual_amount_with_tax',
                  'monthly_amount', 'monthly_amount_with_tax', 'estimated_tax']


class ProPaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProPaymentDetails
        fields = ['free_days', 'annual_amount', 'annual_amount_with_tax',
                  'monthly_amount', 'monthly_amount_with_tax', 'estimated_tax']


class CompanyPaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompanyPaymentDetails
        fields = ['free_days', 'annual_amount', 'annual_amount_with_tax',
                  'monthly_amount', 'monthly_amount_with_tax', 'estimated_tax']


class PromoCodeSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(required=True)
    class Meta:
        model = PromoCode
        fields = ['promo_code', 'created_time', 'valid_from', 'valid_to',
                  'life_span', 'amount_type', 'user_type','user_id']


class DisableAccountSerializer(serializers.ModelSerializer):
    reason = serializers.CharField(
        max_length=150,
        required=True,
    )

    class Meta:
        model = DisabledAccount
        fields = ['reason',]


class EnableAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUserSettings
        fields = ['account_status',]


class BlockMembersSerializer(serializers.Serializer):
    user_id = serializers.CharField(
        max_length=150,
        required=True,
    )


class SettingsSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(
        max_length=150,
        required=False,
    )
    middle_name = serializers.CharField(
        max_length=150,
        allow_blank=True, required=False
    )
    last_name = serializers.CharField(
        max_length=150,
        required=False,
    )

    profile_visibility = serializers.ChoiceField(
                         choices=CustomUserSettings.PROFILE_VISIBILITY_CHOICES,
                         required=False,)
    who_can_contact_me = serializers.ChoiceField(
                         choices=CustomUserSettings.CONTACT_CHOICES,
                         required=False,)
    who_can_track_me = serializers.ChoiceField(
                         choices=CustomUserSettings.TRACKING_CHOICES,
                         required=False,)
    someone_tracks_me = serializers.BooleanField(required=False)
    change_in_my_or_project_rating = serializers.BooleanField(required=False)
    review_for_my_work_or_project = serializers.BooleanField(required=False)
    new_project = serializers.BooleanField(required=False)
    friend_request = serializers.BooleanField(required=False)
    match_for_my_Interest = serializers.BooleanField(required=False)


class BlockedMembersQuerysetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name']


class PersonalDetailsSerializer(serializers.ModelSerializer):
    athletic_skills = serializers.ListField()
    lbs = serializers.IntegerField(allow_null=True)
    start_age = serializers.IntegerField(allow_null=True)
    stop_age = serializers.IntegerField(allow_null=True)

    class Meta:
        model = CustomUser
        fields = ['gender', 'feet', 'inch', 'lbs', 'start_age',
                  'stop_age', 'physique', 'hair_color', 'hair_length',
                  'eyes', 'athletic_skills', 'ethnic_appearance']

    def get_validation_exclusions(self, instance=None):
        exclusions = super(PersonalDetailsSerializer,
                           self).get_validation_exclusions(instance)
        return exclusions + ['lbs', 'start_age', 'stop_age']


class PasswordResetSerializer(PasswordResetSerializer):

    def get_email_options(self):
        return {
                'subject_template_name': 'registration/password_reset_subject.txt',
                'html_email_template_name': 'registration/'
                                        'password_reset_email.html',
        }


class UserProfileSerializer(serializers.ModelSerializer):
    job_types = serializers.ListField(required=False)
    membership = serializers.CharField(read_only=True)
    first_name = serializers.CharField(
        max_length=150,
        required=True,
    )
    middle_name = serializers.CharField(
        max_length=150,
        allow_blank=True, required=False
    )
    last_name = serializers.CharField(
        max_length=150,
        required=True,
    )
    guild_membership = serializers.ListField(required=False)

    class Meta:
        model = UserProfile
        fields = ['first_name', 'middle_name', 'last_name', 'job_types',
                  'company', 'company_position', 'guild_membership',
                  'company_website', 'imdb', 'bio',
                  'membership']


class CoWorkerSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=150,
        required=False, allow_blank=True
    )
    user = serializers.CharField(
        max_length=150,
        required=False, allow_blank=True
    )
    position = serializers.CharField(
        max_length=150,
        required=True,
    )
    id = serializers.CharField(
        max_length=150,
        required=False,
    )

    class Meta:
        model = CoWorker
        fields = ['id', 'user', 'name', 'position']


class RemoveCoWorkerSerializer(serializers.Serializer):
    id = serializers.ListField(required=False)


class RemoveAgentManagerSerializer(serializers.Serializer):
    id = serializers.ListField(required=False)


class TrackUserSerializer(serializers.Serializer):
    track_id =  serializers.CharField(
        max_length=150,
        required=True,
    )


class RateUserSkillsSerializer(serializers.ModelSerializer):
    user = serializers.CharField(
        max_length=150,
        required=True,
    )
    job_type = serializers.CharField(
        max_length=150,
        required=True,
    )
    rating = serializers.CharField(
        max_length=150,
        required=True,
    )

    class Meta:
        model = UserRating
        fields = ['user', 'job_type', 'rating']


class AgentManagerSerializer(serializers.ModelSerializer):
    agent_type = serializers.CharField(
        max_length=150,
        required=True,
    )
    agent_name = serializers.CharField(
        max_length=150,
        required=True,
    )
    agent_phone = PhoneNumberField(
        required=True,
    )
    agent_job_type = serializers.CharField(
        max_length=150,
        required=True,
    )
    agent_email = serializers.EmailField(
        required=False, allow_blank=True
    )
    id = serializers.CharField(
        required=False,
        max_length=150
    )

    class Meta:
        model = UserAgentManager
        fields = ['id', 'agent_type', 'agent_name', 'agent_phone',
                  'agent_email', 'agent_job_type']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name']


class GetSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUserSettings
        exclude = []


class PhotoSerializer(serializers.Serializer):
    id = serializers.CharField(
        max_length=150,
        required=True,
    )
    position = serializers.CharField(
        max_length=150,
        required=True,
    )
    class Meta:
        model = Photo
        exclude = ['id', 'position']


class UploadPhotoSerializer(serializers.Serializer):
    file = serializers.ImageField(required=True)
    position = serializers.CharField(
        max_length=150,
        required=True,
    )


class UserNotificationSerializer(serializers.ModelSerializer):
    # unread_count = serializers.CharField(
    #     max_length=150,
    #     required=True,
    # )
    user = serializers.StringRelatedField()
    from_user = serializers.StringRelatedField()

    class Meta:
        model = UserNotification
        exclude = []


class ChangeNotificationStatusSerializer(serializers.ModelSerializer):
    id = serializers.CharField(
        max_length=150,
        required=True,
    )
    class Meta:
        model = UserNotification
        fields = ['id', 'status_type']
