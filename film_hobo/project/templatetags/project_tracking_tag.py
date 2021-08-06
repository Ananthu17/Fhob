
from django import template
from hobo_user.models import Project
from project.models import ProjectTracking
from rest_framework.generics import get_object_or_404
from django.db.models import Q

register = template.Library()

@register.simple_tag()
def get_project_tracking_list(user, project):
    try:
        tracking_info = ProjectTracking.objects.get(
                        project=project).tracked_by.all()
        tracking_users = tracking_info.values_list('id', flat=True)
        if user.id in tracking_users:
            return True
        else:
            return False
    except ProjectTracking.DoesNotExist:
        return False




