from hobo_user.models import UserRating, Project
from project.models import Audition, AuditionRating, Character, Comment, Sides, \
    ProjectRating, Comment
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
        fields = ['id', 'video_url', 'video_type', 'video_cover_image']


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


class AuditionSerializer(serializers.ModelSerializer):

    project = serializers.CharField(
        max_length=150,
        required=True,
    )
    character = serializers.CharField(
        max_length=150,
        required=True,
    )
    location = serializers.CharField(
        max_length=150,
        required=True,
    )
    video_type = serializers.CharField(
        max_length=150,
        required=True,
    )
    video_url = serializers.CharField(
        max_length=150,
        required=True,
    )

    class Meta:
        model = Audition
        fields = ['name', 'agent_email', 'agent_name',
                  'project', 'character', 'location', 'video_url',
                  'video_type', 'cover_image']


class PostProjectVideoSerializer(serializers.Serializer):
    project_id = serializers.CharField(
        max_length=150,
        required=True,
    )


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=150,
        required=True,
    )
    project_id = serializers.CharField(
        max_length=150,
        required=True,
    )


class ProjectLoglineSerializer(serializers.ModelSerializer):
    project_id = serializers.CharField(
        max_length=150,
        required=True,
    )

    class Meta:
        model = Project
        fields = ['project_id', 'logline', 'project_info']


class TrackProjectSerializer(serializers.Serializer):
    project_id = serializers.CharField(
        max_length=150,
        required=True,
    )


class RateAuditionSerializer(serializers.ModelSerializer):
    audition = serializers.CharField(
        max_length=150,
        required=True,
    )
    team_member = serializers.CharField(
        max_length=150,
        required=True,
    )
    rating = serializers.CharField(
        max_length=150,
        required=True,
    )

    class Meta:
        model = AuditionRating
        fields = ['audition', 'team_member', 'rating', 'review']


class AuditionStatusSerializer(serializers.ModelSerializer):
    audition = serializers.CharField(
        max_length=150,
        required=True,
    )
    status = serializers.CharField(
        max_length=150,
        required=True,
    )

    class Meta:
        model = AuditionRating
        fields = ['audition', 'status']


class ProjectRatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectRating
        fields = ['project', 'rating', 'reason']


class RemoveCastSerializer(serializers.Serializer):
    character = serializers.CharField(
        max_length=150,
        required=True,
    )


class ReplaceCastSerializer(serializers.Serializer):
    character = serializers.CharField(
        max_length=150,
        required=True,
    )
    user = serializers.CharField(
        max_length=150,
        required=False,
    )
    name = serializers.CharField(
        max_length=150,
        required=False,
    )


class CommentSerializer(serializers.ModelSerializer):
    project = serializers.CharField(
        max_length=150,
        required=True,
    )
    reply_to = serializers.CharField(
        max_length=150,
        required=False,
    )
    mentioned_users = serializers.CharField(
                        max_length=150,
                        required=False,
                    )

    class Meta:
        model = Comment
        fields = ['project', 'comment_txt', 'reply_to', 'mentioned_users']
        extra_kwargs = {'comment_txt': {'required': True}}


class DeleteCommentSerializer(serializers.Serializer):
    comment_id = serializers.CharField(
        max_length=150,
        required=True,
    )
