from django.urls import path
from .views import HelpAPI, HelpView, BetaUserAdmin, \
     HelpProject, HelpGettingStarted, HelpRating, TermsOfService, \
     PrivacyPolicy, RefundPolicy, IntellectualPropertyRights, Membership

app_name = "general"

urlpatterns = [
    path('help-api/', HelpAPI.as_view(), name='help-api'),
    path('help/', HelpView.as_view(), name='help'),
    path('help/project/', HelpProject.as_view(), name='help_project'),
    path('help/getting_started/',
         HelpGettingStarted.as_view(), name='help_getting_started'),
    path('help/rating/', HelpRating.as_view(), name='help_rating'),
    path('beta_user_admin/', BetaUserAdmin.as_view(),
         name='beta_user_admin'),
    path('terms_of_service/', TermsOfService.as_view(),
         name='terms_of_service'),
    path('privacy_policy/', PrivacyPolicy.as_view(), name='privacy_policy'),
    path('refund_policy/', RefundPolicy.as_view(), name='refund_policy'),
    path('intellectual_property_rights/', IntellectualPropertyRights.as_view(),
         name='intellectual_property_rights'),
    path('membership/', Membership.as_view(),
         name='membership'),
    ]
