from django import template
from hobo_user.models import Project
from project.models import ProjectRating
from project.models import AuditionRating
from rest_framework.generics import get_object_or_404
from django.db.models import Q

register = template.Library()

@register.simple_tag()
def get_my_project_rating(user_id, project_id):
    try:
        project_rating_obj = ProjectRating.objects.get(
                            Q(project=project_id) &
                            Q(rated_by=user_id)
                            )
        rating = project_rating_obj.rating
    except ProjectRating.DoesNotExist:
        rating = 0
    return rating


@register.simple_tag()
def get_my_audition_rating(team_member, audition):
    rating_lst = []
    try:
        audition_rating_obj = AuditionRating.objects.get(
            Q(audition=audition) &
            Q(team_member=team_member)
        )
        rating_lst.append(audition_rating_obj.rating)
        rating_lst.append(audition_rating_obj.review)
    except AuditionRating.DoesNotExist:
        rating_lst.append(0)
        rating_lst.append("")
    return rating_lst

@register.simple_tag()
def get_dict_value_if_exists(dict, key):
    if key in dict:
        return dict[key]
    else:
        return 0

@register.simple_tag()
def get_team_count(dict, key):
    if key in dict:
        team_count = len(dict[key])
        return team_count
    else:
        return 0
