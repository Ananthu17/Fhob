from rest_framework import serializers
from .models import Help, ReportProblem


class HelpSerializer(serializers.ModelSerializer):

    class Meta:
        model = Help
        fields = ['subject', 'description', 'screenshot']


class ReportProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportProblem
        fields = ['user_email', 'name', 'user_phone', 'user_problem',
                  'timestamp']
