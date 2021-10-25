from django.contrib import admin
from .models import UserMessage, SpamMessage, MessageStatus, \
    MessageNotification, UserMessageImages, UserMessageFileUpload
from .importexport import UserMessageImagesResource, \
                          UserMessageFileUploadResource, \
                          UserMessageResource, SpamMessageResource, \
                          MessageStatusResource, MessageNotificationResource
from import_export.admin import ImportExportModelAdmin


class UserMessageAdmin(ImportExportModelAdmin):
    resource_class = UserMessageResource
    list_display = ('from_user', 'to_user', 'msg_thread', 'subject')


class SpamMessageAdmin(ImportExportModelAdmin):
    resource_class = SpamMessageResource
    list_display = ('spam_user', 'reported_by')


class MessageStatusAdmin(ImportExportModelAdmin):
    resource_class = MessageStatusResource
    list_display = ('user', 'msg_thread', 'is_read', 'is_priority', 'is_spam')


class MessageNotificationAdmin(ImportExportModelAdmin):
    resource_class = MessageNotificationResource
    list_display = ('user', 'from_user', 'status_type', 'notification_message')


@admin.register(UserMessageImages)
class UserMessageImagesAdmin(ImportExportModelAdmin):
    resource_class = UserMessageImagesResource


@admin.register(UserMessageFileUpload)
class UserMessageFileUploadAdmin(ImportExportModelAdmin):
    resource_class = UserMessageFileUploadResource


admin.site.register(UserMessage, UserMessageAdmin)
admin.site.register(SpamMessage, SpamMessageAdmin)
admin.site.register(MessageStatus, MessageStatusAdmin)
admin.site.register(MessageNotification, MessageNotificationAdmin)
# admin.site.register(UserMessageImages)
# admin.site.register(UserMessageFileUpload)
