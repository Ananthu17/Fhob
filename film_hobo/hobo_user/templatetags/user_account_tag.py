from django import template
from hobo_user.models import CustomUser

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
