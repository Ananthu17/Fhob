from django.urls import path
from .views import ComposeMessageView, ComposeMessageAPI, AllMessagesView, \
     AddToPriorityAPI, PriorityMessagesView, GetMessageNotificationAPI, \
     DeleteMessageAPI, RemoveFromPriorityAPI, GetNewMessageAJAXView, \
     ReportSpamAPI, MessageDetailView, ComposeMessageUploadAPI, \
     CovertWordToHtmlView, CovertExcelToHtmlView

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
     path('compose-message-file-upload-api/',
          ComposeMessageUploadAPI.as_view(),
          name='compose-message-file-upload-api'),
     path('get-new-message-html/', GetNewMessageAJAXView.as_view(),
          name='get-new-message-html'),
     path('word-to-html-api/', CovertWordToHtmlView.as_view(),
          name='word-to-html-api'),
     path('excel-to-html-api/', CovertExcelToHtmlView.as_view(),
          name='excel-to-html-api'),
]
