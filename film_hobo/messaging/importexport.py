from import_export.resources import ModelResource

from .models import UserMessageImages, UserMessageFileUpload, \
                    UserMessage, SpamMessage, MessageStatus, \
                    MessageNotification


class UserMessageImagesResource(ModelResource):

    class Meta:
        model = UserMessageImages


class UserMessageFileUploadResource(ModelResource):

    class Meta:
        model = UserMessageFileUpload


class UserMessageResource(ModelResource):

    class Meta:
        model = UserMessage


class SpamMessageResource(ModelResource):

    class Meta:
        model = SpamMessage


class MessageStatusResource(ModelResource):

    class Meta:
        model = MessageStatus


class MessageNotificationResource(ModelResource):

    class Meta:
        model = MessageNotification
