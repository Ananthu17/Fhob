from django.urls import path


from .views import CustomUserSignupHobo, CustomUserLogin, CustomUserList, \
                   CustomUserDetail, HomePage, ExtendedRegisterView, \
                   ExtendedLoginView, ExtendedLogoutView, ChooseMembershipPage, \
                   CustomUserSignupIndieProView, CustomUserSignupCompany, \
                   ExtendedRegisterIndieProView


app_name = "hobo_user"

urlpatterns = [
    path('registration/', ExtendedRegisterView.as_view(),
         name='user_register'),
    path('registration_indie_pro/', ExtendedRegisterIndieProView.as_view(),
         name='user_register_indie_pro'),
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
    path('signup_indie_pro/', CustomUserSignupIndieProView.as_view(),
         name='signup_indie_pro'),
]
