from django import template
from hobo_user.models import Project
from rest_framework.generics import get_object_or_404

register = template.Library()

@register.simple_tag()
def get_samr_display_value(project_id):
    project = get_object_or_404(Project, pk=project_id)
    samr = project.cast_samr
    samr_data = []

    if samr == 'indie_with_rating_1_star':
        samr_data.append("Indie")
        samr_data.append(1)
        samr_data.append(['IND'])
    if samr == 'indie_with_rating_2_star':
        samr_data.append("Indie")
        samr_data.append(2)
        samr_data.append(['IND'])
    if samr == 'indie_with_rating_3_star':
        samr_data.append("Indie")
        samr_data.append(3)
        samr_data.append(['IND'])
    if samr == 'indie_with_rating_4_star':
        samr_data.append("Indie")
        samr_data.append(4)
        samr_data.append(['IND'])
    if samr == 'indie_with_rating_5_star':
        samr_data.append("Indie")
        samr_data.append(5)
        samr_data.append(['IND'])
    if samr == 'pro_with_rating_1_star':
        samr_data.append("Pro")
        samr_data.append(1)
        samr_data.append(['PRO'])
    if samr == 'pro_with_rating_2_star':
        samr_data.append("Pro")
        samr_data.append(2)
        samr_data.append(['PRO'])
    if samr == 'pro_with_rating_3_star':
        samr_data.append("Pro")
        samr_data.append(3)
        samr_data.append(['PRO'])
    if samr == 'pro_with_rating_4_star':
        samr_data.append("Pro")
        samr_data.append(4)
        samr_data.append(['PRO'])
    if samr == 'pro_with_rating_5_star':
        samr_data.append("Pro")
        samr_data.append(5)
        samr_data.append(['PRO'])
    if samr == 'indie_and_pro_with_rating_1_star':
        samr_data.append("Indie/Pro")
        samr_data.append(1)
        samr_data.append(['IND', 'PRO'])
    if samr == 'indie_and_pro_with_rating_2_star':
        samr_data.append("Indie/Pro")
        samr_data.append(2)
        samr_data.append(['IND', 'PRO'])
    if samr == 'indie_and_pro_with_rating_3_star':
        samr_data.append("Indie/Pro")
        samr_data.append(3)
        samr_data.append(['IND', 'PRO'])
    if samr == 'indie_and_pro_with_rating_4_star':
        samr_data.append("Indie/Pro")
        samr_data.append(4)
        samr_data.append(['IND', 'PRO'])
    if samr == 'indie_and_pro_with_rating_5_star':
        samr_data.append("Indie/Pro")
        samr_data.append(5)
        samr_data.append(['IND', 'PRO'])
    return samr_data

@register.simple_tag()
def get_crew_samr_display_value(project_id):
    project = get_object_or_404(Project, pk=project_id)
    samr = project.crew_samr
    print("----------------", samr)
    samr_data = []

    if samr == 'indie_with_rating_1_star':
        samr_data.append("Indie")
        samr_data.append(1)
        samr_data.append(['IND'])
    if samr == 'indie_with_rating_2_star':
        samr_data.append("Indie")
        samr_data.append(2)
        samr_data.append(['IND'])
    if samr == 'indie_with_rating_3_star':
        samr_data.append("Indie")
        samr_data.append(3)
        samr_data.append(['IND'])
    if samr == 'indie_with_rating_4_star':
        samr_data.append("Indie")
        samr_data.append(4)
        samr_data.append(['IND'])
    if samr == 'indie_with_rating_5_star':
        samr_data.append("Indie")
        samr_data.append(5)
        samr_data.append(['IND'])
    if samr == 'pro_with_rating_1_star':
        samr_data.append("Pro")
        samr_data.append(1)
        samr_data.append(['PRO'])
    if samr == 'pro_with_rating_2_star':
        samr_data.append("Pro")
        samr_data.append(2)
        samr_data.append(['PRO'])
    if samr == 'pro_with_rating_3_star':
        samr_data.append("Pro")
        samr_data.append(3)
        samr_data.append(['PRO'])
    if samr == 'pro_with_rating_4_star':
        samr_data.append("Pro")
        samr_data.append(4)
        samr_data.append(['PRO'])
    if samr == 'pro_with_rating_5_star':
        samr_data.append("Pro")
        samr_data.append(5)
        samr_data.append(['PRO'])
    if samr == 'indie_and_pro_with_rating_1_star':
        samr_data.append("Indie/Pro")
        samr_data.append(1)
        samr_data.append(['IND', 'PRO'])
    if samr == 'indie_and_pro_with_rating_2_star':
        samr_data.append("Indie/Pro")
        samr_data.append(2)
        samr_data.append(['IND', 'PRO'])
    if samr == 'indie_and_pro_with_rating_3_star':
        samr_data.append("Indie/Pro")
        samr_data.append(3)
        samr_data.append(['IND', 'PRO'])
    if samr == 'indie_and_pro_with_rating_4_star':
        samr_data.append("Indie/Pro")
        samr_data.append(4)
        samr_data.append(['IND', 'PRO'])
    if samr == 'indie_and_pro_with_rating_5_star':
        samr_data.append("Indie/Pro")
        samr_data.append(5)
        samr_data.append(['IND', 'PRO'])
    return samr_data


@register.simple_tag()
def get_range_value(count):
    return range(0, count)
