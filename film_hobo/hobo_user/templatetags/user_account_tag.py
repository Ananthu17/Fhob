from django import template
from hobo_user.models import CustomUser

register = template.Library()

@register.simple_tag()
def user_has_account(email):
    try:
        user = CustomUser.objects.get(email=email)
        id = user.id
        return id
    except CustomUser.DoesNotExist:
        pass
