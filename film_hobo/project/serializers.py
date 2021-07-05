from hobo_user.models import UserRating
from rest_framework import serializers


class RateUserSkillsSerializer(serializers.Serializer):
    project_member_id = serializers.CharField(
        max_length=150,
        required=True,
    )
    reason = serializers.CharField(
        max_length=150,
        required=False,
    )
    rating = serializers.CharField(
        max_length=150,
        required=True,
    )

    class Meta:
        model = UserRating
        fields = ['reason', 'rating', 'project_member_id' ]
