from django import template
from hobo_user.models import CustomUser, CustomUserSettings, \
    UserRatingCombined, FriendRequest, Friend
from django.db.models import Q
register = template.Library()

@register.simple_tag()
def can_contact(logged_user, profile):
    user = profile
    from_user = logged_user
    can_contact = False
    user_settings = CustomUserSettings.objects.get(user=user)
    permission = user_settings.who_can_contact_me

    from_user_rating = UserRatingCombined.objects.filter(
                            user=from_user)
    one_star_count = from_user_rating.filter(rating__gte=1).count()
    two_star_count = from_user_rating.filter(rating__gte=2).count()
    three_star_count = from_user_rating.filter(
                        rating__gte=3).count()
    four_star_count = from_user_rating.filter(
                        rating__gte=4).count()
    five_star_count = from_user_rating.filter(
                        rating__gte=5).count()

    if permission == 'no_one':
        can_contact = False
    if permission == 'all_members':
        can_contact = True
    if permission == 'pros_and_companies_only' and from_user.membership == 'COM':
        can_contact = True
    if permission == 'members_with_rating_1_star' and one_star_count >= 1:
        can_contact = True
    if permission == 'members_with_rating_2_star' and two_star_count >= 1:
        can_contact = True
    if permission == 'members_with_rating_3_star' and three_star_count >= 1:
        can_contact = True
    if permission == 'members_with_rating_4_star' and four_star_count >= 1:
        can_contact = True
    if permission == 'members_with_rating_5_star' and five_star_count >= 1:
        can_contact = True
    return can_contact

@register.simple_tag()
def get_friend_request_status(logged_user, profile_user):
    status = ""
    try:
        friend_obj = Friend.objects.get(user=logged_user)
        all_friends = friend_obj.friends.all()
        if profile_user in all_friends:
            status = 'friend'
        else:
            status = 'not-friend'
    except Friend.DoesNotExist:
        status = 'not-friend'

    if status == 'not-friend':
        user_ids = FriendRequest.objects.filter(
                   user=profile_user).values_list('requested_by', flat=True)
        if logged_user.id in user_ids:
            status = FriendRequest.objects.get(
                            Q(user=profile_user) &
                            Q(requested_by=logged_user)).status
        else:
            user_ids = FriendRequest.objects.filter(
                   user=logged_user).values_list('requested_by', flat=True)
            if profile_user.id in user_ids:
                status = 'respond'
    return status


@register.simple_tag()
def get_groups(friend):
    lst = []
    for obj in friend.group_members.all():
        lst.append(obj.group)
    return lst
