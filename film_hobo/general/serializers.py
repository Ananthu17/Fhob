from rest_framework import serializers
from .models import Help


class HelpSerializer(serializers.ModelSerializer):

    class Meta:
        model = Help
        fields = ['subject', 'description', 'screenshot']
