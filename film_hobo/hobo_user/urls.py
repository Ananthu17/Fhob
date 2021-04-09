from django.urls import path


from .views import CustomUserSignupHobo, CustomUserLogin, CustomUserList, \
                   CustomUserDetail, HomePage, ExtendedRegisterView

app_name = "hobo_user"

urlpatterns = [
    path('registration/', ExtendedRegisterView.as_view(),
         name='user_register'),
    path('user_home/', HomePage.as_view(), name='user_home'),
    path('signup_hobo/', CustomUserSignupHobo.as_view(), name="signup_hobo"),
    path('login/', CustomUserLogin.as_view(), name="login"),
    path('user_list/', CustomUserList.as_view(), name="user_list"),
    path('user_detail/', CustomUserDetail.as_view(), name="user_detail"),
]
