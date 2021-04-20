from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from import_export.admin import ImportExportModelAdmin

from .models import CustomUser, Project, ProjectReaction, EthnicAppearance, \
                    EthnicAppearanceInline, AthleticSkill, \
                    AthleticSkillInline, PromoCode, Team, Actor, Writer, \
                    Producer, Director, Editor, Makeup, Country, \
                    IndiePaymentDetails, ProPaymentDetails, GuildMembership, \
                    CompanyPaymentDetails

from .importexport import EthnicAppearanceResource, AthleticSkillResource, \
                    CountryResource, GuildMembershipResource


class EthnicAppearanceInlineInline(admin.StackedInline):
    model = EthnicAppearanceInline
    insert_after = 'eyes'


class AthleticSkillInlineInline(admin.StackedInline):
    model = AthleticSkillInline


class CustomUserAdmin(UserAdmin, admin.ModelAdmin):
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        ('User', {'fields': ('first_name', 'middle_name', 'last_name',
                             'email', 'password')}),
        ('Terms and Conditions', {'fields': ('i_agree',)}),
        ('Membership', {'fields': ('membership', 'guild_membership',
                                   'payment_plan')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        ('Personal Details', {'fields': ('gender', 'date_of_birth',
         'phone_number', 'address', 'country')}),
        ('Height', {'fields': ('feet', 'inch')}),
        ('Weight', {'fields': ('lbs',)}),
        ('Age-Playing Range', {'fields': ('start_age', 'stop_age')}),
        ('Build', {'fields': ('physique', 'hair_color', 'hair_length',
                              'eyes',)})
    )
    # adding personal details inline
    inlines = [
        EthnicAppearanceInlineInline, AthleticSkillInlineInline
    ]
    change_form_template = 'admin/custom/change_form.html'

    class Media:
        css = {
            'all': (
                'css/admin.css',
            )
        }

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2',
                       'is_staff', 'is_active')}
         ),
    )

    # overide django admin save model
    def save_model(self, request, obj, form, change):
        obj.username = obj.email
        super().save_model(request, obj, form, change)


admin.site.site_header = "Film Hobo Admin"
admin.site.site_title = "Film Hobo Admin Portal"
admin.site.index_title = "Welcome to Film Hobo Admin Portal"
admin.site.unregister(CustomUser)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Project)
admin.site.register(ProjectReaction)
admin.site.register(PromoCode)
admin.site.register(Team)
admin.site.register(Actor)
admin.site.register(Writer)
admin.site.register(Producer)
admin.site.register(Director)
admin.site.register(Editor)
admin.site.register(Makeup)
admin.site.register(IndiePaymentDetails)
admin.site.register(ProPaymentDetails)
admin.site.register(CompanyPaymentDetails)


@admin.register(EthnicAppearance)
class EthnicAppearanceAdmin(ImportExportModelAdmin):
    resource_class = EthnicAppearanceResource


@admin.register(AthleticSkill)
class AthleticSkillAdmin(ImportExportModelAdmin):
    resource_class = AthleticSkillResource


@admin.register(Country)
class CountryAdmin(ImportExportModelAdmin):
    resource_class = CountryResource


@admin.register(GuildMembership)
class GuildMembershipAdmin(ImportExportModelAdmin):
    resource_class = GuildMembershipResource
