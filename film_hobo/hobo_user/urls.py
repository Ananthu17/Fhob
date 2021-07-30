from django.urls import path

from rest_auth.views import LoginView

from .views import CustomUserSignupHobo, CustomUserLogin, CustomUserList, \
                   CustomUserDetail, HomePage, ExtendedRegisterView, \
                   ExtendedLogoutView, \
                   ChooseMembershipPage, CustomUserSignupIndieView, \
                   CustomUserSignupCompany, \
                   ExtendedRegisterIndieView, SendEmailVerificationView, \
                   EmailVerificationStatusView, CustomUserSignupProView, \
                   ExtendedRegisterProView, SelectPaymentPlanIndieView, \
                   PaymentPlanAPI, SelectPaymentPlanProView, \
                   IndiePaymentDetailsAPI, ProPaymentDetailsAPI, \
                   PaymentProView, PaymentIndieView, CheckPromoCodeAPI, \
                   SettingsView, CustomUserLogout, \
                   ExtendedRegisterCompanyView, \
                   ChangePasswordAPI, DisableAccountAPI, EnableAccountAPI, \
                   EnableAccountView, BlockMembersAPI, UnBlockMembersAPI, \
                   PaymentCompanyView, ForgotPasswordView, \
                   SelectPaymentPlanCompanyView, CompanyPaymentDetailsAPI, \
                   ForgotPasswordAPI, SettingsAPI, \
                   PasswordResetTemplateView, GetUnblockedMembersAPI, \
                   GetUnblockedMembersAjaxView, PersonalDetailsAPI, \
                   PersonalDetailsView, HowTo, \
                   UserProfileAPI, UserProfileView, \
                   AddCoworkerAPI, RemoveCoworkerAPI, \
                   MemberProfileView, AddAgentManagerAPI, \
                   AddNewAgentFormAjaxView, RemoveAgentManagerAPI, \
                   FriendsAndFollowersView, TrackUserAPI, GetAgentManagerAPI, \
                   GetSettingsAPI, EditAgentManagerAPI, EditCoworkerAPI, \
                   UnTrackUserAPI, ChangePhotoPositionAPI, SwapImageAjaxView, \
                   UploadImageView, UploadImageAPI, GetNotificationAPI, \
                   GetTrackingNotificationAjaxView, \
                   GetAllNotificationAjaxView, \
                   ChangeNotificationStatusAPI, ProductionCompanyProfileView, \
                   ProductionCompanyProfileAPI, EditProductionCompanyView, \
                   AttachCoworkerAjaxView, AddUserInterestAjaxView, \
                   AddUserInterestView, AddUserInterestAPI, \
                   EditAgencyManagementCompanyView, CompanyClientAPI, \
                   AgencyManagementCompanyProfileAPI, RemoveClientAPI, \
                   AgencyManagementCompanyProfileView, SendFriendRequestAPI, \
                   AcceptFriendRequestAPI, ListFriendRequestAPI, \
                   ListAllFriendsAPI, DeleteFriendRequestAPI, \
                   UnFriendUserAPI, \
                   GetFriendRequestNotificationAjaxView, \
                   CancelFriendRequestAPI, \
                   GetFriendRequestAcceptNotificationAjaxView, \
                   FeedbackAPIView, FeedbackWebView, \
                   AddGroupAPI, RemoveFriendGroupAPI, \
                   AddFriendToGroupAPI, UpdateFriendGroupAjaxView, \
                   FilterFriendByGroupAjaxView, \
                   ProjectAPIView, ProjectCreateAPIView, \
                   ProjectUpdateAPIView, ProjectDeleteAPIView, \
                   TeamAPIView, TeamCreateAPIView, TeamUpdateAPIView, \
                   TeamDeleteAPIView, \
                   GetProfileRatingNotificationAjaxView, \
                   EditUserInterestAPI, VideoRatingView, ProjectView, \
                   FindVideoRatingAPI, VideoListAPI, \
                   CreateProjectView, ScreeningProjectDeatilView, \
                   UserHomeProjectInvite, ScreeningProjectDeatilInviteView, \
                   GetScreeningProjectInviteNotificationAjaxView

app_name = "hobo_user"

urlpatterns = [
    # api-view endpoints
    path('registration/', ExtendedRegisterView.as_view(),
         name='user_register'),
    path('registration_company/', ExtendedRegisterCompanyView.as_view(),
         name='user_register_company'),
    path('registration_indie/', ExtendedRegisterIndieView.as_view(),
         name='user_register_indie'),
    path('registration_pro/', ExtendedRegisterProView.as_view(),
         name='user_register_pro'),
    path('email_verification/', SendEmailVerificationView.as_view(),
         name='email_verification'),
    path('email_verification_status/', EmailVerificationStatusView.as_view(),
         name='email_verification_status'),
    path('select-payment-plan-api/', PaymentPlanAPI.as_view(),
         name='select-payment-plan-api'),
    path('indie_payment_details_api/', IndiePaymentDetailsAPI.as_view(),
         name='indie_payment_details_api'),
    path('login/', LoginView.as_view(),
         name='login'),
    path('logout/', ExtendedLogoutView.as_view(),
         name='logout'),
    path('pro_payment_details_api/', ProPaymentDetailsAPI.as_view(),
         name='pro_payment_details_api'),
    path('company_payment_details_api/', CompanyPaymentDetailsAPI.as_view(),
         name='company_payment_details_api'),
    path('check-promocode-api/', CheckPromoCodeAPI.as_view(),
         name='check-promocode-api'),
    path('change-password-api/', ChangePasswordAPI.as_view(),
         name='change-password-api'),
    path('disable-account-api/', DisableAccountAPI.as_view(),
         name='disabled-account-api'),
    path('enable-account-api/', EnableAccountAPI.as_view(),
         name='enable-account-api'),
    path('block-members-api/', BlockMembersAPI.as_view(),
         name='block-members-api'),
    path('unblock-members-api/', UnBlockMembersAPI.as_view(),
         name='unblock-members-api'),
    path('forgot-password-api/', ForgotPasswordAPI.as_view(),
         name='forgot-password-api'),
    path('update-settings-api/', SettingsAPI.as_view(),
         name='update-settings-api'),
    path('get-all-unblocked-members-api/',
         GetUnblockedMembersAPI.as_view(),
         name='get-all-unblocked-members-api'),
    path('personal-details-api/',
         PersonalDetailsAPI.as_view(),
         name='personal-details-api'),
    path('profile-api/', UserProfileAPI.as_view(),
         name='profile-api'),
    path('production-company-profile-api/',
         ProductionCompanyProfileAPI.as_view(),
         name='production-company-profile-api'),
    path('agency-management-company-profile-api/',
         AgencyManagementCompanyProfileAPI.as_view(),
         name='agency-management-company-profile-api'),
    path('add-coworker-api/', AddCoworkerAPI.as_view(),
         name='add-coworker-api'),
    path('edit-coworker-api/', EditCoworkerAPI.as_view(),
         name='edit-coworker-api'),
    path('add-agent-manager-api/', AddAgentManagerAPI.as_view(),
         name='add-agent-manager-api'),
    path('remove-coworker-api/', RemoveCoworkerAPI.as_view(),
         name='remove-coworker-api'),
    path('remove-client-api/', RemoveClientAPI.as_view(),
         name='remove-client-api'),
    path('remove-agent-api/', RemoveAgentManagerAPI.as_view(),
         name='remove-agent-api'),
    path('track-user-api/', TrackUserAPI.as_view(),
         name='track-user-api'),
    path('untrack-user-api/', UnTrackUserAPI.as_view(),
         name='untrack-user-api'),
    path('get-agent-manager-api/', GetAgentManagerAPI.as_view(),
         name='get-agent-manager-api'),
    path('get-user-settings-api/', GetSettingsAPI.as_view(),
         name='get-user-settings-api'),
    path('edit-agent-manager-api/', EditAgentManagerAPI.as_view(),
         name='edit-agent-manager-api'),
    path('change-photo-position-api/', ChangePhotoPositionAPI.as_view(),
         name='change-photo-position-api'),
    path('upload-image-api/', UploadImageAPI.as_view(),
         name='upload-image-api'),
    path('get-notification-api/', GetNotificationAPI.as_view(),
         name='get-notification-api'),
    path('change-notification-status-api/',
         ChangeNotificationStatusAPI.as_view(),
         name='change-notification-status-api'),
    path('add-user-interest-api/', AddUserInterestAPI.as_view(),
         name='add-user-interest-api'),
    path('edit-user-interest-api/', EditUserInterestAPI.as_view(),
         name='edit-user-interest-api'),
    path('company-client-api/', CompanyClientAPI.as_view(),
         name='company-client-api'),
    path('send-friend-request-api/', SendFriendRequestAPI.as_view(),
         name='send-friend-request-api'),
    path('accept-friend-request-api/', AcceptFriendRequestAPI.as_view(),
         name='accept-friend-request-api'),
    path('list-friend-requests-api/', ListFriendRequestAPI.as_view(),
         name='list-friend-requests-api'),
    path('list-all-friend-api/', ListAllFriendsAPI.as_view(),
         name='list-all-friend-api'),
    path('cancel-friend-request-api/', CancelFriendRequestAPI.as_view(),
         name='cancel-friend-request-api'),
    path('delete-friend-request-api/', DeleteFriendRequestAPI.as_view(),
         name='delete-friend-request-api'),
    path('unfriend-user-api/', UnFriendUserAPI.as_view(),
         name='unfriend-user-api'),
    path('add-group-api/', AddGroupAPI.as_view(),
         name='add-group-api'),
    path('add-friend-to-group-api/', AddFriendToGroupAPI.as_view(),
         name='add-friend-to-group-api'),
    path('remove-friend-group-api/', RemoveFriendGroupAPI.as_view(),
         name='remove-friend-group-api'),
    path('feedback-api/', FeedbackAPIView.as_view(), name='feedback-api'),


    # web-view endpoints
    path('how_to/', HowTo.as_view(), name='how_to'),
    path('user_home/', HomePage.as_view(), name='user_home'),
    path('user_home/<int:id>/',
         ScreeningProjectDeatilView.as_view(),
         name='projects_detail'),
    path('user_home/invite/',
         ScreeningProjectDeatilInviteView.as_view(),
         name='projects_detail_invite'),
    path('user_home/project_invite/<int:id>/',
         UserHomeProjectInvite.as_view(),
         name='user_home_project_invite'),
    path('signup_hobo/', CustomUserSignupHobo.as_view(), name="signup_hobo"),
    path('signup_company/', CustomUserSignupCompany.as_view(),
         name="signup_company"),
    path('user_login/', CustomUserLogin.as_view(), name="user_login"),
    path('user_logout/', CustomUserLogout.as_view(), name="user_logout"),
    path('user_list/', CustomUserList.as_view(), name="user_list"),
    path('user_detail/', CustomUserDetail.as_view(), name="user_detail"),
    path('choose-membership/', ChooseMembershipPage.as_view(),
         name='choose-membership'),
    path('signup_pro/', CustomUserSignupProView.as_view(),
         name='signup_pro'),
    path('signup_indie/', CustomUserSignupIndieView.as_view(),
         name='signup_indie'),
    path('payment_plan_indie/', SelectPaymentPlanIndieView.as_view(),
         name='payment_plan_indie'),
    path('payment_plan_pro/', SelectPaymentPlanProView.as_view(),
         name='payment_plan_pro'),
    path('payment_plan_company/', SelectPaymentPlanCompanyView.as_view(),
         name='payment_plan_company'),
    path('payment_pro/', PaymentProView.as_view(),
         name='payment_pro'),
    path('payment_indie/', PaymentIndieView.as_view(),
         name='payment_indie'),
    path('payment_company/', PaymentCompanyView.as_view(),
         name='payment_company'),
    path('settings/', SettingsView.as_view(),
         name='settings'),
    path('enable-account/', EnableAccountView.as_view(),
         name='enable-account'),
    path('forgot-password/', ForgotPasswordView.as_view(),
         name='forgot-password'),
    path('password-reset/', PasswordResetTemplateView.as_view(),
         name='password-reset'),
    path('get-unblocked-members/', GetUnblockedMembersAjaxView.as_view(),
         name='get-unblocked-members'),
    path('personal-details/', PersonalDetailsView.as_view(),
         name='personal-details'),
    path('edit-profile/', UserProfileView.as_view(),
         name='edit-profile'),
    path('edit-production-company-profile/',
         EditProductionCompanyView.as_view(),
         name='edit-production-company-profile'),
    path('add-new-agent-form/', AddNewAgentFormAjaxView.as_view(),
         name='add-new-agent-form'),
    path('profile/<int:id>/', MemberProfileView.as_view(),
         name='profile'),
    path('production-company-profile/<int:id>/',
         ProductionCompanyProfileView.as_view(),
         name='production-company-profile'),
    path('agency-management-company-profile/<int:id>/',
         AgencyManagementCompanyProfileView.as_view(),
         name='agency-management-company-profile'),
    path('friends-and-followers/', FriendsAndFollowersView.as_view(),
         name='friends-and-followers'),
    path('swap-image-position/', SwapImageAjaxView.as_view(),
         name='swap-image-position'),
    path('upload-image/', UploadImageView.as_view(),
         name='upload-image'),
    path('get-tracking-notification-html/',
         GetTrackingNotificationAjaxView.as_view(),
         name='get-tracking-notification-html'),
    path('get-friendrequest-notification-html/',
         GetFriendRequestNotificationAjaxView.as_view(),
         name='get-friendrequest-notification-html'),
    path('get-friendrequest-accept-notification-html/',
         GetFriendRequestAcceptNotificationAjaxView.as_view(),
         name='get-friendrequest-accept-notification-html'),
    path('get-all-notification-html/', GetAllNotificationAjaxView.as_view(),
         name='get-all-notification-html'),
    path('attach-coworker/', AttachCoworkerAjaxView.as_view(),
         name='attach-coworker'),
    path('add-user-interest-form/', AddUserInterestAjaxView.as_view(),
         name='add-user-interest-form'),
    path('add-user-interest/', AddUserInterestView.as_view(),
         name='add-user-interest'),
    path('edit-agency-management-company-profile/',
         EditAgencyManagementCompanyView.as_view(),
         name='edit-agency-management-company-profile'),
    path('update-friend-groups/',
         UpdateFriendGroupAjaxView.as_view(),
         name='update-friend-groups'),
    path('filter-friend-by-groups/', FilterFriendByGroupAjaxView.as_view(),
         name='filter-friend-by-groups'),
    path('feedback/',
         FeedbackWebView.as_view(),
         name='feedback-web'),

    path('projects/', ProjectAPIView.as_view(),
         name='project-list'),
    path('projects/create/', ProjectCreateAPIView.as_view(),
         name='create-project'),
    path('projects/delete/<id>', ProjectDeleteAPIView.as_view(),
         name='delete-project'),
    path('projects/update/<id>', ProjectUpdateAPIView.as_view(),
         name='delete-project'),
    path('teams/', TeamAPIView.as_view(),
         name='team-list'),
    path('teams/create/', TeamCreateAPIView.as_view(),
         name='create-team'),
    path('teams/delete/<id>', TeamDeleteAPIView.as_view(),
         name='delete-team'),
    path('teams/update/<id>', TeamUpdateAPIView.as_view(),
         name='delete-project'),
    path('get-profile-rating-notification-html/',
         GetProfileRatingNotificationAjaxView.as_view(),
         name='get-profile-rating-notification-html'),
    path('get-screeing-project-notification-html/',
         GetScreeningProjectInviteNotificationAjaxView.as_view(),
         name='get-screeing-project-notification-html'),
    # path('projects/rating', UserRatingAPI.as_view(),
    #      name="rate-api"),
    # path('projects/search/',  ProjectSearchView.as_view(),
    #      name="project-search"),
    path('video/rate/',  VideoRatingView.as_view(),
         name="videorate-api"),
    path('video/find-rating/<id>', FindVideoRatingAPI.as_view(),
         name="find-videorating"),
    path('video/top-rated',  VideoListAPI.as_view(),
         name="top-rated-videos"),
    path('projectview/', ProjectView.as_view(),
         name='projects'),
    path('projectview/create/', CreateProjectView.as_view(),
         name='new_project')
]
