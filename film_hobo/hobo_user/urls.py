from django.urls import path


from .views import CustomUserSignupHobo, CustomUserLogin, CustomUserList, \
                   CustomUserDetail, HomePage, ExtendedRegisterView, \
                   ExtendedLoginView, ExtendedLogoutView, ChooseMembershipPage, \
                   CustomUserSignupIndieView, CustomUserSignupCompany, \
                   ExtendedRegisterIndieView, SendEmailVerificationView, \
                   EmailVerificationStatusView, CustomUserSignupProView, \
                   ExtendedRegisterProView


app_name = "hobo_user"

urlpatterns = [
    path('registration/', ExtendedRegisterView.as_view(),
         name='user_register'),
    path('registration_indie/', ExtendedRegisterIndieView.as_view(),
         name='user_register_indie'),
    path('registration_pro/', ExtendedRegisterProView.as_view(),
         name='user_register_pro'),
    path('user_home/', HomePage.as_view(), name='user_home'),
    path('signup_hobo/', CustomUserSignupHobo.as_view(), name="signup_hobo"),
    path('signup_company/', CustomUserSignupCompany.as_view(),
         name="signup_company"),
    path('login/', CustomUserLogin.as_view(), name="login"),
    path('user_list/', CustomUserList.as_view(), name="user_list"),
    path('user_detail/', CustomUserDetail.as_view(), name="user_detail"),
    path('authentication/', ExtendedLoginView.as_view(),
         name='user_login'),
    path('logout/', ExtendedLogoutView.as_view(),
         name='user_logout'),
    path('choose-membership/', ChooseMembershipPage.as_view(),
         name='choose-membership'),
    path('signup_pro/', CustomUserSignupProView.as_view(),
         name='signup_pro'),
    path('signup_indie/', CustomUserSignupIndieView.as_view(),
         name='signup_indie'),
    path('email_verification/', SendEmailVerificationView.as_view(),
         name='email_verification'),
    path('email_verification_status/', EmailVerificationStatusView.as_view(),
         name='email_verification_status'),

]
