from rest_framework import serializers
from .models import Help, EmailUs, ReportProblem


class HelpSerializer(serializers.ModelSerializer):

    class Meta:
        model = Help
        fields = ['subject', 'description', 'screenshot']



class ContactUsSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmailUs
        fields = ['subject', 'message', 'topic']


class ReportProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportProblem
        fields = ['user_email', 'name', 'user_phone', 'user_problem',
                  'timestamp']

