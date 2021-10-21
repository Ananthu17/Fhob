from import_export.fields import Field
from import_export.resources import ModelResource

from .models import EthnicAppearance, AthleticSkill, Country, \
    GuildMembership, JobType, Location, CustomUser, BetaTesterCodes, \
    CompanyClient, CompanyPaymentDetails, CompanyProfile, \
    CompanyRatingCombined, CompanyRating, CoWorker, CustomUserSettings, \
    DisabledAccount, Feedback, FriendGroup, FriendRequest, \
    HoboPaymentsDetails, IndiePaymentDetails, NewJobType, Photo, \
    ProPaymentDetails, ProjectReaction, Project, PromoCode, UserAgentManager
from payment.models import FilmHoboSenderEmail


class CustomUserResource(ModelResource):

    class Meta:
        model = CustomUser


class BetaTesterCodesResource(ModelResource):

    class Meta:
        model = BetaTesterCodes


class CompanyClientResource(ModelResource):

    class Meta:
        model = CompanyClient


class CompanyPaymentDetailsResource(ModelResource):

    class Meta:
        model = CompanyPaymentDetails


class CompanyProfileResource(ModelResource):

    class Meta:
        model = CompanyProfile


class CompanyRatingCombinedResource(ModelResource):

    class Meta:
        model = CompanyRatingCombined


class CompanyRatingResource(ModelResource):

    class Meta:
        model = CompanyRating


class CoWorkerResource(ModelResource):

    class Meta:
        model = CoWorker


class CustomUserSettingsResource(ModelResource):

    class Meta:
        model = CustomUserSettings


class DisabledAccountResource(ModelResource):

    class Meta:
        model = DisabledAccount


class FeedbackResource(ModelResource):

    class Meta:
        model = Feedback


class FriendGroupResource(ModelResource):

    class Meta:
        model = FriendGroup


class FriendRequestResource(ModelResource):

    class Meta:
        model = FriendRequest


class HoboPaymentDetailsResource(ModelResource):

    class Meta:
        model = HoboPaymentsDetails


class IndiePaymentDetailsResource(ModelResource):

    class Meta:
        model = IndiePaymentDetails


class NewJobTypeResource(ModelResource):

    class Meta:
        model = NewJobType


class PhotoResource(ModelResource):

    class Meta:
        model = Photo


class ProPaymentDetailsResource(ModelResource):

    class Meta:
        model = ProPaymentDetails


class ProjectReactionResource(ModelResource):

    class Meta:
        model = ProjectReaction


class ProjectResource(ModelResource):

    class Meta:
        model = Project


class PromoCodeResource(ModelResource):

    class Meta:
        model = PromoCode


class UserAgentManagerResource(ModelResource):

    class Meta:
        model = UserAgentManager


class EthnicAppearanceResource(ModelResource):

    class Meta:
        model = EthnicAppearance


class AthleticSkillResource(ModelResource):

    class Meta:
        model = AthleticSkill


class CountryResource(ModelResource):

    class Meta:
        model = Country


class GuildMembershipResource(ModelResource):

    class Meta:
        model = GuildMembership


class JobTypeResource(ModelResource):

    class Meta:
        model = JobType


class LocationResource(ModelResource):
    city = Field(attribute='city', column_name='city')
    state = Field(attribute='state', column_name='state')
    country = Field(attribute='country', column_name='country')

    class Meta:
        model = Location


class FilmHoboSenderEmailResource(ModelResource):

    class Meta:
        model = FilmHoboSenderEmail
