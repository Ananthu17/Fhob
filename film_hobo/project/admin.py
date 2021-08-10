from django.contrib import admin
from .models import Character, Sides, Audition, ProjectTracking, \
    AuditionRating, AuditionRatingCombined, ProjectRating
from django.db import models
from django.forms import CheckboxSelectMultiple

admin.site.register(Character)
admin.site.register(Sides)
admin.site.register(Audition)
admin.site.register(AuditionRating)
admin.site.register(AuditionRatingCombined)
admin.site.register(ProjectRating)


class ProjectTrackingAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }


admin.site.register(ProjectTracking, ProjectTrackingAdmin)
