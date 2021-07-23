from hobo_user.models import UserRating, Project
from project.models import Character, Sides
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


class ProjectVideoURLSerializer(serializers.Serializer):
    video_type = serializers.CharField(
        max_length=150,
        required=True,
    )
    video_url = serializers.CharField(
        max_length=150,
        required=True,
    )
    id = serializers.CharField(
        max_length=150,
        required=True,
    )

    class Meta:
        model = Project
        fields = ['id', 'video_url', 'video_type']


class CharacterSerializer(serializers.ModelSerializer):
    project = serializers.CharField(
        max_length=150,
        required=True,
    )
    password = serializers.CharField(
        max_length=150,
        required=False, allow_null=True
    )

    class Meta:
        model = Character
        fields = ['name', 'description', 'project', 'password']


class UpdateCharacterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Character
        fields = ['name', 'description', 'project', 'password']


class SidesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sides
        fields = ['project', 'character', 'scene_1', 'scene_2', 'scene_3']


class ProjectLastDateSerializer(serializers.ModelSerializer):
    id = serializers.CharField(
        max_length=150,
        required=True,
    )

    class Meta:
        model = Project
        fields = ['id', 'last_date']
