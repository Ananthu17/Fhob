

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone


def notify(room_name, message):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(room_name, message)
    return


def get_notifications_time(time_posted):
    timediff = timezone.now() - time_posted
    seconds = timediff.total_seconds()
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    if timediff.days != 0:
        return str(timediff.days) + " days"
    else:
        if hours != 0:
            return str(hours) + " hours"
        elif minutes != 0:
            return str(minutes) + " minutes"
        else:
            return str(seconds) + " seconds"
