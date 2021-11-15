from django.contrib import admin
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from import_export.admin import ImportExportModelAdmin

from .models import Help, EmailUs, ReportProblem

from .importexport import HelpResource, EmailUsResource, \
                          ReportProblemResource, TokenResource, \
                          EmailChangeCodeResource, PasswordResetCodeResource, \
                          SignupCodeResource, GroupResource, \
                          PayPalIPNResource, SiteResource, \
                          SocialAccountResource, SocialTokenResource, \
                          SocialAppResource
from rest_framework.authtoken.models import Token
from authemail.models import EmailChangeCode, PasswordResetCode, SignupCode
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
# from paypal.standard.ipn.models import PayPalIPN
# Register your models here.


admin.site.unregister(EmailAddress)


@admin.register(EmailAddress)
class EmailAddressAdmin(ImportExportModelAdmin):
    list_display = ("email", "user", "primary", "verified")
    list_filter = ("primary", "verified")
    search_fields = []
    raw_id_fields = ("user",)
    actions = ["make_verified"]

    def get_search_fields(self, request):
        base_fields = get_adapter(request).get_user_search_fields()
        return ["email"] + list(map(lambda a: "user__" + a, base_fields))

    def make_verified(self, request, queryset):
        queryset.update(verified=True)

    make_verified.short_description = \
        "Mark selected email addresses as verified"


admin.site.unregister(Token)


@admin.register(Token)
class TokenAdmin(ImportExportModelAdmin):
    resource_class = TokenResource


admin.site.unregister(EmailChangeCode)


@admin.register(EmailChangeCode)
class EmailChangeCodeAdmin(ImportExportModelAdmin):
    resource_class = EmailChangeCodeResource


admin.site.unregister(PasswordResetCode)


@admin.register(PasswordResetCode)
class PasswordResetCodeAdmin(ImportExportModelAdmin):
    resource_class = PasswordResetCodeResource


admin.site.unregister(SignupCode)


@admin.register(SignupCode)
class SignupCodeAdmin(ImportExportModelAdmin):
    resource_class = SignupCodeResource


admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(ImportExportModelAdmin):
    resource_class = GroupResource


# admin.site.unregister(PayPalIPN)


# @admin.register(PayPalIPN)
# class PayPalIPNAdmin(ImportExportModelAdmin):
#     resource_class = PayPalIPNResource


admin.site.unregister(Site)


@admin.register(Site)
class SiteAdmin(ImportExportModelAdmin):
    resource_class = SiteResource


admin.site.unregister(SocialAccount)


@admin.register(SocialAccount)
class SocialAccountAdmin(ImportExportModelAdmin):
    resource_class = SocialAccountResource


admin.site.unregister(SocialToken)


@admin.register(SocialToken)
class SocialTokenAdmin(ImportExportModelAdmin):
    resource_class = SocialTokenResource


admin.site.unregister(SocialApp)


@admin.register(SocialApp)
class SocialAppAdmin(ImportExportModelAdmin):
    resource_class = SocialAppResource


@admin.register(Help)
class HelpAdmin(ImportExportModelAdmin):
    resource_class = HelpResource


@admin.register(EmailUs)
class EmailUsAdmin(ImportExportModelAdmin):
    resource_class = EmailUsResource


@admin.register(ReportProblem)
class ReportProblemAdmin(ImportExportModelAdmin):
    resource_class = ReportProblemResource


# admin.site.register(Help)
# admin.site.register(EmailUs)
# admin.site.register(ReportProblem)
