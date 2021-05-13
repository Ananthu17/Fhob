from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views.generic.base import View

from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from hobo_user.models import HoboPaymentsDetails, IndiePaymentDetails, \
    ProPaymentDetails, CompanyPaymentDetails, PromoCode
from .serializers import DiscountsSerializer
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
                try:
                    HoboPaymentsDetails.objects.all().update(
                        monthly_amount=float(data['monthly_hobo']))
                    final_result['monthly_hobo'] = HoboPaymentsDetails.objects.first().__dict__['monthly_amount']
                except ValueError:
                    return Response(
                        {"status": "failure",
                         "monthly_hobo": "please enter a valid number"
                         }, status=status.HTTP_400_BAD_REQUEST)

            if data['annual_hobo'] == "":
                final_result['annual_hobo'] = ""
            else:
                try:
                    HoboPaymentsDetails.objects.all().update(
                        annual_amount=float(data['annual_hobo']))
                    final_result['annual_hobo'] = HoboPaymentsDetails.objects.first().__dict__['annual_amount']
                except ValueError:
                    return Response(
                        {"status": "failure",
                         "annual_hobo": "please enter a valid number"
                         }, status=status.HTTP_400_BAD_REQUEST)
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
                try:
                    IndiePaymentDetails.objects.all().update(
                        monthly_amount=float(data['monthly_indie']))
                    final_result['monthly_indie'] = IndiePaymentDetails.objects.first().__dict__['monthly_amount']
                except ValueError:
                    return Response(
                        {"status": "failure",
                         "monthly_indie": "please enter a valid number"
                         }, status=status.HTTP_400_BAD_REQUEST)

            if data['annual_indie'] == "":
                final_result['annual_indie'] = ""
            else:
                try:
                    IndiePaymentDetails.objects.all().update(
                        annual_amount=float(data['annual_indie']))
                    final_result['annual_indie'] = IndiePaymentDetails.objects.first().__dict__['annual_amount']
                except ValueError:
                    return Response(
                        {"status": "failure",
                         "annual_indie": "please enter a valid number"
                         }, status=status.HTTP_400_BAD_REQUEST)
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
                try:
                    ProPaymentDetails.objects.all().update(
                        monthly_amount=float(data['monthly_pro']))
                    final_result['monthly_pro'] = ProPaymentDetails.objects.first().__dict__['monthly_amount']
                except ValueError:
                    return Response(
                        {"status": "failure",
                         "monthly_pro": "please enter a valid number"
                         }, status=status.HTTP_400_BAD_REQUEST)
            if data['annual_pro'] == "":
                final_result['annual_pro'] = ""
            else:
                try:
                    ProPaymentDetails.objects.all().update(
                        annual_amount=float(data['annual_pro']))
                    final_result['annual_pro'] = ProPaymentDetails.objects.first().__dict__['annual_amount']
                except ValueError:
                    return Response(
                        {"status": "failure",
                         "annual_pro": "please enter a valid number"
                         }, status=status.HTTP_400_BAD_REQUEST)
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
                try:
                    CompanyPaymentDetails.objects.all().update(
                        monthly_amount=float(data['monthly_company']))
                    final_result['monthly_company'] = CompanyPaymentDetails.objects.first().__dict__['monthly_amount']
                except ValueError:
                    return Response(
                        {"status": "failure",
                         "monthly_company": "please enter a valid number"
                         }, status=status.HTTP_400_BAD_REQUEST)
            if data['annual_company'] == "":
                final_result['annual_company'] = ""
            else:
                try:
                    CompanyPaymentDetails.objects.all().update(
                        annual_amount=float(data['annual_company']))
                    final_result['annual_company'] = CompanyPaymentDetails.objects.first().__dict__['annual_amount']
                except ValueError:
                    return Response(
                        {"status": "failure",
                         "annual_company": "please enter a valid number"
                         }, status=status.HTTP_400_BAD_REQUEST)
        except AttributeError:
            return Response(
                {"status": "failure",
                 "message": "no entry in CompanyPaymentDetails model to edit"
                 }, status=status.HTTP_204_NO_CONTENT)
        return Response(final_result, status=status.HTTP_200_OK)


class PaymentAdmin(View):
    """
    Web URL View to load the admin payment page
    """
    def get(self, request, *args, **kwargs):
        return render(request, 'payment/payment_admin.html')


class AddDiscountDetailAPI(APIView):
    """
    API for superuser to add a discount with details
    """
    permission_classes = (IsSuperUser,)

    def post(self, request, format=None):
        data = request.data
        midnight = 'T00:00:00Z'
        data['valid_from'] = data['valid_from'] + midnight
        data['valid_to'] = data['valid_to'] + midnight
        serializer = DiscountsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success",
                             "message": "new promocode record added"})
        else:
            return Response(serializer.errors)


class GetDiscountDetailListAPI(APIView):
    """
    API for superuser to get the discount details
    """
    permission_classes = (IsSuperUser,)

    def get(self, request, *args, **kwargs):
        promocodes = PromoCode.objects.all()
        serializer = DiscountsSerializer(promocodes, many=True)
        return Response(serializer.data)


class EditDiscountDetailAPI(APIView):
    """
    API for superuser to edit a discount details
    """
    permission_classes = (IsSuperUser,)

    def put(self, request, *args, **kwargs):
        try:
            data = request.data
            code = request.data['promo_code']
            PromoCode.objects.get(promo_code=code)
            midnight = 'T00:00:00Z'
            data['valid_from'] = data['valid_from'] + midnight
            data['valid_to'] = data['valid_to'] + midnight
            serializer = DiscountsSerializer(data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "success",
                                "message": "promocode record updated successfully"})
            else:
                return Response(serializer.errors)
        except ObjectDoesNotExist:
            return Response(
                {"status": "promocode record not found"},
                status=status.HTTP_404_NOT_FOUND)


class DeleteDiscountDetailAPI(APIView):
    """
    API for superuser to delete a discount with details
    """
    permission_classes = (IsSuperUser,)

    def delete(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            promocode = PromoCode.objects.get(pk=pk)
            promocode.delete()
            return Response(
                {"status": "promocode record deleted"},
                status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response(
                {"status": "promocode record not found"},
                status=status.HTTP_404_NOT_FOUND)
