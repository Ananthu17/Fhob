from django.urls import path
from .views import ComposeMessageView, ComposeMessageAPI, AllMessagesView

urlpatterns = [
     path('compose-message/', ComposeMessageView.as_view(), name='compose-message'),
     path('all-messages/', AllMessagesView.as_view(), name='all-messages'),
     path('compose-message-api/', ComposeMessageAPI.as_view(),
          name='compose-message-api'),
]
