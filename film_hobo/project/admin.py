from django.contrib import admin
from .models import Character, Sides, Audition, ProjectTracking, \
    AuditionRating, AuditionRatingCombined, ProjectRating, Comment, \
    SceneImages, ProjectCrew, CrewApplication, AttachedCrewMember, \
    ReportVideo
from django.db import models
from django.forms import CheckboxSelectMultiple
from django.utils.html import format_html

admin.site.register(Character)
admin.site.register(Sides)
admin.site.register(Audition)
admin.site.register(AuditionRating)
admin.site.register(AuditionRatingCombined)
admin.site.register(ProjectRating)
admin.site.register(Comment)


class ProjectTrackingAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }


class ReportVideoAdmin(admin.ModelAdmin):
    list_display = ('reported_by_user', 'project_id', 'project_name',
                    'show_video_url', 'reason')

    def show_video_url(self, obj):
        return format_html("<a href='{url}' target='_blank'>{url}</a>", url=obj.video_url)


admin.site.register(ProjectTracking, ProjectTrackingAdmin)
admin.site.register(ReportVideo, ReportVideoAdmin)
admin.site.register(SceneImages)
admin.site.register(ProjectCrew)
admin.site.register(CrewApplication)
admin.site.register(AttachedCrewMember)
