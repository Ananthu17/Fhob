from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.utils import timezone
from django.views.generic.base import View

from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from datetimerange import DateTimeRange

from hobo_user.models import HoboPaymentsDetails, IndiePaymentDetails, \
    ProPaymentDetails, CompanyPaymentDetails, PromoCode
from .models import PaymentOptions
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
                        "annual_pro": "", "annual_company": "",
                        "tax": "", "free_evaluation_time": "",
                        "auto_renew": ""
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
        final_result = {"monthly_hobo": "", "monthly_indie": "",
                        "monthly_pro": "", "monthly_company": "",
                        "annual_hobo": "", "annual_indie": "",
                        "annual_pro": "", "annual_company": "",
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

        try:
            PaymentOptions.objects.first().__dict__

            try:
                float(data['tax'])
                if data['tax'] == "":
                    final_result['tax'] = PaymentOptions.objects.first().__dict__['tax']
                elif (float(data['tax']) < 0.0) or (float(data['tax']) > 100.0):
                    return Response(
                            {"status": "failure",
                             "tax": "please enter a valid number between 0 and 100"
                             }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    final_result['tax'] = float(data['tax'])
                    final_result['monthly_hobo'] = final_result['monthly_hobo'] + \
                        (final_result['monthly_hobo'] * (float(data['tax']) / 100.0))
                    final_result['monthly_indie'] = final_result['monthly_indie'] + \
                        (final_result['monthly_indie'] * (float(data['tax']) / 100.0))
                    final_result['monthly_pro'] = final_result['monthly_pro'] + \
                        (final_result['monthly_pro'] * (float(data['tax']) / 100.0))
                    final_result['monthly_company'] = final_result['monthly_company'] + \
                        (final_result['monthly_company'] * (float(data['tax']) / 100.0))
                    final_result['annual_hobo'] = final_result['annual_hobo'] + \
                        (final_result['annual_hobo'] * (float(data['tax']) / 100.0))
                    final_result['annual_indie'] = final_result['annual_indie'] + \
                        (final_result['annual_indie'] * (float(data['tax']) / 100.0))
                    final_result['annual_pro'] = final_result['annual_pro'] + \
                        (final_result['annual_pro'] * (float(data['tax']) / 100.0))
                    final_result['annual_company'] = final_result['annual_company'] + \
                        (final_result['annual_company'] * (float(data['tax']) / 100.0))
            except ValueError:
                return Response(
                        {"status": "failure",
                         "tax": "please enter a valid number"
                         }, status=status.HTTP_400_BAD_REQUEST)

            try:
                int(data['free_evaluation_time'])
                if data['free_evaluation_time'] == "":
                    final_result['free_evaluation_time'] = PaymentOptions.objects.first().__dict__['free_evaluation_time']
                elif int(data['free_evaluation_time']) == 0:
                    final_result['free_evaluation_time'] = '0'
                else:
                    final_result['free_evaluation_time'] = data['free_evaluation_time']
            except ValueError:
                return Response(
                    {"status": "failure",
                     "free_evaluation_time": "please enter a valid number"
                     }, status=status.HTTP_400_BAD_REQUEST)

            if data['auto_renew'] == "":
                final_result['auto_renew'] = PaymentOptions.objects.first().__dict__['auto_renew']
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
                annual_amount=float(final_result['annual_hobo']),
                estimated_tax=float(final_result['tax']))
            IndiePaymentDetails.objects.all().update(
                free_days=final_result['free_evaluation_time'],
                monthly_amount=float(final_result['monthly_indie']),
                annual_amount=float(final_result['annual_indie']),
                estimated_tax=float(final_result['tax']))
            ProPaymentDetails.objects.all().update(
                free_days=final_result['free_evaluation_time'],
                monthly_amount=float(final_result['monthly_pro']),
                annual_amount=float(final_result['annual_pro']),
                estimated_tax=float(final_result['tax']))
            CompanyPaymentDetails.objects.all().update(
                free_days=final_result['free_evaluation_time'],
                monthly_amount=float(final_result['monthly_company']),
                annual_amount=float(final_result['annual_company']),
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


class CalculateDiscountAPI(APIView):
    """
    API for calculateing the discount
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        try:
            data = request.data
            promocode_obj = PromoCode.objects.get(promo_code=data['promocode'])
            current_date_time = timezone.now()
            time_range = DateTimeRange(
                promocode_obj.valid_from, promocode_obj.valid_to)
            if current_date_time in time_range:
                if promocode_obj.amount_type == 'flat_amount':
                    final_amount = float(data['amount']) - \
                        float(promocode_obj.amount)
                else:
                    final_amount = float(data['amount']) - \
                        (float(data['amount']) * (float(promocode_obj.amount) / 100.0))
                return Response({"status": "success",
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
