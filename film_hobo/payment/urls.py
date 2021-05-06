from django.urls import path

from .views import GetMembershipFeeDetailsAPI, UpdateMembershipFeeAPI

app_name = "payment"

urlpatterns = [
    # api-view endpoints
    path('get_membership_fee_detail/', GetMembershipFeeDetailsAPI.as_view(),
         name='update_membership'),
    path('update_membership_fee/', UpdateMembershipFeeAPI.as_view(),
         name='update_membership'),
    # web-view endpoints
]
