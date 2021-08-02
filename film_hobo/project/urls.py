from django.urls import path
from .views import ProjectVideoPlayerView, RateUserSkillsAPI, \
     GetMembershipChangeNotificationAjaxView, SingleFilmProjectView, \
     SaveProjectVideoUrlAPI, SaveVideoUploadTypeAjaxView, \
     CharacterCreateAPIView, CharacterUpdateAPIView, AddCharactersView, \
     AddSidesAjaxView, EditCharactersView, AddProjectSidesLastDateAPIView, \
     AddSidesView, SidesCreateAPIView, CastApplyAuditionView, getpdf, \
     SubmitAuditionAPI, AuditionListView, EditSidesView, AddProjectVideoView, \
     PostProjectVideoAPI, ScriptPasswordCheckAPI, CastAuditionPasswordCheckAPI, \
     TeamSelectPasswordCheckAPI, SaveProjectLoglineAPI, ListProjectTrackersAPI, \
     TrackProjectAPI

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
     path('edit-sides/<int:id>/', EditSidesView.as_view(),
          name='edit-sides'),
     path('add-sides-api/', SidesCreateAPIView.as_view(),
          name='add-sides-api'),
     path('cast-apply-audition/<int:id>/', CastApplyAuditionView.as_view(),
          name='cast-apply-audition'),
     path('submit-audition-api/', SubmitAuditionAPI.as_view(),
          name='submit-audition-api'),
     path('pdf/<int:id>/', getpdf, name='pdf'),
     path('audition-list/<int:id>/', AuditionListView.as_view(),
          name='audition-list'),
     path('add-project-video/<int:id>/', AddProjectVideoView.as_view(),
          name='add-project-video'),
     path('post-project-video/', PostProjectVideoAPI.as_view(),
          name='post-project-video'),
     path('script-password-check/', ScriptPasswordCheckAPI.as_view(),
          name='script-password-check'),
     path('cast-audition-password-check/', CastAuditionPasswordCheckAPI.as_view(),
          name='cast-audition-password-check'),
     path('team-select-password-check/', TeamSelectPasswordCheckAPI.as_view(),
          name='team-select-password-check'),
     path('save-project-logline/', SaveProjectLoglineAPI.as_view(),
          name='save-project-logline'),
     path('list-project-trackers-api/', ListProjectTrackersAPI.as_view(),
          name='list-project-trackers-api'),
     path('track-project-api/', TrackProjectAPI.as_view(),
          name='track-project-api'),
    ]
