from django.urls import path
from .views import HelpAPI, HelpView

urlpatterns = [
    path('help-api/', HelpAPI.as_view(), name='help-api'),
    path('help/', HelpView.as_view(), name='help'),
    ]
