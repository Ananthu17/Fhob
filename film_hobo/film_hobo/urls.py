"""film_hobo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from hobo_user.views import ExtendedSignupVerify, PasswordResetConfirmView

from rest_framework_simplejwt import views as jwt_views
from initial_user.views import InitialUserDetailSavePage

urlpatterns = [
    path('', InitialUserDetailSavePage.as_view(),
         name='landing_home'),
    path('admin/', admin.site.urls),
    path('initial_user/', include('initial_user.urls')),
    path('payment/', include('payment.urls')),
    path('hobo_user/', include('hobo_user.urls')),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(),
         name='token_refresh'),
    path('rest-auth/', include('rest_auth.urls')),
    path('rest-auth/registration/', include('rest_auth.registration.urls')),
    path('api/accounts/', include('authemail.urls')),
    path('signup/verify/', ExtendedSignupVerify.as_view(),
         name='authemail-signup-verify'),
    path('password-reset-confirm/<str:uidb64>/<str:token>',
         PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
