from django.urls import path
from .views import ProjectVideoPlayerView, RateUserSkillsAPI, \
     GetMembershipChangeNotificationAjaxView, SingleFilmProjectView, \
     SaveProjectVideoUrlAPI, SaveVideoUploadTypeAjaxView

urlpatterns = [
     path('video/<int:id>/', ProjectVideoPlayerView.as_view(), name='video'),
     path('rate-user-api/', RateUserSkillsAPI.as_view(),
          name='rate-user-api'),
     path('get-membership-change-notification-html/',
          GetMembershipChangeNotificationAjaxView.as_view(),
          name='get-membership-change-notification-html'),
     path('single-film-project/<int:id>', SingleFilmProjectView.as_view(),
          name='single-film-project'),
     path('save-project-video-url-api/', SaveProjectVideoUrlAPI.as_view(),
          name='save-project-video-url-api'),
     path('save-video-upload-type/', SaveVideoUploadTypeAjaxView.as_view(),
          name='save-video-upload-type'),
    ]
