import braintree
import datetime
import json
import requests

from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.generic.base import View

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from datetimerange import DateTimeRange

from film_hobo import settings
from hobo_user.models import HoboPaymentsDetails, IndiePaymentDetails, \
    ProPaymentDetails, CompanyPaymentDetails, PromoCode, CustomUser, \
    BraintreePromoCode, BetaTesterCodes
from .models import PaymentOptions, Transaction, EmailRecord, \
    FilmHoboSenderEmail
from .serializers import DiscountsSerializer, TransactionSerializer, \
    EmailRecordSerializer

# Create your views here.

from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, \
    OrdersCaptureRequest, OrdersGetRequest


class IsSuperUser(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class UpdateMembershipFeeDetailsAPI(APIView):
    """
    API for superuser to update the membership fee details to film_hobo backend
    """
    permission_classes = (IsSuperUser,)

    def get(self, request, *args, **kwargs):
        pass
        # token_generation_url = \
        #     'https://api.sandbox.paypal.com/v1/oauth2/token'

        # token_generation_url_username = settings.PAYPAL_CLIENT_ID
        # token_generation_url_password = settings.PAYPAL_SECRET_ID
        # full_user = token_generation_url_username + ':' +\
        #     token_generation_url_password

        # token_generation_url_response = requests.get(
        #     token_generation_url,
        #     headers={'Accept': 'application/json',
        #              'Accept-Language': 'en_US'},
        #     params={'grant_type': 'client_credentials'},
        #     auth=(
        # token_generation_url_username, token_generation_url_password))
        # if indie_monthly_user_response.status_code == 200:
        #     passindie_monthly_user_response
        # else:
        #     pass

        # details_url_origin = \
        #     'https://api-m.sandbox.paypal.com/v1/billing/plans/'
        # indie_monthly_details_url = \
        #     details_url_origin + settings.INDIE_PAYMENT_MONTHLY
        # indie_yearly_details_url = \
        #     details_url_origin + settings.INDIE_PAYMENT_YEARLY
        # pro_monthly_details_url = \
        #     details_url_origin + settings.PRO_PAYMENT_MONTHLY
        # pro_yearly_details_url = \
        #     details_url_origin + settings.PRO_PAYMENT_YEARLY
        # company_monthly_details_url = \
        #     details_url_origin + settings.COMPANY_PAYMENT_MONTHLY
        # company_yearly_details_url = \
        #     details_url_origin + settings.COMPANY_PAYMENT_YEARLY

        # indie_monthly_user_response = requests.get(
        #     indie_monthly_details_url,
        #     headers={'Content-type': 'application/json',
        #              'Authorization': ''})
        # if indie_monthly_user_response.status_code == 200:
        #     new_user = CustomUser.objects.get(
        #                 email=request.POST['email'])
        #     if must_validate_email:
        #         ipaddr = self.request.META.get('REMOTE_ADDR', '0.0.0.0')
        #         signup_code = SignupCode.objects.create_signup_code(
        #                 new_user, ipaddr)
        #         signup_code.send_signup_email()

        #     return render(request,
        #                     'user_pages/user_email_verification.html',
        #                     {'user': new_user})
        # else:
        #     return HttpResponse('Could not save data')


class BetaUserPlanDetails(APIView):
    """
    API to get beta user plan details
    """

    def post(self, request, *args, **kwargs):
        data = request.data
        code = data['code']
        membership_plan = data['membership']
        period = data['period']
        if not code or not membership_plan or not period:
            return Response(
                {"status": "failure",
                 "message": "please enter a valid code/memebrship/period"
                 }, status=status.HTTP_204_NO_CONTENT)
        else:
            extra_data = {'code': '', 'days': '',
                          'bill_date': '',
                          'selected_plan_id': ''}
            bet_user_code_obj = BetaTesterCodes.objects.get(code=code)
            free_evaluation_time = bet_user_code_obj.days
            date_today = datetime.date.today()
            date_interval = datetime.timedelta(days=int(free_evaluation_time))
            bill_date = date_today + date_interval
            extra_data['code'] = code
            extra_data['days'] = bet_user_code_obj.days
            extra_data['bill_date'] = bill_date.strftime("%d/%m/%Y")
            if membership_plan == 'indie':
                if period == 'monthly':
                    selected_plan_id = bet_user_code_obj.indie_monthly_plan_id
                else:
                    selected_plan_id = bet_user_code_obj.indie_yearly_plan_id
            elif membership_plan == 'pro':
                if period == 'monthly':
                    selected_plan_id = bet_user_code_obj.pro_monthly_plan_id
                else:
                    selected_plan_id = bet_user_code_obj.pro_yearly_plan_id
            elif membership_plan == 'company':
                if period == 'monthly':
                    selected_plan_id = \
                        bet_user_code_obj.company_monthly_plan_id
                else:
                    selected_plan_id = \
                        bet_user_code_obj.company_yearly_plan_id
            else:
                pass
            extra_data['selected_plan_id'] = selected_plan_id
            data.update(extra_data)
            return Response(extra_data, status=status.HTTP_200_OK)


class DiscountPlanDetails(APIView):
    """
    API to get users discount details
    """

    def post(self, request, *args, **kwargs):
        data = request.data
        code = data['code']
        membership_plan = data['membership']
        period = data['period']
        if not code or not membership_plan or not period:
            return Response(
                {"status": "failure",
                 "message": "please enter a valid code/memebrship/period"
                 }, status=status.HTTP_204_NO_CONTENT)
        else:
            extra_data = {'code': '',
                          'selected_plan_id': ''}
            # extra_data = {'code': '', 'days': '',
            #               'bill_date': '',
            #               'selected_plan_id': ''}
            discount_code_obj = PromoCode.objects.get(promo_code=code)

            # free_evaluation_time = discount_code_obj.days
            # date_today = datetime.date.today()
            # date_interval = datetime.timedelta(days=int(free_evaluation_time))
            # bill_date = date_today + date_interval

            extra_data['code'] = code
            # extra_data['days'] = discount_code_obj.days
            # extra_data['bill_date'] = bill_date.strftime("%d/%m/%Y")
            if membership_plan == 'indie':
                if period == 'monthly':
                    selected_plan_id = discount_code_obj.indie_monthly_plan_id
                else:
                    selected_plan_id = discount_code_obj.indie_yearly_plan_id
            elif membership_plan == 'pro':
                if period == 'monthly':
                    selected_plan_id = discount_code_obj.pro_monthly_plan_id
                else:
                    selected_plan_id = discount_code_obj.pro_yearly_plan_id
            elif membership_plan == 'company':
                if period == 'monthly':
                    selected_plan_id = \
                        discount_code_obj.company_monthly_plan_id
                else:
                    selected_plan_id = \
                        discount_code_obj.company_yearly_plan_id
            else:
                pass
            extra_data['selected_plan_id'] = selected_plan_id
            data.update(extra_data)
            return Response(extra_data, status=status.HTTP_200_OK)


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
                elif (float(data['tax']) < 0.0) or \
                     (float(data['tax']) > 100.0):
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
        user_obj = CustomUser.objects.get(id=request.user.id)
        admin_token = Token.objects.get(user=user_obj).key
        if not request.GET.get('token'):
            return_url = "/payment/payment_admin/?token=" + admin_token + '/'
            return HttpResponseRedirect(return_url)
        else:
            return render(request, 'payment/payment_admin.html')


class AddDiscountDetailAPI(APIView):
    """
    API for superuser to add a discount with details
    """
    permission_classes = (IsSuperUser,)

    def post(self, request, format=None):
        initial_data = request.data
        print(initial_data)
        midnight = 'T00:00:00Z'
        initial_data['valid_from'] = initial_data['valid_from'] + midnight
        initial_data['valid_to'] = initial_data['valid_to'] + midnight
        initial_data['user_type'] = 'ADMIN'
        datetime_obj_valid_from = datetime.datetime.strptime(
            initial_data['valid_from'], '%Y-%m-%dT%H:%M:%SZ')
        datetime_obj_valid_to = datetime.datetime.strptime(
            initial_data['valid_to'], '%Y-%m-%dT%H:%M:%SZ')
        delta = datetime_obj_valid_to - datetime_obj_valid_from
        discounted_days = delta.days

        # function to get value of a key in json
        def find_values(id, json_repr):
            results = []

            def _decode_dict(a_dict):
                try:
                    results.append(a_dict[id])
                except KeyError:
                    pass
                return a_dict

            json.loads(json_repr, object_hook=_decode_dict)
            return results

        # function to get final discounted value
        def find_final_discounted_value(percentage, plan_value):
            value_to_be_deducted = (float(percentage) *
                                    float(plan_value) / 100.00)
            final_discounted_value = plan_value - value_to_be_deducted
            return round(final_discounted_value, 2)

        # get paypal access_token
        paypal_client_id = settings.PAYPAL_CLIENT_ID
        paypal_secret = settings.PAYPAL_SECRET_ID
        data = {'grant_type': 'client_credentials'}
        token_user_response = requests.post(
                            'https://api-m.sandbox.paypal.com/v1/oauth2/token',
                            data=data,
                            auth=(paypal_client_id, paypal_secret),
                            headers={'Accept': 'application/json',
                                     'Accept-Language': 'en_US'})
        print(token_user_response.status_code)
        if token_user_response.status_code == 200:
            access_token = json.loads(
                token_user_response.content)['access_token']
        else:
            return Response(
                {"status": "error in fetching paypal access token"},
                status=status.HTTP_404_NOT_FOUND)

        access_token_strting = 'Bearer ' + access_token

        # get the current plan details
        paypal_get_plan_details_api = \
            "https://api-m.sandbox.paypal.com/v1/billing/plans/"

        # 1
        indie_monthly_plan_details_api = paypal_get_plan_details_api + \
            settings.INDIE_PAYMENT_MONTHLY
        indie_monthly_plan_details_api_response = requests.get(
                            indie_monthly_plan_details_api,
                            headers={'Content-Type': 'application/json',
                                     'Authorization': access_token_strting})
        
        if indie_monthly_plan_details_api_response.status_code == 200:
            indie_monthly_plan_value = find_values(
                'value', indie_monthly_plan_details_api_response.text)[0]
        else:
            return Response(
                {"status": "error in fetching paypal plan"},
                status=status.HTTP_404_NOT_FOUND)
        # 2
        indie_yearly_plan_details_api = paypal_get_plan_details_api + \
            settings.INDIE_PAYMENT_YEARLY
        indie_yearly_plan_details_api_response = requests.get(
                            indie_yearly_plan_details_api,
                            headers={'Content-Type': 'application/json',
                                     'Authorization': access_token_strting})
       
        if indie_yearly_plan_details_api_response.status_code == 200:
            indie_yearly_plan_value = find_values(
                'value', indie_yearly_plan_details_api_response.text)[0]
        else:
            return Response(
                {"status": "error in fetching paypal plan"},
                status=status.HTTP_404_NOT_FOUND)
        # 3
        pro_monthly_plan_details_api = paypal_get_plan_details_api + \
            settings.PRO_PAYMENT_MONTHLY
        pro_monthly_plan_details_api_response = requests.get(
                            pro_monthly_plan_details_api,
                            headers={'Content-Type': 'application/json',
                                     'Authorization': access_token_strting})
        if pro_monthly_plan_details_api_response.status_code == 200:
            pro_monthly_plan_value = find_values(
                'value', pro_monthly_plan_details_api_response.text)[0]
        else:
            return Response(
                {"status": "error in fetching paypal plan"},
                status=status.HTTP_404_NOT_FOUND)
        # 4
        pro_yearly_plan_details_api = paypal_get_plan_details_api + \
            settings.PRO_PAYMENT_YEARLY
        pro_yearly_plan_details_api_response = requests.get(
                            pro_yearly_plan_details_api,
                            headers={'Content-Type': 'application/json',
                                     'Authorization': access_token_strting})
        if pro_yearly_plan_details_api_response.status_code == 200:
            pro_yearly_plan_value = find_values(
                'value', pro_yearly_plan_details_api_response.text)[0]
        else:
            return Response(
                {"status": "error in fetching paypal plan"},
                status=status.HTTP_404_NOT_FOUND)
        # 5
        company_monthly_plan_details_api = paypal_get_plan_details_api + \
            settings.COMPANY_PAYMENT_MONTHLY
        company_monthly_plan_details_api_response = requests.get(
                            company_monthly_plan_details_api,
                            headers={'Content-Type': 'application/json',
                                     'Authorization': access_token_strting})
        if company_monthly_plan_details_api_response.status_code == 200:
            company_monthly_plan_value = find_values(
                'value', company_monthly_plan_details_api_response.text)[0]
        else:
            return Response(
                {"status": "error in fetching paypal plan"},
                status=status.HTTP_404_NOT_FOUND)
        # 6
        company_yearly_plan_details_api = paypal_get_plan_details_api + \
            settings.COMPANY_PAYMENT_YEARLY
        company_yearly_plan_details_api_response = requests.get(
                            company_yearly_plan_details_api,
                            headers={'Content-Type': 'application/json',
                                     'Authorization': access_token_strting})
        if company_yearly_plan_details_api_response.status_code == 200:
            company_yearly_plan_value = find_values(
                'value', company_yearly_plan_details_api_response.text)[0]
        else:
            return Response(
                {"status": "error in fetching paypal plan"},
                status=status.HTTP_404_NOT_FOUND)

        # create plans based on the input

        plan_types = ['Indie Payment Monthly', 'Indie Payment Yearly',
                      'Pro Payment Monthly', 'Pro Payment Yearly',
                      'Company Payment Monthly', 'Company Payment Yearly']
        plan_ids = {'indie_monthly_plan_id': '',
                    'indie_yearly_plan_id': '',
                    'pro_monthly_plan_id': '',
                    'pro_yearly_plan_id': '',
                    'company_monthly_plan_id': '',
                    'company_yearly_plan_id': ''}
        for plan_type in plan_types:
            plan_name = 'Discount Plan' + ' - ' + plan_type + ' - ' + \
                request.data['promo_code']
            if plan_type.find('Monthly'):
                plan_interval_unit = 'MONTH'
            else:
                plan_interval_unit = 'YEAR'

            if plan_type == 'Indie Payment Monthly':
                plan_interval_count = indie_monthly_plan_value
                if (initial_data['amount_type'] == 'percentage'):
                    final_discounted_value = \
                        find_final_discounted_value(
                            float(initial_data['amount']),
                            float(indie_monthly_plan_value))
                else:
                    final_discounted_value = (
                        float(indie_monthly_plan_value) -
                        float(initial_data['amount']))
            elif plan_type == 'Indie Payment Yearly':
                plan_interval_count = indie_yearly_plan_value
                if (initial_data['amount_type'] == 'percentage'):
                    final_discounted_value = \
                        find_final_discounted_value(
                            float(initial_data['amount']),
                            float(indie_yearly_plan_value))
                else:
                    final_discounted_value = (
                        float(indie_yearly_plan_value) -
                        float(initial_data['amount']))
            elif plan_type == 'Pro Payment Monthly':
                plan_interval_count = pro_monthly_plan_value
                if (initial_data['amount_type'] == 'percentage'):
                    final_discounted_value = \
                        find_final_discounted_value(
                            float(initial_data['amount']),
                            float(pro_monthly_plan_value))
                else:
                    final_discounted_value = (
                        float(pro_monthly_plan_value) -
                        float(initial_data['amount']))
            elif plan_type == 'Pro Payment Yearly':
                plan_interval_count = pro_yearly_plan_value
                if (initial_data['amount_type'] == 'percentage'):
                    final_discounted_value = \
                        find_final_discounted_value(
                            float(initial_data['amount']),
                            float(pro_yearly_plan_value))
                else:
                    final_discounted_value = (
                        float(pro_yearly_plan_value) -
                        float(initial_data['amount']))
            elif plan_type == 'Company Payment Monthly':
                plan_interval_count = company_monthly_plan_value
                if (initial_data['amount_type'] == 'percentage'):
                    final_discounted_value = \
                        find_final_discounted_value(
                            float(initial_data['amount']),
                            float(company_monthly_plan_value))
                else:
                    final_discounted_value = (
                        float(company_monthly_plan_value) -
                        float(initial_data['amount']))
            elif plan_type == 'Company Payment Yearly':
                plan_interval_count = company_yearly_plan_value
                if (initial_data['amount_type'] == 'percentage'):
                    final_discounted_value = \
                        find_final_discounted_value(
                            float(initial_data['amount']),
                            float(company_yearly_plan_value))
                else:
                    final_discounted_value = (
                        float(company_yearly_plan_value) -
                        float(initial_data['amount']))
            else:
                pass

            create_plan_json = {
                "name": plan_name,
                "description": plan_name,
                "product_id": settings.PRODUCT_ID,
                "billing_cycles": [
                    {
                        "frequency": {
                            "interval_unit": "DAY",
                            "interval_count": discounted_days
                        },
                        "tenure_type": "TRIAL",
                        "sequence": 1,
                        "total_cycles": 1,
                        "pricing_scheme": {
                            "fixed_price": {
                                "value": final_discounted_value,
                                "currency_code": "USD"
                            }
                        }
                    },
                    {
                        "frequency": {
                            "interval_unit": plan_interval_unit,
                            "interval_count": 1
                        },
                        "tenure_type": "REGULAR",
                        "sequence": 2,
                        "total_cycles": 0,
                        "pricing_scheme": {
                            "fixed_price": {
                                "value": plan_interval_count,
                                "currency_code": "USD"
                            }
                        }
                    }
                ],
                "payment_preferences": {
                    "auto_bill_outstanding": True,
                    "payment_failure_threshold": 1
                }
            }

            create_plan_user_response = requests.post(
                        'https://api-m.sandbox.paypal.com/v1/billing/plans',
                        data=json.dumps(create_plan_json),
                        headers={'Accept': 'application/json',
                                 'Authorization': access_token_strting,
                                 'Content-type': 'application/json'
                                 })
            print(create_plan_user_response.status_code)
            if create_plan_user_response.status_code == 201:
                plan_id = json.loads(create_plan_user_response.content)['id']
                if plan_type == 'Indie Payment Monthly':
                    plan_ids['indie_monthly_plan_id'] = plan_id
                elif plan_type == 'Indie Payment Yearly':
                    plan_ids['indie_yearly_plan_id'] = plan_id
                elif plan_type == 'Pro Payment Monthly':
                    plan_ids['pro_monthly_plan_id'] = plan_id
                elif plan_type == 'Pro Payment Yearly':
                    plan_ids['pro_yearly_plan_id'] = plan_id
                elif plan_type == 'Company Payment Monthly':
                    plan_ids['company_monthly_plan_id'] = plan_id
                elif plan_type == 'Company Payment Yearly':
                    plan_ids['company_yearly_plan_id'] = plan_id
                else:
                    pass
            else:
                return HttpResponse('Could not save data')
        initial_data.update(plan_ids)
        print(initial_data)
        serializer = DiscountsSerializer(data=initial_data)
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
            try:
                promocodes_applied = PromoCode.objects.get(
                    promo_code=request.data['promocodes_applied'])
            except ObjectDoesNotExist:
                return Response(
                            {"status": "promocode does not exist"},
                            status=status.HTTP_400_BAD_REQUEST)
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

            if promocodes_applied:
                if payment_plan.lower() == 'year' or 'yearly' or 'annually':
                    payment_plan_time = 'YEAR'
                else:
                    payment_plan_time = 'MONTH'

                new_plan_name = membership_type.capitalize() \
                    + ' Payment - ' + payment_plan.capitalize() \
                    + ' - ' + promocodes_applied.promo_code

                data_dict = {
                    "product_id": settings.PRODUCT_ID,
                    "name": new_plan_name,
                    "description": new_plan_name,
                    "status": "ACTIVE",
                    "billing_cycles": [
                        {
                            "frequency": {
                                "interval_unit": payment_plan_time,
                                "interval_count": 1
                            },
                            "tenure_type": "REGULAR",
                            "sequence": 1,
                            "total_cycles": 0,
                            "pricing_scheme": {
                                "fixed_price": {
                                    "value": final_amount,
                                    "currency_code": "USD"
                                }
                            }
                        }
                    ],
                    "payment_preferences": {
                            "auto_bill_outstanding": True,
                            "setup_fee": {
                                "value": "0",
                                "currency_code": "USD"
                            },
                            "setup_fee_failure_action": "CONTINUE",
                            "payment_failure_threshold": 3
                    },
                    "taxes": {
                        "percentage": "0",
                        "inclusive": False
                    }
                    }

                paypal_client_id = settings.PAYPAL_CLIENT_ID
                paypal_secret = settings.PAYPAL_SECRET_ID
                data = {'grant_type': 'client_credentials'}
                token_user_response = \
                    requests.post(
                        'https://api-m.sandbox.paypal.com/v1/oauth2/token',
                        data=data,
                        auth=(paypal_client_id, paypal_secret),
                        headers={'Accept': 'application/json',
                                 'Accept-Language': 'en_US'})
                if token_user_response.status_code == 200:
                    access_token = json.loads(
                        token_user_response.content)['access_token']
                else:
                    return HttpResponse('Could not save data')

                access_token_strting = 'Bearer ' + access_token

                create_plan_user_response = requests.post(
                        'https://api-m.sandbox.paypal.com/v1/billing/plans',
                        data=json.dumps(data_dict),
                        headers={'Content-type': 'application/json',
                                 'Authorization': access_token_strting
                                 })
                if create_plan_user_response.status_code == 201:
                    plan_id = \
                        json.loads(create_plan_user_response.content)['id']
                else:
                    return HttpResponse('Could not save data')
            else:
                # create_order request for no discount added
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
                base_url = settings.ORIGIN_URL
                complete_url = base_url + '/payment/paypal/send_email_recepit/'
                order_id = data['id']
                send_email_url_args = {
                    "order_id": order_id
                }
                user_response = requests.post(
                    complete_url,
                    data=send_email_url_args)
                if user_response.status_code == 200:
                    pass
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


# class UpdateSubscription(APIView):
#     """
#     API to update the braintree subscription
#     """
#     permission_classes = (IsAdminUser,)

#     def post(self, request, *args, **kwargs):
#         new_indie_monthly = request.data['indie_monthly']
#         new_indie_yearly = request.data['indie_yearly']
#         new_pro_monthly = request.data['pro_monthly']
#         new_pro_yearly = request.data['pro_yearly']
#         new_company_monthly = request.data['company_monthly']
#         new_company_yearly = request.data['company_yearly']

#         gateway = braintree.BraintreeGateway(
#             braintree.Configuration(
#                 braintree.Environment.Sandbox,
#                 merchant_id=settings.BRAINTREE_MERCHANT_ID,
#                 public_key=settings.BRAINTREE_PUBLIC_KEY,
#                 private_key=settings.BRAINTREE_PRIVATE_KEY
#             )
#         )
#         result = gateway.subscription.update("a_subscription_id", {
#             "id": "new_id",
#             "payment_method_token": "new_payment_method_token",
#             "price": "new_price",
#             "plan_id": "new_plan",
#         })
#         if not result.is_success:
#             return Response(
#                 {"status": "braintree subscription updation unsuccsessful "},
#                 status=status.HTTP_400_BAD_REQUEST)
#         return Response(
#             {"status": "braintree subscription updation succsessful "},
#             status=status.HTTP_200_OK)


class GetBraintreeDiscountDetailListAPI(APIView):
    """
    API for superuser to get the braintree discount details
    """

    def get(self, request, *args, **kwargs):
        gateway = braintree.BraintreeGateway(
            braintree.Configuration(
                braintree.Environment.Sandbox,
                merchant_id=settings.BRAINTREE_MERCHANT_ID,
                public_key=settings.BRAINTREE_PUBLIC_KEY,
                private_key=settings.BRAINTREE_PRIVATE_KEY
            )
        )

        discounts = gateway.discount.all()
        final_list = []
        for discount in discounts:
            data_dict = {
                "braintree_id": "",
                "promo_code": "",
                "description": "",
                "duration": "",
                "billing_cycles": "",
                "amount": ''
            }
            if discount.never_expires:
                promocode, created = \
                    BraintreePromoCode.objects.update_or_create(
                        braintree_id=discount.id, promo_code=discount.name,
                        description=discount.description,
                        duration='full_subscription',
                        billing_cycles=discount.number_of_billing_cycles,
                        amount=discount.amount
                    )
                data_dict['braintree_id'] = discount.id
                data_dict['promo_code'] = discount.name
                data_dict['description'] = discount.description
                data_dict['duration'] = 'full_subscription'
                data_dict['billing_cycles'] = discount.number_of_billing_cycles
                data_dict['amount'] = discount.amount
                final_list.append(data_dict)
            else:
                promocode, created = \
                    BraintreePromoCode.objects.update_or_create(
                        braintree_id=discount.id, promo_code=discount.name,
                        description=discount.description,
                        duration='billing_cycle_subscription',
                        billing_cycles=discount.number_of_billing_cycles,
                        amount=discount.amount
                    )
                data_dict['braintree_id'] = discount.id
                data_dict['promo_code'] = discount.name
                data_dict['description'] = discount.description
                data_dict['duration'] = 'billing_cycle_subscription'
                data_dict['billing_cycles'] = discount.number_of_billing_cycles
                data_dict['amount'] = discount.amount
                final_list.append(data_dict)
        if len(discounts) > 0:
            return JsonResponse(final_list, safe=False)
        else:
            return Response({"status": "no content",
                            "discounts": "no discounts associated with this \
                            account"
                             }, status=status.HTTP_204_NO_CONTENT)


class BraintreeCalculateDiscountAPI(APIView):
    """
    API for calculateing the braintree discount
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
                initial_amount = float(data['amount'])
                promotion_amount = float(promocode_obj.amount)
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
        except ObjectDoesNotExist:
            return Response(
                {"status": "promocode does not exist"},
                status=status.HTTP_404_NOT_FOUND)


class GetNewPlanDetailsJSON(APIView):
    """
    API for getting data to create new plan for discounts
    """
    def post(self, request, format=None):
        plan_type = request.data['plan_type']
        plan_tenure = request.data['plan_tenure']
        applied_promocode = request.data['applied_promocode']
        final_new_amount = request.data['final_new_amount']

        if plan_tenure.lower() == 'year' or 'yearly':
            plan_tenure_time = 'YEAR'
        else:
            plan_tenure_time = 'MONTH'

        new_plan_name = plan_type.capitalize() \
            + ' Payment - ' + plan_tenure.capitalize() \
            + ' - ' + applied_promocode

        data_dict = {
            "product_id": settings.PRODUCT_ID,
            "name": new_plan_name,
            "description": new_plan_name,
            "status": "ACTIVE",
            "billing_cycles": [
                {
                    "frequency": {
                        "interval_unit": plan_tenure_time,
                        "interval_count": 1
                    },
                    "tenure_type": "REGULAR",
                    "sequence": 1,
                    "total_cycles": 0,
                    "pricing_scheme": {
                        "fixed_price": {
                            "value": final_new_amount,
                            "currency_code": "USD"
                        }
                    }
                }
            ],
            "payment_preferences": {
                    "auto_bill_outstanding": True,
                    "setup_fee": {
                        "value": "0",
                        "currency_code": "USD"
                    },
                    "setup_fee_failure_action": "CONTINUE",
                    "payment_failure_threshold": 3
            },
            "taxes": {
                "percentage": "0",
                "inclusive": False
            }
            }

        if plan_type.strip() == '' or \
           plan_tenure.strip() == '' or \
           applied_promocode.strip() == '' or \
           final_new_amount.strip() == '':
            return Response({"status": "no content"
                             }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse(data_dict, safe=False)


class PayPalSendEmail(APIView):
    """
    API to send receipt for paypal transaction
    """
    def post(self, request, *args, **kwargs):
        order_id = request.data['order_id']
        transaction_obj = Transaction.objects.get(paypal_order_id=order_id)
        start_date = transaction_obj.date
        start_date_formated = start_date.strftime("%d/%m/%Y")
        free_days = datetime.timedelta(days=int(transaction_obj.days_free))
        start_date_after_trial = start_date + free_days
        start_date_after_trial_formated = \
            start_date_after_trial.strftime("%d/%m/%Y")
        payment_method = transaction_obj.payment_method
        payment_plan = transaction_obj.payment_plan
        price = float(transaction_obj.final_amount)

        start_date_total_purchase_value = "00.00"
        start_date_sales_tax_percentage = 0.0
        start_date_sales_tax_value = "00.00"
        start_date_order_total_value = "00.00"

        paid_start_date_total_purchase_value = '{:.2f}'.format(round(price, 2))
        paid_start_date_sales_tax_percentage = 0.0
        paid_start_date_sales_tax_value = "00.00"
        paid_start_date_order_total_value = '{:.2f}'.format(round(price, 2))

        base_url = settings.ORIGIN_URL
        privacy_policy_url = base_url + '/general/privacy_policy/'
        terms_of_service_url = base_url + '/general/terms_of_service/'

        html_context = {
            'user_name': transaction_obj.user.get_full_name(),
            'user_membership': transaction_obj.user.membership,
            'order_id': transaction_obj.id,
            'start_date': start_date_formated,
            'start_date_after_trial': start_date_after_trial_formated,

            'payment_method': payment_method,
            'plan': payment_plan,
            'price': price,
            'free_trial_days': transaction_obj.days_free,

            'start_date_total_purchase_value': start_date_total_purchase_value,
            'start_date_sales_tax_percentage': start_date_sales_tax_percentage,
            'start_date_sales_tax_value': start_date_sales_tax_value,
            'start_date_order_total_value': start_date_order_total_value,

            'paid_start_date_total_purchase_value':
            paid_start_date_total_purchase_value,
            'paid_start_date_sales_tax_percentage':
            paid_start_date_sales_tax_percentage,
            'paid_start_date_sales_tax_value':
            paid_start_date_sales_tax_value,
            'paid_start_date_order_total_value':
            paid_start_date_order_total_value,

            'privacy_policy_url': privacy_policy_url,
            'terms_of_service_url': terms_of_service_url,
        }
        text_context = {
            'user_name': transaction_obj.user.get_full_name,
        }
        email_subject = "Welcome to FilmHobo. " \
            "Here are your subscription details."
        email_body_text = render_to_string(
            "payment_receipts/email_receipt.txt", text_context, request
        )
        email_body_html = render_to_string(
            "payment_receipts/email_receipt.html", html_context, request
        )
        recipient_email = transaction_obj.user.email
        email_recipients = [recipient_email]
        email_from = getattr(
            settings, "PAYPAL_SENDER_EMAIL",
        )
        email_from_obj = FilmHoboSenderEmail.objects.get(email=email_from)
        success = send_mail(
            subject=email_subject,
            message=email_body_text,
            from_email=email_from,
            recipient_list=email_recipients,
            html_message=email_body_html,
        )
        email_record_obj = EmailRecord.objects.create(
            sender=email_from_obj,
            recipient=transaction_obj.user,
            email=transaction_obj.user.email,
            subject=email_subject,
            sent=success,
        )
        serialized_obj_dict = {
            "when": email_record_obj.when,
            "sender": email_record_obj.sender.id,
            "recipient": email_record_obj.recipient.id,
            "email": email_record_obj.email,
            "subject": email_record_obj.subject,
            "sent": email_record_obj.sent
        }
        serializer = EmailRecordSerializer(data=serialized_obj_dict)
        if serializer.is_valid():
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class PayPalSendRemainderEmail(APIView):
    """
    API to send receipt for after monthly subscription is taken transaction
    """
    def post(self, request, *args, **kwargs):
        order_id = request.data['order_id']
        transaction_obj = Transaction.objects.get(paypal_order_id=order_id)
        order_date = transaction_obj.date
        order_date_formated = order_date.strftime("%d/%m/%Y")
        payment_method = transaction_obj.payment_method
        payment_plan = transaction_obj.payment_plan
        price = float(transaction_obj.final_amount)

        total_purchase_value = "00.00"
        sales_tax_percentage = 0.0
        sales_tax_value = "00.00"
        order_total_value = "00.00"

        base_url = settings.ORIGIN_URL
        privacy_policy_url = base_url + '/general/privacy_policy/'
        terms_of_service_url = base_url + '/general/terms_of_service/'

        html_context = {
            'user_name': transaction_obj.user.get_full_name(),
            'user_membership': transaction_obj.user.membership,
            'order_id': transaction_obj.id,
            'order_date': order_date_formated,

            'payment_method': payment_method,
            'plan': payment_plan,
            'price': price,
            'free_trial_days': transaction_obj.days_free,

            'total_purchase_value': total_purchase_value,
            'sales_tax_percentage': sales_tax_percentage,
            'sales_tax_value': sales_tax_value,
            'order_total_value': order_total_value,

            'privacy_policy_url': privacy_policy_url,
            'terms_of_service_url': terms_of_service_url,
        }
        text_context = {
            'user_name': transaction_obj.user.get_full_name,
        }
        email_subject = "Filmhobo Subscription Receipt"
        email_body_text = render_to_string(
            "payment_receipts/email_receipt.txt", text_context, request
        )
        email_body_html = render_to_string(
            "payment_receipts/email_reminder_receipt.html",
            html_context, request
        )
        recipient_email = transaction_obj.user.email
        email_recipients = [recipient_email]
        email_from = getattr(
            settings, "PAYPAL_SENDER_EMAIL",
        )
        email_from_obj = FilmHoboSenderEmail.objects.get(email=email_from)
        success = send_mail(
            subject=email_subject,
            message=email_body_text,
            from_email=email_from,
            recipient_list=email_recipients,
            html_message=email_body_html,
        )
        email_record_obj = EmailRecord.objects.create(
            sender=email_from_obj,
            recipient=transaction_obj.user,
            email=transaction_obj.user.email,
            subject=email_subject,
            sent=success,
        )
        serialized_obj_dict = {
            "when": email_record_obj.when,
            "sender": email_record_obj.sender.id,
            "recipient": email_record_obj.recipient.id,
            "email": email_record_obj.email,
            "subject": email_record_obj.subject,
            "sent": email_record_obj.sent
        }
        serializer = EmailRecordSerializer(data=serialized_obj_dict)
        if serializer.is_valid():
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class PayPalSendPlanChangeEmail(APIView):
    """
    API to send email to users when there is a change in subscription plan
    """
    def post(self, request, *args, **kwargs):
        email_status = False
        payment_plans = {
            "indie_monthly": settings.INDIE_PAYMENT_MONTHLY,
            "indie_yearly": settings.INDIE_PAYMENT_YEARLY,
            "pro_monthly": settings.PRO_PAYMENT_MONTHLY,
            "pro_yearly": settings.PRO_PAYMENT_MONTHLY,
            "company_monthly": settings.COMPANY_PAYMENT_MONTHLY,
            "company_yearly": settings.COMPANY_PAYMENT_YEARLY
        }

        changed_plan_id = request.data['changed_plan_id']
        for plan_name, plan_id in payment_plans.items():
            if plan_id == changed_plan_id:
                if plan_name == 'indie_monthly':
                    indie_monthly_users = CustomUser.objects.filter(
                        membership='IND', payment_plan='monthly')
                    for user in indie_monthly_users:
                        revised_rate = \
                            IndiePaymentDetails.objects.first().monthly_amount
                        send_email_url = settings.ORIGIN_URL + \
                            '/payment/paypal/change_notify_email/'
                        data = {
                            'user_id': user.id,
                            'revised_rate': revised_rate
                        }
                        send_email_url_response = requests.post(
                            send_email_url, data=data)
                        if send_email_url_response.status_code == 200:
                            email_status = True
                        else:
                            return Response(
                                {"status": "failure"},
                                status=status.HTTP_400_BAD_REQUEST)
                elif plan_name == 'indie_yearly':
                    indie_yearly_users = CustomUser.objects.filter(
                        membership='IND', payment_plan='yearly')
                    for user in indie_yearly_users:
                        revised_rate = \
                            IndiePaymentDetails.objects.first().annual_amount
                        send_email_url = settings.ORIGIN_URL + \
                            '/payment/paypal/change_notify_email/'
                        data = {
                            'user_id': user.id,
                            'revised_rate': revised_rate
                        }
                        send_email_url_response = requests.post(
                            send_email_url, data=data)
                        if send_email_url_response.status_code == 200:
                            email_status = True
                        else:
                            return Response(
                                {"status": "failure"},
                                status=status.HTTP_400_BAD_REQUEST)
                elif plan_name == 'pro_monthly':
                    pro_monthly_users = CustomUser.objects.filter(
                        membership='PRO', payment_plan='monthly')
                    for user in pro_monthly_users:
                        revised_rate = \
                            ProPaymentDetails.objects.first().monthly_amount
                        send_email_url = settings.ORIGIN_URL + \
                            '/payment/paypal/change_notify_email/'
                        data = {
                            'user_id': user.id,
                            'revised_rate': revised_rate
                        }
                        send_email_url_response = requests.post(
                            send_email_url, data=data)
                        if send_email_url_response.status_code == 200:
                            email_status = True
                        else:
                            return Response(
                                {"status": "failure"},
                                status=status.HTTP_400_BAD_REQUEST)
                elif plan_name == 'pro_yearly':
                    pro_yearly_users = CustomUser.objects.filter(
                        membership='PRO', payment_plan='yearly')
                    for user in pro_yearly_users:
                        revised_rate = \
                            ProPaymentDetails.objects.first().annual_amount
                        send_email_url = settings.ORIGIN_URL + \
                            '/payment/paypal/change_notify_email/'
                        data = {
                            'user_id': user.id,
                            'revised_rate': revised_rate
                        }
                        send_email_url_response = requests.post(
                            send_email_url, data=data)
                        if send_email_url_response.status_code == 200:
                            email_status = True
                        else:
                            return Response(
                                {"status": "failure"},
                                status=status.HTTP_400_BAD_REQUEST)
                elif plan_name == 'company_monthly':
                    company_monthly_users = CustomUser.objects.filter(
                        membership='COM', payment_plan='monthly')
                    for user in company_monthly_users:
                        revised_rate = \
                            CompanyPaymentDetails.objects.first().monthly_amount
                        send_email_url = settings.ORIGIN_URL + \
                            '/payment/paypal/change_notify_email/'
                        data = {
                            'user_id': user.id,
                            'revised_rate': revised_rate
                        }
                        send_email_url_response = requests.post(
                            send_email_url, data=data)
                        if send_email_url_response.status_code == 200:
                            email_status = True
                        else:
                            return Response(
                                {"status": "failure"},
                                status=status.HTTP_400_BAD_REQUEST)
                elif plan_name == 'company_yearly':
                    company_yearly_users = CustomUser.objects.filter(
                        membership='COM', payment_plan='yearly')
                    for user in company_yearly_users:
                        revised_rate = \
                            CompanyPaymentDetails.objects.first().annual_amount
                        send_email_url = settings.ORIGIN_URL + \
                            '/payment/paypal/change_notify_email/'
                        data = {
                            'user_id': user.id,
                            'revised_rate': revised_rate
                        }
                        send_email_url_response = requests.post(
                            send_email_url, data=data)
                        if send_email_url_response.status_code == 200:
                            email_status = True
                        else:
                            return Response(
                                {"status": "failure"},
                                status=status.HTTP_400_BAD_REQUEST)
                else:
                    pass
        if email_status:
            return Response({"status": "success"},
                            status=status.HTTP_200_OK)
        else:
            return Response({"status": "failure"},
                            status=status.HTTP_400_BAD_REQUEST)


class PayPalChangeNotifyEmail(APIView):
    """
    API to send email to users when there is a payment plan change
    """
    def post(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        revised_rate = request.data['revised_rate']
        user_obj = CustomUser.objects.get(id=user_id)

        base_url = settings.ORIGIN_URL
        privacy_policy_url = base_url + '/general/privacy_policy/'
        terms_of_service_url = base_url + '/general/terms_of_service/'

        html_context = {
            'user_name': user_obj.get_full_name(),
            'user_membership': user_obj.membership,
            'revised_rate': revised_rate,
            'plan_term': user_obj.payment_plan,
            'privacy_policy_url': privacy_policy_url,
            'terms_of_service_url': terms_of_service_url,
        }
        text_context = {
            'user_name': user_obj.get_full_name,
        }
        email_subject = "Filmhobo Plan Change Notification"
        email_body_text = render_to_string(
            "payment_receipts/email_receipt.txt", text_context, request
        )
        email_body_html = render_to_string(
            "payment_receipts/plan_change_email.html",
            html_context, request
        )
        recipient_email = user_obj.email
        email_recipients = [recipient_email]
        email_from = getattr(
            settings, "PAYPAL_SENDER_EMAIL",
        )
        email_from_obj = FilmHoboSenderEmail.objects.get(email=email_from)
        success = send_mail(
            subject=email_subject,
            message=email_body_text,
            from_email=email_from,
            recipient_list=email_recipients,
            html_message=email_body_html,
        )
        email_record_obj = EmailRecord.objects.create(
            sender=email_from_obj,
            recipient=user_obj,
            email=user_obj.email,
            subject=email_subject,
            sent=success,
        )
        serialized_obj_dict = {
            "when": email_record_obj.when,
            "sender": email_record_obj.sender.id,
            "recipient": email_record_obj.recipient.id,
            "email": email_record_obj.email,
            "subject": email_record_obj.subject,
            "sent": email_record_obj.sent
        }
        serializer = EmailRecordSerializer(data=serialized_obj_dict)
        if serializer.is_valid():
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
