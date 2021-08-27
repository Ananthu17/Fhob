from django.urls import path
from .views import HelpAPI, HelpView, AddBetaUserCode, BetaUserAdmin

app_name = "general"

urlpatterns = [
    path('help-api/', HelpAPI.as_view(), name='help-api'),
    path('help/', HelpView.as_view(), name='help'),
    path('add_beta_user_code/', AddBetaUserCode.as_view(),
         name='add_beta_user_code'),
    path('beta_user_admin/', BetaUserAdmin.as_view(),
         name='beta_user_admin'),
    ]
