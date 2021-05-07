from django.shortcuts import render
from django.views.generic.base import View

from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from hobo_user.models import HoboPaymentsDetails, IndiePaymentDetails, \
    ProPaymentDetails, CompanyPaymentDetails

# Create your views here.


class IsSuperUser(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class GetMembershipFeeDetailsAPI(APIView):
    """
    API for superuser to get the membership fee details
    """
    permission_classes = (IsSuperUser,)

    def get(self, request, *args, **kwargs):
        final_result = {"monthly_hobo": "", "monthly_indie": "",
                        "monthly_pro": "", "monthly_company": "",
                        "annual_hobo": "", "annual_indie": "",
                        "annual_pro": "", "annual_company": ""
                        }
        try:
            hobo_details_dict = HoboPaymentsDetails.objects.first().__dict__
            final_result['monthly_hobo'] = hobo_details_dict[
                'monthly_amount']
            final_result['annual_hobo'] = hobo_details_dict[
                'annual_amount']
        except AttributeError:
            final_result['monthly_hobo'] = ""
            final_result['annual_hobo'] = ""

        try:
            indie_details_dict = IndiePaymentDetails.objects.first().__dict__
            final_result['monthly_indie'] = indie_details_dict[
                'monthly_amount']
            final_result['annual_indie'] = indie_details_dict[
                'annual_amount']
        except AttributeError:
            final_result['monthly_indie'] = ""
            final_result['annual_indie'] = ""

        try:
            pro_details_dict = ProPaymentDetails.objects.first().__dict__
            final_result['monthly_pro'] = pro_details_dict[
                'monthly_amount']
            final_result['annual_pro'] = pro_details_dict[
                'annual_amount']
        except AttributeError:
            final_result['monthly_pro'] = ""
            final_result['annual_pro'] = ""

        try:
            company_details_dict = CompanyPaymentDetails.objects.first().__dict__
            final_result['monthly_company'] = company_details_dict[
                'monthly_amount']
            final_result['annual_company'] = company_details_dict[
                'annual_amount']
        except AttributeError:
            final_result['monthly_company'] = ""
            final_result['annual_company'] = ""
        return Response(final_result, status=status.HTTP_200_OK)


class UpdateMembershipFeeAPI(APIView):
    """
    API for superuser to update the membership fee details
    """
    permission_classes = (IsSuperUser,)

    def put(self, request, format=None):
        data = request.data
        final_result = {"monthly_hobo": "", "monthly_indie": "",
                        "monthly_pro": "", "monthly_company": "",
                        "annual_hobo": "", "annual_indie": "",
                        "annual_pro": "", "annual_company": ""
                        }

        try:
            HoboPaymentsDetails.objects.first().__dict__
            if data['monthly_hobo'] == "":
                final_result['monthly_hobo'] = ""
            else:
                HoboPaymentsDetails.objects.all().update(
                    monthly_amount=float(data['monthly_hobo']))
                final_result['monthly_hobo'] = HoboPaymentsDetails.objects.first().__dict__['monthly_amount']
            if data['annual_hobo'] == "":
                final_result['annual_hobo'] = ""
            else:
                HoboPaymentsDetails.objects.all().update(
                    annual_amount=float(data['annual_hobo']))
                final_result['annual_hobo'] = HoboPaymentsDetails.objects.first().__dict__['annual_amount']
        except AttributeError:
            return Response(
                {"status": "failure",
                 "message": "no entry in HoboPaymentsDetails model to edit"
                 }, status=status.HTTP_204_NO_CONTENT)

        try:
            IndiePaymentDetails.objects.first().__dict__
            if data['monthly_indie'] == "":
                final_result['monthly_indie'] = ""
            else:
                IndiePaymentDetails.objects.all().update(
                    monthly_amount=float(data['monthly_indie']))
                final_result['monthly_indie'] = IndiePaymentDetails.objects.first().__dict__['monthly_amount']
            if data['annual_indie'] == "":
                final_result['annual_indie'] = ""
            else:
                IndiePaymentDetails.objects.all().update(
                    annual_amount=float(data['annual_indie']))
                final_result['annual_indie'] = IndiePaymentDetails.objects.first().__dict__['annual_amount']
        except AttributeError:
            return Response(
                {"status": "failure",
                 "message": "no entry in IndiePaymentDetails model to edit"
                 }, status=status.HTTP_204_NO_CONTENT)

        try:
            ProPaymentDetails.objects.first().__dict__
            if data['monthly_pro'] == "":
                final_result['monthly_pro'] = ""
            else:
                ProPaymentDetails.objects.all().update(
                    monthly_amount=float(data['monthly_pro']))
                final_result['monthly_pro'] = ProPaymentDetails.objects.first().__dict__['monthly_amount']
            if data['annual_pro'] == "":
                final_result['annual_pro'] = ""
            else:
                ProPaymentDetails.objects.all().update(
                    annual_amount=float(data['annual_pro']))
                final_result['annual_pro'] = ProPaymentDetails.objects.first().__dict__['annual_amount']
        except AttributeError:
            return Response(
                {"status": "failure",
                 "message": "no entry in ProPaymentDetails model to edit"
                 }, status=status.HTTP_204_NO_CONTENT)

        try:
            CompanyPaymentDetails.objects.first().__dict__
            if data['monthly_company'] == "":
                final_result['monthly_company'] = ""
            else:
                CompanyPaymentDetails.objects.all().update(
                    monthly_amount=float(data['monthly_company']))
                final_result['monthly_company'] = CompanyPaymentDetails.objects.first().__dict__['monthly_amount']
            if data['annual_company'] == "":
                final_result['annual_company'] = ""
            else:
                CompanyPaymentDetails.objects.all().update(
                    annual_amount=float(data['annual_company']))
                final_result['annual_company'] = CompanyPaymentDetails.objects.first().__dict__['annual_amount']
        except AttributeError:
            return Response(
                {"status": "failure",
                 "message": "no entry in CompanyPaymentDetails model to edit"
                 }, status=status.HTTP_204_NO_CONTENT)
        return Response(final_result, status=status.HTTP_200_OK)


class PaymentAdmin(View):

    def get(self, request, *args, **kwargs):
        context = {'message': 'Hello Django!'}
        return render(request, 'payment/payment_admin.html', context=context)
