from django.contrib import admin
from .models import UserMessage, SpamMessage, MessageStatus, \
    MessageNotification, UserMessageImages, UserMessageFileUpload


class UserMessageAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'msg_thread', 'subject')


class SpamMessageAdmin(admin.ModelAdmin):
    list_display = ('spam_user', 'reported_by')


class MessageStatusAdmin(admin.ModelAdmin):
    list_display = ('user', 'msg_thread', 'is_read', 'is_priority', 'is_spam')


class MessageNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'from_user', 'status_type', 'notification_message')


admin.site.register(UserMessage, UserMessageAdmin)
admin.site.register(SpamMessage, SpamMessageAdmin)
admin.site.register(MessageStatus, MessageStatusAdmin)
admin.site.register(MessageNotification, MessageNotificationAdmin)
admin.site.register(UserMessageImages)
admin.site.register(UserMessageFileUpload)
