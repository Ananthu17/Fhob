
from django import template
from django.db.models import Q
from hobo_user.models import CustomUser, CompanyRating, UserRating, \
    CompanyProfile

register = template.Library()

@register.simple_tag()
def user_has_account(email):
    try:
        user = CustomUser.objects.get(email=email)
        return user
    except CustomUser.DoesNotExist:
        pass

@register.simple_tag()
def get_url(url):
    if url.startswith('http'):
        hyperlink = url
    elif url.startswith('www'):
        hyperlink = "http://"+url
    else:
        hyperlink = "http://www."+url
    return hyperlink

@register.simple_tag()
def get_more_modal_id(position):
    pos = []
    pos = str(position).split(" ")
    position = '_'.join(pos)
    return position

@register.simple_tag()
def get_my_rating(current_user, profile_id):
    rating = 0
    # profile_user = CustomUser.objects.get(pk=profile_id)

    try:
        rating = CompanyRating.objects.get(
                    Q(rated_by=current_user) &
                    Q(company=profile_id)
                    ).rating
    except CompanyRating.DoesNotExist:
        rating = 0

    return rating


@register.simple_tag()
def get_my_skill_rating(current_user, team_obj):
    rating = 0
    try:
        rating = UserRating.objects.get(
                    Q(rated_by=current_user) &
                    Q(user=team_obj.user) &
                    Q(job_type=team_obj.job_type) &
                    Q(project=team_obj.project)
                    ).rating
    except UserRating.DoesNotExist:
        rating = 0
    return rating


@register.simple_tag()
def get_dict_value(dict, key):
    return dict[key]
