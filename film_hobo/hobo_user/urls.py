from django.urls import path

from rest_auth.views import LoginView

from .views import CustomUserSignupHobo, CustomUserLogin, CustomUserLogout, \
                   CustomUserList, CustomUserDetail, HomePage, \
                   ExtendedRegisterView, ExtendedLoginView, \
                   ExtendedLogoutView, ChooseMembershipPage, \
                   CustomUserSignupCompany, SendEmailVerificationView, \
                   EmailVerificationStatusView, ExtendedRegisterCompanyView, \
                   ExtendedRegisterIndieView, CustomUserSignupProView, \
                   CustomUserSignupIndieView, ExtendedRegisterProView, \
                   SelectPaymentPlanIndieView, PaymentPlanAPI, \
                   SelectPaymentPlanProView, IndiePaymentDetailsAPI


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
    # web-view endpoints
    path('user_home/', HomePage.as_view(), name='user_home'),
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
]
