from django.urls import path

from .views import InitialUserDetailSaveAPI, InitialUserDetailSavePage

app_name = "initial_user"

urlpatterns = [
    path('landing_home_api/', InitialUserDetailSaveAPI.as_view(),
         name='landing_home_api'),
    path('landing_home/', InitialUserDetailSavePage.as_view(),
         name='landing_home')
]
