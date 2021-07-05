from django.urls import path
from .views import ProjectVideoPlayerView, RateUserSkillsAPI, \
     GetMembershipChangeNotificationAjaxView

urlpatterns = [
     path('video/<int:id>', ProjectVideoPlayerView.as_view(), name='video'),
     path('rate-user-api/', RateUserSkillsAPI.as_view(),
          name='rate-user-api'),
     path('get-membership-change-notification-html/',
          GetMembershipChangeNotificationAjaxView.as_view(),
          name='get-membership-change-notification-html'),
    ]
