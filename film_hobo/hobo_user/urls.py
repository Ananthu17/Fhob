from django.urls import path

from rest_auth.views import LoginView


from .views import CustomUserSignupHobo, CustomUserLogin, CustomUserList, \
                   CustomUserDetail, HomePage, ExtendedRegisterView, \
                   ExtendedLoginView, ExtendedLogoutView, ChooseMembershipPage, \
                   CustomUserSignupIndieView, CustomUserSignupCompany, \
                   ExtendedRegisterIndieView, SendEmailVerificationView, \
                   EmailVerificationStatusView, CustomUserSignupProView, \
                   ExtendedRegisterProView, SelectPaymentPlanIndieView, \
                   PaymentPlanAPI, SelectPaymentPlanProView, \
                   IndiePaymentDetailsAPI, ProPaymentDetailsAPI, \
                   PaymentProView, PaymentIndieView, CheckPromoCodeAPI, \
                   SettingsView, CustomUserLogout, ExtendedRegisterCompanyView, \
                   ChangePasswordAPI, DisableAccountAPI, EnableAccountAPI, \
                   EnableAccountView, BlockMembersAPI, UnBlockMembersAPI, \
                   PaymentCompanyView, ForgotPasswordView, \
                   SelectPaymentPlanCompanyView, CompanyPaymentDetailsAPI, \
                   ForgotPasswordAPI, PasswordResetConfirmView, SettingsAPI, \
                   PasswordResetTemplateView, GetUnblockedMembersAPI, \
                   GetUnblockedMembersAjaxView, PersonalDetailsAPI, \
                   PersonalDetailsView

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

]
