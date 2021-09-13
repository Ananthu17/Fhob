from django import template
from hobo_user.models import CustomUser, CustomUserSettings, \
    UserRatingCombined

register = template.Library()

@register.simple_tag()
def can_view_profile(logged_user, profile):

    can_visit = False
    profile_user_settings = CustomUserSettings.objects.get(user=profile)
    permission = profile_user_settings.profile_visibility

    logged_user_rating = UserRatingCombined.objects.filter(
                            user=logged_user)
    one_star_count = logged_user_rating.filter(rating__gte=1).count()
    two_star_count = logged_user_rating.filter(rating__gte=2).count()
    three_star_count = logged_user_rating.filter(
                        rating__gte=3).count()
    four_star_count = logged_user_rating.filter(
                        rating__gte=4).count()
    five_star_count = logged_user_rating.filter(
                        rating__gte=5).count()

    if permission == 'no_one':
        can_visit = False
    if permission == 'all_members':
        can_visit = True
    if permission == 'pros_and_companies_only' and logged_user.membership == 'COM':
        can_visit = True
    if permission == 'members_with_rating_1_star' and one_star_count >= 1:
        can_visit = True
    if permission == 'members_with_rating_2_star' and two_star_count >= 1:
        can_visit = True
    if permission == 'members_with_rating_3_star' and three_star_count >= 1:
        can_visit = True
    if permission == 'members_with_rating_4_star' and four_star_count >= 1:
        can_visit = True
    if permission == 'members_with_rating_5_star' and five_star_count >= 1:
        can_visit = True
    if profile == logged_user:
        can_visit = True
    return can_visit


