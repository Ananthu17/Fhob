from import_export.resources import ModelResource

from .models import Character, Sides, Audition, ProjectTracking, \
    AuditionRating, AuditionRatingCombined, ProjectRating, Comment, \
    SceneImages, ProjectCrew, CrewApplication, AttachedCrewMember


class CharacterResource(ModelResource):

    class Meta:
        model = Character


class CharacterResource(ModelResource):

    class Meta:
        model = Character


class SidesResource(ModelResource):

    class Meta:
        model = Sides


class AuditionResource(ModelResource):

    class Meta:
        model = Audition


class ProjectTrackingResource(ModelResource):

    class Meta:
        model = ProjectTracking


class AuditionRatingResource(ModelResource):

    class Meta:
        model = AuditionRating


class AuditionRatingCombinedResource(ModelResource):

    class Meta:
        model = AuditionRatingCombined


class ProjectRatingResource(ModelResource):

    class Meta:
        model = ProjectRating


class CommentResource(ModelResource):

    class Meta:
        model = Comment


class SceneImagesResource(ModelResource):

    class Meta:
        model = SceneImages


class ProjectCrewResource(ModelResource):

    class Meta:
        model = ProjectCrew


class CrewApplicationResource(ModelResource):

    class Meta:
        model = CrewApplication


class AttachedCrewMemberResource(ModelResource):

    class Meta:
        model = AttachedCrewMember
