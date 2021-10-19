from rest_framework import serializers
from .models import Help, EmailUs


class HelpSerializer(serializers.ModelSerializer):

    class Meta:
        model = Help
        fields = ['subject', 'description', 'screenshot']


class ContactUsSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmailUs
        fields = ['subject', 'message', 'topic']
