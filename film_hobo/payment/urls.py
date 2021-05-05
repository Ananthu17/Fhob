from django.urls import path

from .views import UpdateMembershipFeeAPI

app_name = "payment"

urlpatterns = [
    # api-view endpoints
    path('update_membership_api/', UpdateMembershipFeeAPI.as_view(),
         name='update_membership_api'),
    # web-view endpoints
]
