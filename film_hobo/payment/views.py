import braintree
import json
import requests

from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.generic.base import View

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from datetimerange import DateTimeRange

from film_hobo import settings
from hobo_user.models import HoboPaymentsDetails, IndiePaymentDetails, \
    ProPaymentDetails, CompanyPaymentDetails, PromoCode, CustomUser
from .models import PaymentOptions, Transaction
from .serializers import DiscountsSerializer, TransactionSerializer
# Create your views here.

from paypal.standard.forms import PayPalPaymentsForm
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, \
    OrdersCaptureRequest, OrdersGetRequest


class IsSuperUser(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class GetMembershipFeeDetailsAPI(APIView):
    """
    API for superuser to get the membership fee details
    """
    permission_classes = (IsSuperUser,)

    def get(self, request, *args, **kwargs):
        final_result = {"monthly_hobo": "", "monthly_hobo_with_tax": "",
                        "monthly_indie": "", "monthly_indie_with_tax": "",
                        "monthly_pro": "", "monthly_pro_with_tax": "",
                        "monthly_company": "", "monthly_company_with_tax": "",
                        "annual_hobo": "", "annual_hobo_with_tax": "",
                        "annual_indie": "", "annual_indie_with_tax": "",
                        "annual_pro": "", "annual_pro_with_tax": "",
                        "annual_company": "", "annual_company": "",
                        "tax": "", "free_evaluation_time": "",
                        "auto_renew": ""
                        }
        try:
            hobo_details_dict = HoboPaymentsDetails.objects.first().__dict__
            final_result['monthly_hobo'] = hobo_details_dict[
                'monthly_amount']
            final_result['monthly_hobo_with_tax'] = hobo_details_dict[
                'monthly_amount_with_tax']
            final_result['annual_hobo'] = hobo_details_dict[
                'annual_amount']
            final_result['annual_hobo_with_tax'] = hobo_details_dict[
                'annual_amount_with_tax']
        except AttributeError:
            final_result['monthly_hobo'] = ""
            final_result['monthly_hobo_with_tax'] = ""
            final_result['annual_hobo'] = ""
            final_result['annual_hobo_with_tax'] = ""

        try:
            indie_details_dict = IndiePaymentDetails.objects.first().__dict__
            final_result['monthly_indie'] = indie_details_dict[
                'monthly_amount']
            final_result['monthly_indie_with_tax'] = indie_details_dict[
                'monthly_amount_with_tax']
            final_result['annual_indie'] = indie_details_dict[
                'annual_amount']
            final_result['annual_indie_with_tax'] = indie_details_dict[
                'annual_amount_with_tax']
        except AttributeError:
            final_result['monthly_indie'] = ""
            final_result['monthly_indie_with_tax'] = ""
            final_result['annual_indie'] = ""
            final_result['annual_indie_with_tax'] = ""

        try:
            pro_details_dict = ProPaymentDetails.objects.first().__dict__
            final_result['monthly_pro'] = pro_details_dict[
                'monthly_amount']
            final_result['monthly_pro_with_tax'] = pro_details_dict[
                'monthly_amount_with_tax']
            final_result['annual_pro'] = pro_details_dict[
                'annual_amount']
            final_result['annual_pro_with_tax'] = pro_details_dict[
                'annual_amount_with_tax']
        except AttributeError:
            final_result['monthly_pro'] = ""
            final_result['monthly_pro_with_tax'] = ""
            final_result['annual_pro'] = ""
            final_result['annual_pro_with_tax'] = ""

        try:
            company_details_dict = \
                CompanyPaymentDetails.objects.first().__dict__
            final_result['monthly_company'] = company_details_dict[
                'monthly_amount']
            final_result['monthly_company_with_tax'] = company_details_dict[
                'monthly_amount_with_tax']
            final_result['annual_company'] = company_details_dict[
                'annual_amount']
            final_result['annual_company_with_tax'] = company_details_dict[
                'annual_amount_with_tax']
        except AttributeError:
            final_result['monthly_company'] = ""
            final_result['monthly_company_with_tax'] = ""
            final_result['annual_company'] = ""
            final_result['annual_company_with_tax'] = ""

        try:
            payment_options_dict = PaymentOptions.objects.first().__dict__
            final_result['tax'] = payment_options_dict[
                'tax']
            final_result['free_evaluation_time'] = payment_options_dict[
                'free_evaluation_time']
            final_result['auto_renew'] = payment_options_dict[
                'auto_renew'].lower().replace(" ", "")
        except AttributeError:
            final_result['tax'] = ""
            final_result['free_evaluation_time'] = ""
            final_result['auto_renew'] = ""

        return Response(final_result, status=status.HTTP_200_OK)


class GetMembershipFeeDetailsPublicAPI(APIView):
    """
    API for superuser to get the membership fee details
    """

    def get(self, request, *args, **kwargs):
        final_result = {"monthly_hobo": "", "monthly_hobo_with_tax": "",
                        "monthly_indie": "", "monthly_indie_with_tax": "",
                        "monthly_pro": "", "monthly_pro_with_tax": "",
                        "monthly_company": "", "monthly_company_with_tax": "",
                        "annual_hobo": "", "annual_hobo_with_tax": "",
                        "annual_indie": "", "annual_indie_with_tax": "",
                        "annual_pro": "", "annual_pro_with_tax": "",
                        "annual_company": "", "annual_company": "",
                        "tax": "", "free_evaluation_time": "",
                        "auto_renew": ""
                        }
        try:
            hobo_details_dict = HoboPaymentsDetails.objects.first().__dict__
            final_result['monthly_hobo'] = hobo_details_dict[
                'monthly_amount']
            final_result['monthly_hobo_with_tax'] = hobo_details_dict[
                'monthly_amount_with_tax']
            final_result['annual_hobo'] = hobo_details_dict[
                'annual_amount']
            final_result['annual_hobo_with_tax'] = hobo_details_dict[
                'annual_amount_with_tax']
        except AttributeError:
            final_result['monthly_hobo'] = ""
            final_result['monthly_hobo_with_tax'] = ""
            final_result['annual_hobo'] = ""
            final_result['annual_hobo_with_tax'] = ""

        try:
            indie_details_dict = IndiePaymentDetails.objects.first().__dict__
            final_result['monthly_indie'] = indie_details_dict[
                'monthly_amount']
            final_result['monthly_indie_with_tax'] = indie_details_dict[
                'monthly_amount_with_tax']
            final_result['annual_indie'] = indie_details_dict[
                'annual_amount']
            final_result['annual_indie_with_tax'] = indie_details_dict[
                'annual_amount_with_tax']
        except AttributeError:
            final_result['monthly_indie'] = ""
            final_result['monthly_indie_with_tax'] = ""
            final_result['annual_indie'] = ""
            final_result['annual_indie_with_tax'] = ""

        try:
            pro_details_dict = ProPaymentDetails.objects.first().__dict__
            final_result['monthly_pro'] = pro_details_dict[
                'monthly_amount']
            final_result['monthly_pro_with_tax'] = pro_details_dict[
                'monthly_amount_with_tax']
            final_result['annual_pro'] = pro_details_dict[
                'annual_amount']
            final_result['annual_pro_with_tax'] = pro_details_dict[
                'annual_amount_with_tax']
        except AttributeError:
            final_result['monthly_pro'] = ""
            final_result['monthly_pro_with_tax'] = ""
            final_result['annual_pro'] = ""
            final_result['annual_pro_with_tax'] = ""

        try:
            company_details_dict = \
                CompanyPaymentDetails.objects.first().__dict__
            final_result['monthly_company'] = company_details_dict[
                'monthly_amount']
            final_result['monthly_company_with_tax'] = company_details_dict[
                'monthly_amount_with_tax']
            final_result['annual_company'] = company_details_dict[
                'annual_amount']
            final_result['annual_company_with_tax'] = company_details_dict[
                'annual_amount_with_tax']
        except AttributeError:
            final_result['monthly_company'] = ""
            final_result['monthly_company_with_tax'] = ""
            final_result['annual_company'] = ""
            final_result['annual_company_with_tax'] = ""

        try:
            payment_options_dict = PaymentOptions.objects.first().__dict__
            final_result['tax'] = payment_options_dict[
                'tax']
            final_result['free_evaluation_time'] = payment_options_dict[
                'free_evaluation_time']
            final_result['auto_renew'] = payment_options_dict[
                'auto_renew'].lower().replace(" ", "")
        except AttributeError:
            final_result['tax'] = ""
            final_result['free_evaluation_time'] = ""
            final_result['auto_renew'] = ""

        return Response(final_result, status=status.HTTP_200_OK)


class UpdateMembershipFeeAPI(APIView):
    """
    API for superuser to update the membership fee details
    """
    permission_classes = (IsSuperUser,)

    def put(self, request, format=None):
        data = request.data
        final_result = {"monthly_hobo": "", "monthly_hobo_with_tax": "",
                        "monthly_indie": "", "monthly_indie_with_tax": "",
                        "monthly_pro": "", "monthly_pro_with_tax": "",
                        "monthly_company": "", "monthly_company_with_tax": "",
                        "annual_hobo": "", "annual_hobo_with_tax": "",
                        "annual_indie": "", "annual_indie_with_tax": "",
                        "annual_pro": "", "annual_pro_with_tax": "",
                        "annual_company": "", "annual_company": "",
                        "tax": "", "free_evaluation_time": "",
                        "auto_renew": ""
                        }

        try:
            HoboPaymentsDetails.objects.first().__dict__
            if data['monthly_hobo'] == "":
                final_result['monthly_hobo'] = ""
            else:
                try:
                    HoboPaymentsDetails.objects.all().update(
                        monthly_amount=float(data['monthly_hobo']))
                    final_result['monthly_hobo'] = \
                        HoboPaymentsDetails.objects.first().__dict__[
                            'monthly_amount']
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
                    final_result['annual_hobo'] = \
                        HoboPaymentsDetails.objects.first().__dict__[
                            'annual_amount']
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
                    final_result['monthly_indie'] = \
                        IndiePaymentDetails.objects.first().__dict__[
                            'monthly_amount']
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
                    final_result['annual_indie'] = \
                        IndiePaymentDetails.objects.first().__dict__[
                            'annual_amount']
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
                    final_result['monthly_pro'] = \
                        ProPaymentDetails.objects.first().__dict__[
                            'monthly_amount']
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
                    final_result['annual_pro'] = \
                        ProPaymentDetails.objects.first().__dict__[
                            'annual_amount']
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
                    final_result['monthly_company'] = \
                        CompanyPaymentDetails.objects.first().__dict__[
                            'monthly_amount']
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
                    final_result['annual_company'] = \
                        CompanyPaymentDetails.objects.first().__dict__[
                            'annual_amount']
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

        try:
            PaymentOptions.objects.first().__dict__

            try:
                float(data['tax'])
                if data['tax'] == "":
                    final_result['tax'] = \
                        PaymentOptions.objects.first().__dict__['tax']
                elif (float(data['tax']) < 0.0) or (float(data['tax']) > 100.0):
                    return Response(
                        {"status": "failure",
                         "tax": "please enter a valid number between 0 and 100"
                         }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    final_result['tax'] = float(data['tax'])
                    final_result['monthly_hobo_with_tax'] = \
                        final_result['monthly_hobo'] + \
                        (final_result['monthly_hobo'] *
                         (float(data['tax']) / 100.0))
                    final_result['monthly_indie_with_tax'] = \
                        final_result['monthly_indie'] + \
                        (final_result['monthly_indie'] *
                         (float(data['tax']) / 100.0))
                    final_result['monthly_pro_with_tax'] = \
                        final_result['monthly_pro'] + \
                        (final_result['monthly_pro'] *
                         (float(data['tax']) / 100.0))
                    final_result['monthly_company_with_tax'] = \
                        final_result['monthly_company'] + \
                        (final_result['monthly_company'] *
                         (float(data['tax']) / 100.0))
                    final_result['annual_hobo_with_tax'] = \
                        final_result['annual_hobo'] + \
                        (final_result['annual_hobo'] *
                         (float(data['tax']) / 100.0))
                    final_result['annual_indie_with_tax'] = \
                        final_result['annual_indie'] + \
                        (final_result['annual_indie'] *
                         (float(data['tax']) / 100.0))
                    final_result['annual_pro_with_tax'] = \
                        final_result['annual_pro'] + \
                        (final_result['annual_pro'] *
                         (float(data['tax']) / 100.0))
                    final_result['annual_company_with_tax'] = \
                        final_result['annual_company'] + \
                        (final_result['annual_company'] *
                         (float(data['tax']) / 100.0))
            except ValueError:
                return Response(
                        {"status": "failure",
                         "tax": "please enter a valid number"
                         }, status=status.HTTP_400_BAD_REQUEST)

            try:
                int(data['free_evaluation_time'])
                if data['free_evaluation_time'] == "":
                    final_result['free_evaluation_time'] = \
                        PaymentOptions.objects.first().__dict__[
                            'free_evaluation_time']
                elif int(data['free_evaluation_time']) == 0:
                    final_result['free_evaluation_time'] = '0'
                else:
                    final_result['free_evaluation_time'] = \
                        data['free_evaluation_time']
            except ValueError:
                return Response(
                    {"status": "failure",
                     "free_evaluation_time": "please enter a valid number"
                     }, status=status.HTTP_400_BAD_REQUEST)

            if data['auto_renew'] == "":
                final_result['auto_renew'] = \
                    PaymentOptions.objects.first().__dict__['auto_renew']
            elif data['auto_renew'].lower().replace(" ", "") == "on":
                final_result['auto_renew'] = "on"
            elif data['auto_renew'].lower().replace(" ", "") == "off":
                final_result['auto_renew'] = "off"
            else:
                return Response(
                    {"status": "failure",
                     "auto_renew": "please enter a option on/off"
                     }, status=status.HTTP_400_BAD_REQUEST)

            PaymentOptions.objects.all().update(
                tax=float(final_result['tax']),
                free_evaluation_time=final_result['free_evaluation_time'],
                auto_renew=final_result['auto_renew'])

            del final_result["auto_renew"]
            for key, value in final_result.items():
                if key == "free_evaluation_time":
                    final_result["free_evaluation_time"] = int(value)
                else:
                    final_result[key] = round(value, 2)

            HoboPaymentsDetails.objects.all().update(
                free_days=final_result['free_evaluation_time'],
                monthly_amount=float(final_result['monthly_hobo']),
                monthly_amount_with_tax=float(
                    final_result['monthly_hobo_with_tax']),
                annual_amount=float(final_result['annual_hobo']),
                annual_amount_with_tax=float(
                    final_result['annual_hobo_with_tax']),
                estimated_tax=float(final_result['tax']))
            IndiePaymentDetails.objects.all().update(
                free_days=final_result['free_evaluation_time'],
                monthly_amount=float(final_result['monthly_indie']),
                monthly_amount_with_tax=float(
                    final_result['monthly_indie_with_tax']),
                annual_amount=float(final_result['annual_indie']),
                annual_amount_with_tax=float(
                    final_result['annual_indie_with_tax']),
                estimated_tax=float(final_result['tax']))
            ProPaymentDetails.objects.all().update(
                free_days=final_result['free_evaluation_time'],
                monthly_amount=float(final_result['monthly_pro']),
                monthly_amount_with_tax=float(
                    final_result['monthly_pro_with_tax']),
                annual_amount=float(final_result['annual_pro']),
                annual_amount_with_tax=float(
                    final_result['annual_pro_with_tax']),
                estimated_tax=float(final_result['tax']))
            CompanyPaymentDetails.objects.all().update(
                free_days=final_result['free_evaluation_time'],
                monthly_amount=float(final_result['monthly_company']),
                monthly_amount_with_tax=float(
                    final_result['monthly_company_with_tax']),
                annual_amount=float(final_result['annual_company']),
                annual_amount_with_tax=float(
                    final_result['annual_company_with_tax']),
                estimated_tax=float(final_result['tax']))

        except ValueError:
            return Response(
                {"status": "failure",
                 "message": "no entry in PaymentOptions model to edit"
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
        data['user_type'] = 'ADMIN'
        serializer = DiscountsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success",
                             "message": "new promocode record added"})
        else:
            print(serializer.errors)
            return Response(serializer.errors)


class GetDiscountDetailListAPI(APIView):
    """
    API for superuser to get the discount details
    """
    permission_classes = (IsSuperUser,)

    def get(self, request, *args, **kwargs):
        promocodes = PromoCode.objects.all().order_by('-id')
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
            unique_id = request.data['id']
            promocode_instance = PromoCode.objects.get(id=unique_id)
            midnight = 'T00:00:00Z'
            data['valid_from'] = data['valid_from'] + midnight
            data['valid_to'] = data['valid_to'] + midnight
            serializer = DiscountsSerializer(promocode_instance,
                                             data=request.data, partial=True)
            if serializer.is_valid():
                serializer.update(PromoCode.objects.get(id=unique_id),
                                  request.data)
                return Response(
                    {"status": "success",
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


class CalculateDiscountAPI(APIView):
    """
    API for calculateing the discount
    """

    def post(self, request, format=None):
        try:
            data = request.data
            if data['promocode'] == '':
                return Response(
                    {"status": "enter a valid promocode"},
                    status=status.HTTP_404_NOT_FOUND)
            else:
                promocode_obj = PromoCode.objects.get(
                    promo_code=data['promocode'])
                current_date_time = timezone.now()
                time_range = DateTimeRange(
                    promocode_obj.valid_from, promocode_obj.valid_to)
                if current_date_time in time_range:
                    if promocode_obj.amount_type == 'flat_amount':
                        initial_amount = float(data['amount'])
                        promotion_amount = float(promocode_obj.amount)
                        temp_amount = initial_amount - promotion_amount
                        if temp_amount < 0:
                            final_amount = 0
                        else:
                            final_amount = temp_amount
                    else:
                        initial_amount = float(data['amount'])
                        promotion_amount = float(data['amount']) * \
                            (float(promocode_obj.amount) / 100.0)
                        temp_amount = initial_amount - promotion_amount
                        if temp_amount < 0:
                            final_amount = 0
                        else:
                            final_amount = temp_amount
                    return Response(
                        {"status": "success",
                         "promocode": data['promocode'],
                         "initial_amount": round(initial_amount, 2),
                         "promotion_amount": round(promotion_amount, 2),
                         "final_amount": round(final_amount, 2)},
                        status=status.HTTP_200_OK)
                else:
                    return Response(
                        {"status": "promocode expired"},
                        status=status.HTTP_404_NOT_FOUND)
        except ObjectDoesNotExist:
            return Response(
                {"status": "promocode does not exist"},
                status=status.HTTP_404_NOT_FOUND)


class TransactionSave(APIView):
    """
    API for saveing transaction details
    """

    def post(self, request, format=None):
        logged_user = CustomUser.objects.get(id=request.user.id)
        membership_type = logged_user.membership
        payment_plan = request.data['payment_plan']
        days_free = request.data['days_free']
        initial_amount = request.data['initial_amount']
        tax_applied = request.data['tax_applied']
        if request.data['promocodes_applied'] == "":
            promocodes_applied = None
        else:
            promocodes_applied = PromoCode.objects.get(
                promo_code=request.data['promocodes_applied'])
        if request.data['promotion_amount'] == '':
            promotion_amount = 0
        else:
            promotion_amount = float(request.data['promotion_amount'])
        final_amount = request.data['final_amount']
        transaction = Transaction.objects.create(
                                   user=logged_user,
                                   membership=membership_type,
                                   payment_plan=payment_plan,
                                   days_free=days_free,
                                   initial_amount=initial_amount,
                                   tax_applied=tax_applied,
                                   promocodes_applied=promocodes_applied,
                                   promotion_amount=promotion_amount,
                                   final_amount=final_amount)
        serializer = TransactionSerializer(transaction)
        if transaction:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                        {"status": "transaction record failure"},
                        status=status.HTTP_400_BAD_REQUEST)


class GetToken(APIView):
    """
    API for get token value
    """

    def post(self, request, format=None):
        email = request.data['email']
        try:
            custom_user = CustomUser.objects.get(email=email)
            user_token = Token.objects.get(user=custom_user.id)
            return Response(
                {"token": user_token.key}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(
                {"status": "invalid user"},
                status=status.HTTP_404_NOT_FOUND)


class CreateUserOrder(APIView):

    def post(self, request, *args, **kwargs):
        try:
            logged_user = Token.objects.get(key=request.data['token']).user
            membership_type = logged_user.membership
        except ObjectDoesNotExist:
            return Response(
                        {"status": "invalid user token"},
                        status=status.HTTP_400_BAD_REQUEST)
        payment_plan = request.data['payment_plan']
        payment_method = request.data['payment_method']
        days_free = request.data['days_free']
        initial_amount = request.data['initial_amount']
        tax_applied = request.data['tax_applied']
        if request.data['promocodes_applied'] == "":
            promocodes_applied = None
        else:
            promocodes_applied = PromoCode.objects.get(
                promo_code=request.data['promocodes_applied'])
        if request.data['promotion_amount'] == '':
            promotion_amount = 0
        else:
            promotion_amount = float(request.data['promotion_amount'])
        final_amount = request.data['final_amount']
        transaction = Transaction.objects.create(
                                   user=logged_user,
                                   membership=membership_type,
                                   payment_plan=payment_plan,
                                   payment_method=payment_method,
                                   days_free=days_free,
                                   initial_amount=initial_amount,
                                   tax_applied=tax_applied,
                                   promocodes_applied=promocodes_applied,
                                   promotion_amount=promotion_amount,
                                   final_amount=final_amount)
        if transaction:
            environment = SandboxEnvironment(
                client_id=settings.PAYPAL_CLIENT_ID,
                client_secret=settings.PAYPAL_SECRET_ID)
            client = PayPalHttpClient(environment)
            create_order = OrdersCreateRequest()

            # order
            create_order.request_body(
                {
                    "intent": "CAPTURE",
                    "application_context": {
                        "brand_name": "FILMHOBO INC",
                        "shipping_preference": "NO_SHIPPING"
                    },
                    "purchase_units": [
                        {
                            "days_free": transaction.days_free,
                            "payment_plan": transaction.payment_plan,
                            "initial_amount": transaction.initial_amount,
                            "amount": {
                                "currency_code": "USD",
                                "value": transaction.final_amount,
                                "breakdown": {
                                    "item_total": {
                                        "currency_code": "USD",
                                        "value": transaction.final_amount
                                    }
                                    },
                                },
                        }
                    ],
                }
            )

            response = client.execute(create_order)
            data = response.result.__dict__['_dict']
            Transaction.objects.filter(id=transaction.id).update(
                paypal_order_id=data['id'])
            # return JsonResponse(data)
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                        {"status": "transaction record failure"},
                        status=status.HTTP_400_BAD_REQUEST)


class CaptureUserOrder(APIView):

    def post(self, request, *args, **kwargs):
        capture_order = OrdersCaptureRequest(kwargs['order_id'])
        environment = SandboxEnvironment(
            client_id=settings.PAYPAL_CLIENT_ID,
            client_secret=settings.PAYPAL_SECRET_ID)
        client = PayPalHttpClient(environment)

        response = client.execute(capture_order)
        data = response.result.__dict__['_dict']
        if response.result.__dict__['_dict']['status'] == 'COMPLETED':
            transaction_obj = Transaction.objects.get(
                paypal_order_id=response.result.__dict__['_dict']['id']
                )
            Transaction.objects.filter(
                paypal_order_id=response.result.__dict__['_dict']['id']
                ).update(paid=True)
            CustomUser.objects.filter(
                email=transaction_obj.user.email
                ).update(registration_complete=True)
        return JsonResponse(data)


class GetOrderDetails(APIView):

    def get(self, request, *args, **kwargs):
        capture_order = OrdersGetRequest(kwargs['order_id'])
        environment = SandboxEnvironment(
            client_id=settings.PAYPAL_CLIENT_ID,
            client_secret=settings.PAYPAL_SECRET_ID)
        client = PayPalHttpClient(environment)

        response = client.execute(capture_order)
        data = response.result.__dict__['_dict']

        return JsonResponse(data)


class GetProductID(APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request, *args, **kwargs):
        data = {'paypal_product_id': settings.PRODUCT_ID}
        return JsonResponse(data)


class SubscriptionDetails(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # user_email = self.request.GET.get('email')
            # logged_user = CustomUser.objects.get(email=user_email)
            logged_user = Token.objects.get(key=request.data['token']).user
            membership_type = logged_user.membership
        except ObjectDoesNotExist:
            return Response(
                        {"status": "invalid user token"},
                        status=status.HTTP_400_BAD_REQUEST)
        payment_plan = request.data['payment_plan']
        if membership_type == 'IND':
            if payment_plan == 'monthly':
                plan_id = settings.INDIE_PAYMENT_MONTHLY
            else:
                plan_id = settings.INDIE_PAYMENT_YEARLY
        elif membership_type == 'PRO':
            if payment_plan == 'monthly':
                plan_id = settings.PRO_PAYMENT_MONTHLY
            else:
                plan_id = settings.PRO_PAYMENT_YEARLY
        elif membership_type == 'COM':
            if payment_plan == 'monthly':
                plan_id = settings.COMPANY_PAYMENT_MONTHLY
            else:
                plan_id = settings.COMPANY_PAYMENT_YEARLY
        else:
            pass
        return Response(
                {"plan_id": plan_id}, status=status.HTTP_200_OK)


class BraintreeSubscriptionDetails(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # user_email = self.request.GET.get('email')
            # logged_user = CustomUser.objects.get(email=user_email)
            logged_user = Token.objects.get(key=request.data['token']).user
            membership_type = logged_user.membership
        except ObjectDoesNotExist:
            return Response(
                        {"status": "invalid user token"},
                        status=status.HTTP_400_BAD_REQUEST)
        payment_plan = request.data['payment_plan']
        if membership_type == 'IND':
            if payment_plan == 'monthly':
                plan_id = settings.BRAINTREE_PLAN_ID_INDIE_PAYMENT_MONTHLY
            else:
                plan_id = settings.BRAINTREE_PLAN_ID_INDIE_PAYMENT_YEARLY
        elif membership_type == 'PRO':
            if payment_plan == 'monthly':
                plan_id = settings.BRAINTREE_PLAN_ID_PRO_PAYMENT_MONTHLY
            else:
                plan_id = settings.BRAINTREE_PLAN_ID_PRO_PAYMENT_YEARLY
        elif membership_type == 'COM':
            if payment_plan == 'monthly':
                plan_id = settings.BRAINTREE_PLAN_ID_COMPANY_PAYMENT_MONTHLY
            else:
                plan_id = settings.BRAINTREE_PLAN_ID_COMPANY_PAYMENT_YEARLY
        else:
            pass
        return Response(
                {"plan_id": plan_id}, status=status.HTTP_200_OK)


class PaypalToken(APIView):

    def post(self, request, *args, **kwargs):
        paypal_client_id = settings.PAYPAL_CLIENT_ID
        paypal_secret = settings.PAYPAL_SECRET_ID
        data = {'grant_type': 'client_credentials'}
        user_response = requests.post(
                            'https://api-m.sandbox.paypal.com/v1/oauth2/token',
                            data=data,
                            auth=(paypal_client_id, paypal_secret),
                            headers={'Accept': 'application/json',
                                     'Accept-Language': 'en_US'})
        if user_response.status_code == 200:
            access_token = json.loads(user_response.content)['access_token']
            return Response(
                {"access_token": access_token}, status=status.HTTP_200_OK)
        else:
            return HttpResponse('Could not save data')


class PaypalPlanID(APIView):
    def get(self, request, *args, **kwargs):
        paypal_plans = {
            'indie_payment_monthly': settings.INDIE_PAYMENT_MONTHLY,
            'indie_payment_yearly': settings.INDIE_PAYMENT_YEARLY,
            'pro_payment_monthly': settings.PRO_PAYMENT_MONTHLY,
            'pro_payment_yearly': settings.PRO_PAYMENT_YEARLY,
            'company_payment_monthly': settings.COMPANY_PAYMENT_MONTHLY,
            'company_payment_yearly': settings.COMPANY_PAYMENT_YEARLY
        }
        return JsonResponse(paypal_plans)


class InitialRequest(APIView):

    def post(self, request, *args, **kwargs):
        amount = request.data['amount']
        payment_method_nonce = request.data['payment_method_nonce']
        # submit_for_settlement = request.data['submit_for_settlement']
        braintree_plan_id = request.data['braintree_plan_id']
        email = request.data['email']
        user = CustomUser.objects.get(email=email)
        membership_type = 'card_payment'
        payment_plan = request.data['payment_plan']
        payment_method = request.data['payment_method']
        days_free = request.data['days_free']
        initial_amount = request.data['initial_amount']
        tax_applied = request.data['tax_applied']
        if request.data['promocodes_applied'] == '':
            promocodes_applied = None
        else:
            promocodes_applied = request.data['promocodes_applied']
        promotion_amount = request.data['promotion_amount']

        gateway = braintree.BraintreeGateway(
            braintree.Configuration(
                braintree.Environment.Sandbox,
                merchant_id=settings.BRAINTREE_MERCHANT_ID,
                public_key=settings.BRAINTREE_PUBLIC_KEY,
                private_key=settings.BRAINTREE_PRIVATE_KEY
            )
        )

        if user.middle_name is None:
            middle_name = ''
        else:
            middle_name = user.middle_name

        if user.last_name is None:
            last_name = ''
        else:
            last_name = user.last_name

        middle_n_last = middle_name + ' ' + last_name

        customer_create_result = gateway.customer.create({
            "first_name": user.first_name,
            "last_name": middle_n_last,
            "payment_method_nonce": payment_method_nonce
        })

        customer_create_temp_result = customer_create_result

        if not customer_create_temp_result.is_success:
            return Response(
                {"status": "braintree customer creation unsuccsessful "},
                status=status.HTTP_400_BAD_REQUEST)
        import pdb;pdb.set_trace()
        subscription_create_result = gateway.subscription.create({
            "payment_method_token":
            customer_create_result.customer.payment_methods[0].token,
            "plan_id": braintree_plan_id
        })
        subscription_create_temp_result = subscription_create_result
        if not subscription_create_temp_result.is_success:
            return Response(
                {"status": "braintree subscription creation unsuccsessful "},
                status=status.HTTP_400_BAD_REQUEST)
        else:
            Transaction.objects.create(
                user=user,
                membership=membership_type,
                payment_plan=payment_plan,
                payment_method=payment_method,
                days_free=days_free,
                initial_amount=initial_amount,
                tax_applied=tax_applied,
                promocodes_applied=promocodes_applied,
                promotion_amount=promotion_amount,
                final_amount=amount)
            CustomUser.objects.filter(
                email=user.email
            ).update(registration_complete=True)

        # transaction_create_result = gateway.transaction.sale({
        #     "amount": amount,
        #     "payment_method_nonce": payment_method_nonce,
        #     "device_data": "",
        #     "options": {
        #         "submit_for_settlement": submit_for_settlement
        #     }
        # })
        # transaction_create_temp_result = transaction_create_result
        # if not transaction_create_temp_result.is_success:
        #     return Response(
        #         {"status": "braintree transaction creation unsuccsessful "},
        #         status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"status": "braintree transaction succsessful "},
            status=status.HTTP_200_OK)


class ManageSubscription(APIView):

    def post(self, request, *args, **kwargs):
        new_price = request.data['new_price']

        gateway = braintree.BraintreeGateway(
            braintree.Configuration(
                braintree.Environment.Sandbox,
                merchant_id=settings.BRAINTREE_MERCHANT_ID,
                public_key=settings.BRAINTREE_PUBLIC_KEY,
                private_key=settings.BRAINTREE_PRIVATE_KEY
            )
        )
        result = gateway.subscription.update("a_subscription_id", {
            "id": "new_id",
            "payment_method_token": "new_payment_method_token",
            "price": new_price,
            "plan_id": "new_plan",
        })
        if not result.is_success:
            return Response(
                {"status": "braintree subscription updation unsuccsessful "},
                status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"status": "braintree subscription updation succsessful "},
            status=status.HTTP_200_OK)
