from django.urls import path
from .views import HelpAPI, HelpView, BetaUserAdmin, \
     HelpProject, HelpGettingStarted, HelpRating

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
    ]
