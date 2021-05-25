from django import template
from hobo_user.models import CustomUser, UserNotification
from django.conf import settings
from django.db.models import Q

register = template.Library()

@register.simple_tag()
def get_notifications(email):
    try:
        user = CustomUser.objects.get(email=email)
        notifications = UserNotification.objects.filter(
                        user=user).order_by('-created_time')
        if notifications:
            return notifications
    except CustomUser.DoesNotExist:
        pass
    return ""
