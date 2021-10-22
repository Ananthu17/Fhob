from django.contrib import admin
from .models import Character, Sides, Audition, ProjectTracking, \
    AuditionRating, AuditionRatingCombined, ProjectRating, Comment, \
    SceneImages, ProjectCrew, CrewApplication, AttachedCrewMember, \
    ReportVideo
from django.db import models
from django.forms import CheckboxSelectMultiple
from import_export.admin import ImportExportModelAdmin
from .importexport import CharacterResource, SidesResource, AuditionResource, \
                          AuditionRatingResource, \
                          AuditionRatingCombinedResource, \
                          ProjectRatingResource, CommentResource, \
                          SceneImagesResource, ProjectCrewResource, \
                          CrewApplicationResource, \
                          AttachedCrewMemberResource, ProjectTrackingResource
from django.utils.html import format_html


@admin.register(Character)
class CharacterAdmin(ImportExportModelAdmin):
    resource_class = CharacterResource


@admin.register(Sides)
class SidesAdmin(ImportExportModelAdmin):
    resource_class = SidesResource


@admin.register(Audition)
class AuditionAdmin(ImportExportModelAdmin):
    resource_class = AuditionResource


@admin.register(AuditionRating)
class AuditionRatingAdmin(ImportExportModelAdmin):
    resource_class = AuditionRatingResource


@admin.register(AuditionRatingCombined)
class AuditionRatingCombinedAdmin(ImportExportModelAdmin):
    resource_class = AuditionRatingCombinedResource


@admin.register(ProjectRating)
class ProjectRatingAdmin(ImportExportModelAdmin):
    resource_class = ProjectRatingResource


@admin.register(Comment)
class CommentAdmin(ImportExportModelAdmin):
    resource_class = CommentResource


# admin.site.register(Character)
# admin.site.register(Sides)
# admin.site.register(Audition)
# admin.site.register(AuditionRating)
# admin.site.register(AuditionRatingCombined)
# admin.site.register(ProjectRating)
# admin.site.register(Comment)


class ProjectTrackingAdmin(ImportExportModelAdmin):
    resource_class = ProjectTrackingResource
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }


@admin.register(SceneImages)
class SceneImagesAdmin(ImportExportModelAdmin):
    resource_class = SceneImagesResource


@admin.register(ProjectCrew)
class ProjectCrewAdmin(ImportExportModelAdmin):
    resource_class = ProjectCrewResource


@admin.register(CrewApplication)
class CrewApplicationAdmin(ImportExportModelAdmin):
    resource_class = CrewApplicationResource


@admin.register(AttachedCrewMember)
class AttachedCrewMemberAdmin(ImportExportModelAdmin):
    resource_class = AttachedCrewMemberResource


    # admin.site.register(SceneImages)
# admin.site.register(ProjectCrew)
# admin.site.register(CrewApplication)
# admin.site.register(AttachedCrewMember)
class ReportVideoAdmin(admin.ModelAdmin):
    list_display = ('reported_by_user', 'project_id', 'project_name',
                    'show_video_url', 'reason')

    def show_video_url(self, obj):
        return format_html("<a href='{url}' target='_blank'>{url}</a>", url=obj.video_url)


admin.site.register(ProjectTracking, ProjectTrackingAdmin)
admin.site.register(ReportVideo, ReportVideoAdmin)
