from django.urls import path
from .views import ComposeMessageView, ComposeMessageAPI, AllMessagesView, \
     AddToPriorityAPI, PriorityMessagesView, GetMessageNotificationAPI, \
     DeleteMessageAPI, RemoveFromPriorityAPI, \
     ReportSpamAPI, MessageDetailView

urlpatterns = [
     path('compose-message/', ComposeMessageView.as_view(),
          name='compose-message'),
     path('all-messages/', AllMessagesView.as_view(), name='all-messages'),
     path('messages/<int:id>/', MessageDetailView.as_view(), name='messages'),
     path('compose-message-api/', ComposeMessageAPI.as_view(),
          name='compose-message-api'),
     path('add-to-priority-api/', AddToPriorityAPI.as_view(),
          name='add-to-priority-api'),
     path('remove-from-priority-api/', RemoveFromPriorityAPI.as_view(),
          name='remove-from-priority-api'),
     path('priority-messages/', PriorityMessagesView.as_view(),
          name='priority-messages'),
     path('delete-message-api/', DeleteMessageAPI.as_view(),
          name='delete-message-api'),
     path('report-spam-api/', ReportSpamAPI.as_view(),
          name='report-spam-api'),
     path('get-message-notification-api/', GetMessageNotificationAPI.as_view(),
          name='get-message-notification-api'),
]
