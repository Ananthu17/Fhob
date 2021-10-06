
from .models import UserMessage
from rest_framework import serializers


class UserMessageSerializer(serializers.ModelSerializer):
    to_user = serializers.CharField(
        max_length=150,
        required=False,
    )

    class Meta:
        model = UserMessage
        fields = ['to_user', 'subject', 'message']
        extra_kwargs = {'message': {'required': False}}


class MessageThreadSerializer(serializers.Serializer):
    msg_thread = serializers.CharField(
        max_length=150,
        required=True,
    )


class ComposeMessageFileUploadSerializer(serializers.Serializer):
    message_id = serializers.CharField(
        max_length=150,
        required=True,
    )
    images = serializers.ImageField(required=False)
    files = serializers.FileField(required=False)



