from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.forms import CheckboxSelectMultiple
from import_export.admin import ImportExportModelAdmin

from .models import CustomUser, Project, ProjectReaction, EthnicAppearance, \
                    AthleticSkill, PromoCode, Team, UserInterest, \
                    AthleticSkillInline, Country, IndiePaymentDetails, \
                    ProPaymentDetails, GuildMembership, \
                    CompanyPaymentDetails, DisabledAccount, \
                    CustomUserSettings, HoboPaymentsDetails, JobType, \
                    UserProfile, CoWorker, FriendRequest, UserTacking, \
                    UserRatingCombined, UserRating, UserAgentManager, \
                    Photo, UserNotification, CompanyProfile, \
                    Location, CompanyClient, NewJobType, Friend, FriendGroup, \
                    GroupUsers, Feedback, CompanyRating, CompanyRatingCombined, \
                    VideoRating,Video, ProjectMemberRating

from .importexport import EthnicAppearanceResource, AthleticSkillResource, \
                    CountryResource, GuildMembershipResource, \
                    JobTypeResource, LocationResource


# class EthnicAppearanceInlineInline(admin.StackedInline):
#     model = EthnicAppearanceInline
#     insert_after = 'eyes'


class AthleticSkillInlineInline(admin.StackedInline):
    model = AthleticSkillInline


class CustomUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_plan'].required = False
        self.fields['date_of_birth'].required = False
        self.fields['phone_number'].required = False
        self.fields['address'].required = False
        self.fields['country'].required = False
        self.fields['company_phone'].required = False
        self.fields['ethnic_appearance'].required = False

    class Meta:
        model = CustomUser
        fields = '__all__'


class CustomUserAdmin(UserAdmin, admin.ModelAdmin):
    form = CustomUserForm
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        ('User', {'fields': ('first_name', 'middle_name', 'last_name',
                             'email', 'password', 'date_of_joining')}),
        ('Terms and Conditions', {'fields': ('i_agree',)}),
        ('Registration Process', {'fields': ('registration_complete',)}),
        ('Membership', {'fields': ('membership', 'guild_membership',
                                   'payment_plan')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        ('Personal Details', {'fields': ('gender', 'date_of_birth',
                              'phone_number', 'address', 'country')}),
        ('Company Details', {'fields': ('company_name', 'title',
                                        'company_address', 'company_website',
                                        'company_phone', 'company_type',
                                        'agency_management_type')}),
        ('Height', {'fields': ('feet', 'inch')}),
        ('Weight', {'fields': ('lbs',)}),
        ('Age-Playing Range', {'fields': ('start_age', 'stop_age')}),
        ('Build', {'fields': ('physique', 'hair_color', 'hair_length',
                              'ethnic_appearance', 'eyes')})
    )
    # adding personal details inline
    inlines = [
        AthleticSkillInlineInline
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


admin.site.site_header = "Filmhobo Admin"
admin.site.site_title = "Filmhobo Admin Portal"
admin.site.index_title = "Welcome to Filmhobo Admin Portal"
admin.site.unregister(CustomUser)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Project)
admin.site.register(ProjectReaction)
admin.site.register(PromoCode)
admin.site.register(HoboPaymentsDetails)
admin.site.register(IndiePaymentDetails)
admin.site.register(ProPaymentDetails)
admin.site.register(CompanyPaymentDetails)
admin.site.register(DisabledAccount)
admin.site.register(CoWorker)
admin.site.register(Video)
admin.site.register(VideoRating)
admin.site.register(FriendRequest)
admin.site.register(UserAgentManager)
admin.site.register(Photo)
admin.site.register(UserInterest)
admin.site.register(CompanyClient)
admin.site.register(NewJobType)
admin.site.register(FriendGroup)
admin.site.register(CompanyRating)
admin.site.register(CompanyRatingCombined)


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


@admin.register(JobType)
class JobTypeAdmin(ImportExportModelAdmin):
    resource_class = JobTypeResource


@admin.register(Location)
class LocationAdmin(ImportExportModelAdmin):
    resource_class = LocationResource


class CustomUserSettingsAdmin(admin.ModelAdmin):
    model = CustomUserSettings
    fieldsets = (
        ('General', {'fields': ('user', 'profile_visibility',
                                'who_can_track_me', 'who_can_contact_me',
                                'account_status')}),
        ('Blocked Members', {'fields': ('blocked_members',)}),
        ('Profile', {'fields': ('hide_ratings',)}),
        ('Notification', {'fields': ('someone_tracks_me',
                                     'change_in_my_or_project_rating',
                                     'review_for_my_work_or_project',
                                     'new_project',
                                     'friend_request',
                                     'match_for_my_Interest',
                                     )}),
    )


admin.site.register(CustomUserSettings, CustomUserSettingsAdmin)


class UserTackingAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }


admin.site.register(UserTacking, UserTackingAdmin)


class FriendAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }


admin.site.register(Friend, FriendAdmin)


class GroupUsersAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }


admin.site.register(GroupUsers, GroupUsersAdmin)
admin.site.register(Feedback)


class UserProfileAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }


admin.site.register(UserProfile, UserProfileAdmin)


class CompanyProfileAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }


admin.site.register(CompanyProfile, CompanyProfileAdmin)


class ProjectMemberRatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_type', 'project', 'rating')


admin.site.register(ProjectMemberRating, ProjectMemberRatingAdmin)


class UserRatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_type', 'project', 'rating', 'rated_by')


admin.site.register(UserRating, UserRatingAdmin)


class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'from_user', 'status_type', 'message', 'created_time')


admin.site.register(UserNotification, UserNotificationAdmin)


class UserRatingCombinedAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_type', 'rating')


admin.site.register(UserRatingCombined, UserRatingCombinedAdmin)


class TeamAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'job_type')


admin.site.register(Team, TeamAdmin)
