
from .models import UserMessage
from rest_framework import serializers


class UserMessageSerializer(serializers.ModelSerializer):
    to_user = serializers.CharField(
        max_length=150,
        required=True,
    )

    class Meta:
        model = UserMessage
        fields = ['to_user', 'subject', 'message']

