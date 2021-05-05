from django import template
from rest_framework.authtoken.models import Token

register = template.Library()

@register.simple_tag()
def get_my_token(request):
    user = request.user
    key = Token.objects.get(user=user).key
    token = 'Token '+key
    return token
