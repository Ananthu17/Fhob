from django import template
from hobo_user.models import CustomUser, CustomUserSettings, \
    UserTracking, UserRatingCombined

register = template.Library()

@register.simple_tag()
def can_track(logged_user, profile):
    track_user = profile
    track_by_user = logged_user

    can_track = False
    track_user_settings = CustomUserSettings.objects.get(user=track_user)
    permission = track_user_settings.who_can_track_me

    track_by_user_rating = UserRatingCombined.objects.filter(
                            user=track_by_user)
    one_star_count = track_by_user_rating.filter(rating__gte=1).count()
    two_star_count = track_by_user_rating.filter(rating__gte=2).count()
    three_star_count = track_by_user_rating.filter(
                        rating__gte=3).count()
    four_star_count = track_by_user_rating.filter(
                        rating__gte=4).count()
    five_star_count = track_by_user_rating.filter(
                        rating__gte=5).count()

    if permission == 'no_one':
        can_track = False
    if permission == 'all_members':
        can_track = True
    if permission == 'pros_and_companies_only' and track_by_user.membership == 'COM':
        can_track = True
    if permission == 'members_with_rating_1_star' and one_star_count >= 1:
        can_track = True
    if permission == 'members_with_rating_2_star' and two_star_count >= 1:
        can_track = True
    if permission == 'members_with_rating_3_star' and three_star_count >= 1:
        can_track = True
    if permission == 'members_with_rating_4_star' and four_star_count >= 1:
        can_track = True
    if permission == 'members_with_rating_5_star' and five_star_count >= 1:
        can_track = True

    return can_track

@register.simple_tag()
def get_tracking_list(logged_user, profile):
    track_user = profile
    track_by_user = logged_user
    try:
        tracking_info = UserTracking.objects.get(
                        user=track_user).tracked_by.all()
        tracking_users = tracking_info.values_list('id', flat=True)
        if track_by_user.id in tracking_users:
            return True
    except UserTracking.DoesNotExist:
        return False

