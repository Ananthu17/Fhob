# from django import template
# from hobo_user.models import CustomUser, Photo
# from django.conf import settings
# from django.db.models import Q

# register = template.Library()

# @register.simple_tag()
# def get_profile_photo(email):
#     try:
#         user = CustomUser.objects.get(email=email)
#         try:
#             photos = Photo.objects.filter(Q(user=user) & Q(position=1))
#             if photos:
#                 profile_photo  = photos.first()
#                 return profile_photo.image.url
#         except Photo.DoesNotExist:
#             pos_list = [1, 2, 3, 4]
#             photos = Photo.objects.filter(
#                             Q(user=user) & Q(position__in=pos_list)
#                             ).order_by('position')
#             if photos:
#                 profile_photo = photos.first()
#                 return profile_photo.image.url
#     except CustomUser.DoesNotExist:
#         pass
#     return ""
