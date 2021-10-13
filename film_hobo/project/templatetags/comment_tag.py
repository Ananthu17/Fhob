from django import template
from project.models import Comment
from rest_framework.generics import get_object_or_404
from django.db.models import Q

register = template.Library()

@register.simple_tag()
def get_reply_comments(comment, project):
    comments = Comment.objects.filter(
               Q(project=project) &
               Q(reply_to=comment)
                ).order_by('-created_time')
    return comments
