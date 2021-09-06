from django import template
from hobo_user.models import CustomUser, UserNotification
from django.utils import timezone
from django.db.models import Q

register = template.Library()


@register.simple_tag()
def get_notifications_count(email):
    try:
        user = CustomUser.objects.get(email=email)
        notifications_count = UserNotification.objects.filter(
                        Q(user=user) &
                        Q(status_type='unread')
                        ).count()
        if notifications_count:
            return notifications_count
    except CustomUser.DoesNotExist:
        pass
    return ""


@register.simple_tag()
def get_notifications_time(time_posted):
    timediff = timezone.now() - time_posted
    seconds = timediff.total_seconds()
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    if timediff.days > 7:
        return str(timediff.days) + " weeks"
    elif((timediff.days >= 1) and (timediff.days <= 7)):
        return str(timediff.days) + " days"
    else:
        if hours != 0:
            return str(hours) + " hours"
        elif minutes != 0:
            return str(minutes) + " minutes"
        else:
            return str(seconds) + " seconds"

