from django import template
from hobo_user.models import Project, VideoRating
from rest_framework.generics import get_object_or_404
from django.db.models import Q

register = template.Library()

@register.simple_tag()
def get_my_project_rating(user_id, project_id):
    try:
        video_rating_obj = VideoRating.objects.get(
                            Q(project=project_id) &
                            Q(rated_by=user_id)
                            )
        rating = video_rating_obj.rating
    except VideoRating.DoesNotExist:
        rating = 0
    return rating


