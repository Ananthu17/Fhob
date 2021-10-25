
from import_export.resources import ModelResource

from .models import Help, EmailUs, ReportProblem
from rest_framework.authtoken.models import Token
from authemail.models import EmailChangeCode, PasswordResetCode, SignupCode
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from paypal.standard.ipn.models import PayPalIPN


class HelpResource(ModelResource):

    class Meta:
        model = Help


class EmailUsResource(ModelResource):

    class Meta:
        model = EmailUs


class ReportProblemResource(ModelResource):

    class Meta:
        model = ReportProblem


class TokenResource(ModelResource):

    class Meta:
        model = Token


class EmailChangeCodeResource(ModelResource):

    class Meta:
        model = EmailChangeCode


class PasswordResetCodeResource(ModelResource):

    class Meta:
        model = PasswordResetCode


class SignupCodeResource(ModelResource):

    class Meta:
        model = SignupCode


class GroupResource(ModelResource):

    class Meta:
        model = Group


class PayPalIPNResource(ModelResource):

    class Meta:
        model = PayPalIPN


class SiteResource(ModelResource):

    class Meta:
        model = Site


class SocialAccountResource(ModelResource):

    class Meta:
        model = SocialAccount


class SocialTokenResource(ModelResource):

    class Meta:
        model = SocialToken


class SocialAppResource(ModelResource):

    class Meta:
        model = SocialApp
