from django.urls import path, include

from payment import views

from .views import GetMembershipFeeDetailsAPI, UpdateMembershipFeeAPI, \
     PaymentAdmin, AddDiscountDetailAPI, GetDiscountDetailListAPI, \
     EditDiscountDetailAPI, DeleteDiscountDetailAPI, CalculateDiscountAPI, \
     GetMembershipFeeDetailsPublicAPI, TransactionSave, GetToken, \
     CreateUserOrder, CaptureUserOrder
from .paypal import CreateOrder, CaptureOrder

app_name = "payment"

urlpatterns = [
    # api-view endpoints
    path('get_membership_fee_detail/', GetMembershipFeeDetailsAPI.as_view(),
         name='get_membership_fee_detail'),
    path('get_membership_fee_detail_public/', GetMembershipFeeDetailsPublicAPI.as_view(),
         name='get_membership_fee_detail_public'),
    path('update_membership_fee/', UpdateMembershipFeeAPI.as_view(),
         name='update_membership_fee'),
    path('add_discount_detail/', AddDiscountDetailAPI.as_view(),
         name='add_discount_detail'),
    path('get_discount_detail_list/', GetDiscountDetailListAPI.as_view(),
         name='get_discount_detail_list'),
    path('edit_discount_detail/', EditDiscountDetailAPI.as_view(),
         name='edit_discount_detail'),
    path('delete_discount_detail/<int:pk>/', DeleteDiscountDetailAPI.as_view(),
         name='delete_discount_detail'),
    path('calculate_discount/', CalculateDiscountAPI.as_view(),
         name='calculate_discount'),
    path('transaction_save/', TransactionSave.as_view(),
         name='transaction_save'),
    path('get_user_token/', GetToken.as_view(),
         name='get_user_token'),
    # web-view endpoints
    path('payment_admin', PaymentAdmin.as_view(),
         name='payment_admin'),
    # paypal endpoints
    path('paypal/', include("paypal.standard.ipn.urls")),
    path('paypal/create/', CreateUserOrder.as_view(), name="paypal-create"),
    path('paypal/<order_id>/capture/',
         CaptureUserOrder.as_view(), name="paypal-capture")
]
