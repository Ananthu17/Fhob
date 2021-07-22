from django.urls import path
from .views import ProjectVideoPlayerView, RateUserSkillsAPI, \
     GetMembershipChangeNotificationAjaxView, SingleFilmProjectView, \
     SaveProjectVideoUrlAPI, SaveVideoUploadTypeAjaxView, \
     CharacterCreateAPIView, CharacterUpdateAPIView, AddCharactersView, \
     AddSidesAjaxView, EditCharactersView, AddProjectSidesLastDateAPIView, \
     AddSidesView, SidesCreateAPIView, CastApplyAuditionView, getpdf

urlpatterns = [
     path('video/<int:id>/', ProjectVideoPlayerView.as_view(), name='video'),
     path('rate-user-api/', RateUserSkillsAPI.as_view(),
          name='rate-user-api'),
     path('get-membership-change-notification-html/',
          GetMembershipChangeNotificationAjaxView.as_view(),
          name='get-membership-change-notification-html'),
     path('single-film-project/<int:id>/', SingleFilmProjectView.as_view(),
          name='single-film-project'),
     path('save-project-video-url-api/', SaveProjectVideoUrlAPI.as_view(),
          name='save-project-video-url-api'),
     path('save-video-upload-type/', SaveVideoUploadTypeAjaxView.as_view(),
          name='save-video-upload-type'),
     path('charater/create/', CharacterCreateAPIView.as_view(),
          name='create-character'),
     path('charater/update/<int:id>/', CharacterUpdateAPIView.as_view(),
          name='update-character'),
     path('add-characters/<int:id>/', AddCharactersView.as_view(),
          name='add-characters'),
     path('add-sides-form/', AddSidesAjaxView.as_view(),
          name='add-sides-form'),
     path('edit-characters/<int:id>/', EditCharactersView.as_view(),
          name='edit-characters'),
     path('add-video-submit-last-date/',
          AddProjectSidesLastDateAPIView.as_view(),
          name='add-video-submit-last-date'),
     path('add-sides/<int:id>/', AddSidesView.as_view(),
          name='add-sides'),
     path('add-sides-api/', SidesCreateAPIView.as_view(),
          name='add-sides-api'),
     path('cast-apply-audition/<int:id>/', CastApplyAuditionView.as_view(),
          name='cast-apply-audition'),
     path('pdf/<int:id>/', getpdf, name='pdf'),
    ]
