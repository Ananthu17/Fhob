from django import forms
from django.contrib import admin
from django.contrib.admin.actions import delete_selected \
    as django_delete_selected
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
                    UserProfile, CoWorker, FriendRequest, UserTracking, \
                    UserRatingCombined, UserRating, UserAgentManager, \
                    Photo, UserNotification, CompanyProfile, \
                    Location, CompanyClient, NewJobType, Friend, FriendGroup, \
                    VideoRatingCombined, CompanyRatingCombined, \
                    UserProject, GroupUsers, Feedback, CompanyRating, \
                    VideoRating, ProjectMemberRating, BetaTesterCodes


from .importexport import EthnicAppearanceResource, AthleticSkillResource, \
                    CountryResource, GuildMembershipResource, \
                    JobTypeResource, LocationResource, CustomUserResource, \
                    BetaTesterCodesResource, CompanyClientResource, \
                    CompanyPaymentDetailsResource, \
                    CompanyRatingCombinedResource, CompanyRatingResource, \
                    CoWorkerResource, CustomUserSettingsResource, \
                    DisabledAccountResource, FeedbackResource, \
                    FriendGroupResource, FriendRequestResource, \
                    HoboPaymentDetailsResource, IndiePaymentDetailsResource, \
                    NewJobTypeResource, PhotoResource, \
                    ProPaymentDetailsResource, ProjectReactionResource, \
                    ProjectResource, PromoCodeResource, \
                    UserAgentManagerResource, UserProjectResource, \
                    UserInterestResource, VideoRatingResource, \
                    VideoRatingCombinedResource, UserTrackingResource, \
                    FriendResource, GroupUsersResource, UserProfileResource, \
                    CompanyProfileResource, ProjectMemberRatingResource, \
                    UserRatingResource, UserNotificationResource, \
                    TeamResource, UserRatingCombinedResource


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


class CustomUserAdmin(UserAdmin, ImportExportModelAdmin):
    form = CustomUserForm
    model = CustomUser
    resource_class = CustomUserResource
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        ('User', {'fields': ('first_name', 'middle_name', 'last_name',
                             'email', 'password', 'date_of_joining')}),
        ('Terms and Conditions', {'fields': ('i_agree',)}),
        ('Registration Process', {'fields': ('registration_complete',)}),
        ('Beta User', {'fields': ('beta_user', 'beta_user_code',
                                  'beta_user_end')}),
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
    # actions = ['delete_selected']

    # def delete_model(modeladmin, request, obj):
    #     # do something with the user instance
    #     obj.delete()

    # def delete_selected(modeladmin, request, queryset):
    #     # do something with the users in the queryset
    #     return django_delete_selected(modeladmin, request, queryset)
    # delete_selected.short_description = \
    #     django_delete_selected.short_description

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


@admin.register(BetaTesterCodes)
class BetaTesterCodesAdmin(ImportExportModelAdmin):
    resource_class = BetaTesterCodesResource


@admin.register(CompanyClient)
class CompanyClientAdmin(ImportExportModelAdmin):
    resource_class = CompanyClientResource


@admin.register(CompanyPaymentDetails)
class CompanyPaymentDetailsAdmin(ImportExportModelAdmin):
    resource_class = CompanyPaymentDetailsResource


@admin.register(CompanyRatingCombined)
class CompanyRatingCombinedAdmin(ImportExportModelAdmin):
    resource_class = CompanyRatingCombinedResource


@admin.register(CompanyRating)
class CompanyRatingAdmin(ImportExportModelAdmin):
    resource_class = CompanyRatingResource


@admin.register(CoWorker)
class CoWorkerAdmin(ImportExportModelAdmin):
    resource_class = CoWorkerResource


@admin.register(DisabledAccount)
class DisabledAccountAdmin(ImportExportModelAdmin):
    resource_class = DisabledAccountResource


@admin.register(Feedback)
class FeedbackAdmin(ImportExportModelAdmin):
    resource_class = FeedbackResource


@admin.register(FriendGroup)
class FriendGroupAdmin(ImportExportModelAdmin):
    resource_class = FriendGroupResource


@admin.register(FriendRequest)
class FriendRequestAdmin(ImportExportModelAdmin):
    resource_class = FriendRequestResource


@admin.register(HoboPaymentsDetails)
class HoboPaymentsDetailsAdmin(ImportExportModelAdmin):
    resource_class = HoboPaymentDetailsResource


@admin.register(IndiePaymentDetails)
class IndiePaymentDetailsAdmin(ImportExportModelAdmin):
    resource_class = IndiePaymentDetailsResource


@admin.register(NewJobType)
class NewJobTypeAdmin(ImportExportModelAdmin):
    resource_class = NewJobTypeResource


@admin.register(Photo)
class PhotoAdmin(ImportExportModelAdmin):
    resource_class = PhotoResource


@admin.register(ProPaymentDetails)
class ProPaymentDetailsAdmin(ImportExportModelAdmin):
    resource_class = ProPaymentDetailsResource


@admin.register(ProjectReaction)
class ProjectReactionAdmin(ImportExportModelAdmin):
    resource_class = ProjectReactionResource


@admin.register(Project)
class ProjectAdmin(ImportExportModelAdmin):
    resource_class = ProjectResource
    list_display = ('id', 'title', 'creator', 'format', 'genre')


@admin.register(PromoCode)
class PromoCodeAdmin(ImportExportModelAdmin):
    resource_class = PromoCodeResource


@admin.register(UserAgentManager)
class UserAgentManagerAdmin(ImportExportModelAdmin):
    resource_class = UserAgentManagerResource


@admin.register(UserProject)
class UserProjectAdmin(ImportExportModelAdmin):
    resource_class = UserProjectResource


@admin.register(UserInterest)
class UserInterestAdmin(ImportExportModelAdmin):
    resource_class = UserInterestResource


@admin.register(VideoRating)
class VideoRatingAdmin(ImportExportModelAdmin):
    resource_class = VideoRatingResource


@admin.register(VideoRatingCombined)
class VideoRatingCombinedAdmin(ImportExportModelAdmin):
    resource_class = VideoRatingCombinedResource


admin.site.site_header = "Filmhobo Admin"
admin.site.site_title = "Filmhobo Admin Portal"
admin.site.index_title = "Welcome to Filmhobo Admin Portal"
admin.site.unregister(CustomUser)
admin.site.register(CustomUser, CustomUserAdmin)


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


class CustomUserSettingsAdmin(ImportExportModelAdmin):
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
    resource_class = CustomUserSettingsResource


admin.site.register(CustomUserSettings, CustomUserSettingsAdmin)


class UserTrackingAdmin(ImportExportModelAdmin):
    resource_class = UserTrackingResource
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }


admin.site.register(UserTracking, UserTrackingAdmin)


class FriendAdmin(ImportExportModelAdmin):
    resource_class = FriendResource
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }


admin.site.register(Friend, FriendAdmin)


class GroupUsersAdmin(ImportExportModelAdmin):
    resource_class = GroupUsersResource
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }


admin.site.register(GroupUsers, GroupUsersAdmin)
# admin.site.register(Feedback)


class UserProfileAdmin(ImportExportModelAdmin):
    resource_class = UserProfileResource
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }


admin.site.register(UserProfile, UserProfileAdmin)


class CompanyProfileAdmin(ImportExportModelAdmin):
    resource_class = CompanyProfileResource
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }


admin.site.register(CompanyProfile, CompanyProfileAdmin)


class ProjectMemberRatingAdmin(ImportExportModelAdmin):
    resource_class = ProjectMemberRatingResource
    list_display = ('user', 'job_type', 'project', 'rating')


admin.site.register(ProjectMemberRating, ProjectMemberRatingAdmin)


class UserRatingAdmin(ImportExportModelAdmin):
    resource_class = UserRatingResource
    list_display = ('user', 'job_type', 'project', 'rating', 'rated_by')


admin.site.register(UserRating, UserRatingAdmin)


class UserNotificationAdmin(ImportExportModelAdmin):
    resource_class = UserNotificationResource
    list_display = (
        'user', 'notification_type', 'from_user',
        'status_type', 'message', 'created_time')


admin.site.register(UserNotification, UserNotificationAdmin)


class UserRatingCombinedAdmin(ImportExportModelAdmin):
    resource_class = UserRatingCombinedResource
    list_display = ('user', 'job_type', 'rating')


admin.site.register(UserRatingCombined, UserRatingCombinedAdmin)


class TeamAdmin(ImportExportModelAdmin):
    resource_class = TeamResource
    list_display = ('project', 'user', 'job_type')


admin.site.register(Team, TeamAdmin)
# admin.site.register(BetaTesterCodes)
# admin.site.register(Project, ProjectAdmin)
