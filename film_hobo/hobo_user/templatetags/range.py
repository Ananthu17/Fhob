from django import template

register = template.Library()


@register.filter(name='times')
def times(number):
    return range(number)

@register.filter(name='blank')
def blank(number):
    return range(5-number)
