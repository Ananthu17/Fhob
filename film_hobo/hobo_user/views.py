import ast
import json
import requests
import datetime
from django.utils import timezone
from authemail.models import SignupCode

from django.conf import settings
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.views import LoginView as DjangoLogin
from django.contrib.auth.views import LogoutView as DjangoLogout
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib import messages
from django.views.generic import TemplateView

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_auth.registration.views import RegisterView
from rest_framework.authtoken.models import Token
from rest_auth.views import LoginView as AuthLoginView
from rest_auth.views import LogoutView as AuthLogoutView
from rest_auth.views import PasswordChangeView as AuthPasswordChangeView


from authemail.views import SignupVerify

from .forms import SignUpForm, LoginForm, SignUpIndieForm, \
    SignUpFormCompany, SignUpProForm, ChangePasswordForm
from .models import CustomUser, IndiePaymentDetails, ProPaymentDetails, \
                    PromoCode
from .serializers import CustomUserSerializer, RegisterSerializer, \
    RegisterIndieSerializer, TokenSerializer, RegisterProSerializer, \
    SignupCodeSerializer, PaymentPlanSerializer, IndiePaymentSerializer, \
    ProPaymentSerializer, PromoCodeSerializer, GeneralSettingsSerializer, \
    RegisterCompanySerializer


class ExtendedLoginView(AuthLoginView):

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data,
                                              context={'request': request})
        self.serializer.is_valid(raise_exception=True)
        self.login()
        return self.get_response()


class ExtendedLogoutView(AuthLogoutView):

    def get(self, request, *args, **kwargs):
        if getattr(settings, 'ACCOUNT_LOGOUT_ON_GET', False):
            response = self.logout(request)
        else:
            response = self.http_method_not_allowed(request, *args, **kwargs)
        return self.finalize_response(request, response, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.logout(request)


class CustomUserLogin(DjangoLogin):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'user_pages/login.html'

    def get(self, request):
        if request.user.is_anonymous:
            form = LoginForm()
            return render(request, 'user_pages/login.html', {'form': form})
        else:
            return render(request, 'user_pages/user_home.html',
                          {'user': request.user})

    def post(self, request):
        form = LoginForm(data=request.POST)
        input_json_data_dict = ast.literal_eval(json.dumps(request.POST))
        input_json_data_dict['email'] = input_json_data_dict['username']
        del input_json_data_dict['username']
        if form.is_valid():
            email = input_json_data_dict['email']
            password = input_json_data_dict['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return render(request, 'user_pages/user_home.html',
                              {'user': user})
            else:
                return HttpResponse(
                    'Unable to log in with provided credentials.')
        else:
            return render(request, 'user_pages/login.html', {'form': form})


class CustomUserLogout(DjangoLogout):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'user_pages/logout.html'

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class ExtendedRegisterView(RegisterView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        # data_to_serialize = request.data
        # if data_to_serialize['i_agree'] == 'on':
        #     data_to_serialize['i_agree'] = True
        # serializer = self.get_serializer(data=data_to_serialize)
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid()
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(self.get_response_data(user),
                        status=status.HTTP_201_CREATED,
                        headers=headers)


class ExtendedRegisterCompanyView(RegisterView):
    serializer_class = RegisterCompanySerializer

    def create(self, request, *args, **kwargs):
        user_input_data = request.data
        user_input_data['membership'] = CustomUser.MEMBERSHIP_CHOICES[3][0]
        serializer = RegisterCompanySerializer(data=user_input_data)
        serializer.is_valid()
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(self.get_response_data(user),
                        status=status.HTTP_201_CREATED,
                        headers=headers)


class ExtendedRegisterIndieView(RegisterView):
    serializer_class = RegisterIndieSerializer

    def create(self, request, *args, **kwargs):
        serializer = RegisterIndieSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(self.get_response_data(user),
                        status=status.HTTP_201_CREATED,
                        headers=headers)


class ExtendedRegisterProView(RegisterView):
    serializer_class = RegisterProSerializer

    def create(self, request, *args, **kwargs):
        serializer = RegisterProSerializer(data=request.data)
        serializer.is_valid()
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(self.get_response_data(user),
                        status=status.HTTP_201_CREATED,
                        headers=headers)


class CustomUserSignupHobo(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'user_pages/signup_hobo.html'

    def get(self, request):
        form = SignUpForm()
        return render(request, 'user_pages/signup_hobo.html', {'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)
        must_validate_email = getattr(
            settings, "AUTH_EMAIL_VERIFICATION", True)
        if form.is_valid():
            customuser_username = request.POST['email']
            if not request.POST._mutable:
                request.POST._mutable = True
            request.POST['username'] = customuser_username
            user_response = requests.post(
                            'http://127.0.0.1:8000/hobo_user/registration/',
                            data=json.dumps(request.POST),
                            headers={'Content-type': 'application/json'})
            if user_response.status_code == 201:
                new_user = CustomUser.objects.get(
                           email=request.POST['email'])

                if must_validate_email:
                    ipaddr = self.request.META.get('REMOTE_ADDR', '0.0.0.0')
                    signup_code = SignupCode.objects.create_signup_code(
                        new_user, ipaddr)
                    signup_code.send_signup_email()

                return render(request,
                              'user_pages/user_email_verification.html',
                              {'user': new_user})
            else:
                return HttpResponse('Could not save data')
        return render(request, 'user_pages/signup_hobo.html', {'form': form})

    class Meta:
        model = get_user_model()


class HomePage(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'user_pages/user_home.html'

    def get(self, request):
        return Response({})


class CustomUserList(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'user_pages/custom_user_list.html'

    def get(self, request):
        queryset = CustomUser.objects.all()
        return Response({'profiles': queryset})


class CustomUserDetail(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'profile_detail.html'

    def get(self, request, pk):
        profile = get_object_or_404(CustomUser, pk=pk)
        serializer = CustomUserSerializer(profile)
        return Response({'serializer': serializer, 'profile': profile})

    def post(self, request, pk):
        profile = get_object_or_404(CustomUser, pk=pk)
        serializer = CustomUserSerializer(profile, data=request.data)
        if not serializer.is_valid():
            return Response({'serializer': serializer, 'profile': profile})
        serializer.save()
        return redirect('profile-list')


class ChooseMembershipPage(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'user_pages/choose_your_membership.html'

    def get(self, request):
        return Response({})


class CustomUserSignupIndieView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'user_pages/signup_indie.html'

    def get(self, request):
        form = SignUpIndieForm()
        return render(request, 'user_pages/signup_indie.html',
                      {'form': form})

    def post(self, request):
        form = SignUpIndieForm(request.POST)
        must_validate_email = getattr(
            settings, "AUTH_EMAIL_VERIFICATION", True)
        if form.is_valid():
            customuser_username = request.POST['email']
            print(request.POST)
            if not request.POST._mutable:
                request.POST._mutable = True
            request.POST['username'] = customuser_username
            user_response = requests.post(
                'http://127.0.0.1:8000/hobo_user/registration_indie/',
                data=json.dumps(request.POST),
                headers={'Content-type': 'application/json'})
            if user_response.status_code == 201:
                new_user = CustomUser.objects.get(
                           email=request.POST['email'])
                if must_validate_email:
                    ipaddr = self.request.META.get('REMOTE_ADDR', '0.0.0.0')
                    signup_code = SignupCode.objects.create_signup_code(
                            new_user, ipaddr)
                    signup_code.send_signup_email()

                return render(request,
                              'user_pages/user_email_verification.html',
                              {'user': new_user})
            else:
                return HttpResponse('Could not save data')
        return render(request, 'user_pages/signup_indie.html',
                      {'form': form})

    class Meta:
        model = get_user_model()


class CustomUserSignupProView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'user_pages/signup_pro.html'

    def get(self, request):
        form = SignUpProForm()
        return render(request, 'user_pages/signup_pro.html',
                      {'form': form})

    def post(self, request):
        form = SignUpProForm(request.POST)
        must_validate_email = getattr(
            settings, "AUTH_EMAIL_VERIFICATION", True)
        if form.is_valid():
            json_response = json.dumps(request.POST)
            json_dict = ast.literal_eval(json_response)
            guild_membership_id_response = form.cleaned_data[
                          'guild_membership_id']

            guild_membership_ids = []
            for guild_id in guild_membership_id_response:
                guild_membership_ids.append(str(guild_id.id))
            json_dict["guild_membership_id"] = guild_membership_ids

            customuser_username = request.POST['email']
            if not request.POST._mutable:
                request.POST._mutable = True
            request.POST['username'] = customuser_username
            user_response = requests.post(
                'http://127.0.0.1:8000/hobo_user/registration_pro/',
                data=json.dumps(json_dict),
                headers={'Content-type': 'application/json'})
            if user_response.status_code == 201:
                new_user = CustomUser.objects.get(
                           email=request.POST['email'])
                if must_validate_email:
                    ipaddr = self.request.META.get('REMOTE_ADDR', '0.0.0.0')
                    signup_code = SignupCode.objects.create_signup_code(
                            new_user, ipaddr)
                    signup_code.send_signup_email()

                return render(request,
                              'user_pages/user_email_verification.html',
                              {'user': new_user})
            else:
                return HttpResponse('Could not save data')
        return render(request, 'user_pages/signup_pro.html',
                      {'form': form})

    class Meta:
        model = get_user_model()


class CustomUserSignupCompany(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'user_pages/signup_company.html'

    def get(self, request):
        form = SignUpFormCompany()
        return render(request, 'user_pages/signup_company.html',
                      {'form': form})


class SendEmailVerificationView(APIView):
    serializer_class = TokenSerializer

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            must_validate_email = getattr(settings,
                                          'AUTH_EMAIL_VERIFICATION', True)
            # key = request.POST['key']
            key = serializer.data['key']
            if must_validate_email:
                user_token = Token.objects.get(key=key)
                user = user_token.user
                ipaddr = self.request.META.get('REMOTE_ADDR', '0.0.0.0')
                signup_code = SignupCode.objects.create_signup_code(
                            user, ipaddr)
                signup_code.send_signup_email()
                response = {'message': 'Email send', 'signup_code':
                            signup_code.code}

            else:
                response = {'message': 'Email not send'}
        else:
            response = {'message': 'Invalid data'}
        return Response(response)


class EmailVerificationStatusView(APIView):
    serializer_class = SignupCodeSerializer

    def post(self, request):
        serializer = SignupCodeSerializer(data=request.data)
        if serializer.is_valid():
            # code = request.POST['code']
            code = serializer.data['code']
            try:
                code = SignupCode.objects.get(code=code)
                if code:
                    response = {'verified': False}
            except SignupCode.DoesNotExist:
                response = {'verified': True}
        else:
            response = {'vefified': False, 'message': 'Invalid Data'}
        return Response(response)


class ExtendedSignupVerify(SignupVerify):

    def get(self, request, format=None):
        code = request.GET.get('code', '')
        verified = SignupCode.objects.set_user_is_verified(code)
        email = ""
        if verified:
            try:
                signup_code = SignupCode.objects.get(code=code)
                email = signup_code.user
                user_membership = CustomUser.objects.get(
                                  email=email).membership
                signup_code.delete()
            except SignupCode.DoesNotExist:
                pass
            content = {'message': 'Email address verified.', 'status':
                       status.HTTP_200_OK, 'email': email, 'user_membership':
                       user_membership}
            return render(request,
                          'user_pages/email_verification_success.html',
                          {'content': content})
        else:
            content = {'message': 'Invalid Link', 'status':
                       status.HTTP_400_BAD_REQUEST}
            return render(request,
                          'user_pages/email_verification_success.html',
                          {'content': content})


class PaymentPlanAPI(APIView):
    serializer_class = PaymentPlanSerializer

    def post(self, request):
        serializer = PaymentPlanSerializer(data=request.data)
        if serializer.is_valid():
            data_dict = serializer.data
            email = data_dict['email']
            user = CustomUser.objects.get(email=email)
            if 'payment_plan' in data_dict:
                payment_plan = data_dict['payment_plan']
                if payment_plan == 'monthly':
                    user.payment_plan = CustomUser.MONTHLY
                if payment_plan == 'annually':
                    user.payment_plan = CustomUser.ANNUALLY
                user.save()
                response = {'message': 'Payment Plan Added', 'status':
                            status.HTTP_200_OK, 'email': email}
            else:
                user.payment_plan = CustomUser.FREE
                user.save()
                response = {'message': 'Payment Plan Empty', 'status':
                            status.HTTP_400_BAD_REQUEST}
        else:
            response = {'message': serializer.errors,
                        'status': status.HTTP_400_BAD_REQUEST}
        return Response(response)


class IndiePaymentDetailsAPI(APIView):
    serializer_class = IndiePaymentSerializer

    def get(self, request):
        payment_details = IndiePaymentDetails.get_solo()
        serializer = IndiePaymentSerializer(payment_details)
        return Response(serializer.data)


class ProPaymentDetailsAPI(APIView):
    serializer_class = ProPaymentSerializer

    def get(self, request):
        payment_details = ProPaymentDetails.get_solo()
        serializer = ProPaymentSerializer(payment_details)
        return Response(serializer.data)


class SelectPaymentPlanIndieView(TemplateView):
    template_name = 'user_pages/payment_plan_indie.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_response = requests.get(
                'http://127.0.0.1:8000/hobo_user/indie_payment_details_api/',
                headers={'Content-type': 'application/json'})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        payment_details = ast.literal_eval(dict_str)
        context['monthly_amount'] = payment_details['monthly_amount']
        context['annual_amount'] = payment_details['annual_amount']
        return context

    def post(self, request, *args, **kwargs):
        user_response = requests.post(
                    'http://127.0.0.1:8000/hobo_user/select-payment-plan-api/',
                    data=json.dumps(request.POST),
                    headers={'Content-type': 'application/json'})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        response = ast.literal_eval(dict_str)
        email = response['email']
        return HttpResponseRedirect("/hobo_user/payment_indie?email="+email)


class SelectPaymentPlanProView(TemplateView):
    template_name = 'user_pages/payment_plan_pro.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_response = requests.get(
                'http://127.0.0.1:8000/hobo_user/pro_payment_details_api/',
                headers={'Content-type': 'application/json'})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        payment_details = ast.literal_eval(dict_str)
        context['monthly_amount'] = payment_details['monthly_amount']
        context['annual_amount'] = payment_details['annual_amount']
        return context

    def post(self, request, *args, **kwargs):
        user_response = requests.post(
                            'http://127.0.0.1:8000/hobo_user/select-payment-plan-api/',
                            data=json.dumps(request.POST),
                            headers={'Content-type': 'application/json'})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        response = ast.literal_eval(dict_str)
        email = response['email']
        return HttpResponseRedirect("/hobo_user/payment_pro?email="+email)


class PaymentIndieView(TemplateView):
    template_name = 'user_pages/payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.request.GET.get('email')
        user = CustomUser.objects.get(email=email)
        user_response = requests.get(
                'http://127.0.0.1:8000/hobo_user/indie_payment_details_api/',
                headers={'Content-type': 'application/json'})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        payment_details = ast.literal_eval(dict_str)
        context['payment_details'] = payment_details
        context['payment_plan'] = user.payment_plan
        return context


class PaymentProView(TemplateView):
    template_name = 'user_pages/payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.request.GET.get('email')
        user = CustomUser.objects.get(email=email)
        user_response = requests.get(
                'http://127.0.0.1:8000/hobo_user/pro_payment_details_api/',
                headers={'Content-type': 'application/json'})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        payment_details = ast.literal_eval(dict_str)
        context['payment_details'] = payment_details
        context['payment_plan'] = user.payment_plan
        return context


class CheckPromoCodeAPI(APIView):
    serializer_class = PromoCodeSerializer

    def post(self, request):
        serializer = PromoCodeSerializer(data=request.data)
        if serializer.is_valid():
            data_dict = serializer.data
            promocode = data_dict['promo_code']
            try:
                promocode = PromoCode.objects.get(promo_code=promocode)
                life_span = promocode.life_span
                validity = promocode.valid_from + datetime.timedelta(
                        days=life_span)
                today = timezone.now()
                if today <= validity:
                    response = {'message': 'Promo Code Applied', 'status':
                                status.HTTP_200_OK}
                else:
                    response = {'message': 'Promo Code Expired', 'status':
                                status.HTTP_200_OK}
            except PromoCode.DoesNotExist:
                response = {'message': 'Invalid Promo Code', 'status':
                            status.HTTP_200_OK}
        else:
            response = {'message': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}

        return Response(response)


class GeneralSettingsUpdateAPI(APIView):
    serializer_class = GeneralSettingsSerializer

    def post(self, request):
        serializer = GeneralSettingsSerializer(data=request.data)
        if serializer.is_valid():
            data_dict = serializer.data
            print("data_dict", data_dict)
            try:
                id = data_dict['user_id']
                user = CustomUser.objects.get(pk=id)
                if 'first_name' in data_dict:
                    user.first_name = data_dict['first_name']
                if 'middle_name' in data_dict:
                    user.middle_name = data_dict['middle_name']
                if 'last_name' in data_dict:
                    user.last_name = data_dict['last_name']
                if 'email' in data_dict:
                    email = data_dict['email']
                    try:
                        all_users = CustomUser.objects.exclude(pk=id)
                        match = all_users.get(email=email)
                        if match:
                            response = {
                             'email_validation_error':
                             'User with this email id already exists',
                             'status': status.HTTP_400_BAD_REQUEST
                              }
                    except CustomUser.DoesNotExist:
                        user.email = data_dict['email']
                        user.save()
                        response = {'message': 'General Settings Updated',
                                    'status': status.HTTP_200_OK}
                else:
                    user.save()
                    response = {'message': 'General Settings Updated',
                                'status': status.HTTP_200_OK}
            except CustomUser.DoesNotExist:
                response = {'errors': 'Invalid id', 'status':
                            status.HTTP_400_BAD_REQUEST}
        else:
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}

        return Response(response)


class SettingsView(TemplateView):
    template_name = 'user_pages/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        json_response = json.dumps(request.POST)
        json_dict = ast.literal_eval(json_response)
        json_dict['user_id'] = user.id
        user_response = requests.post(
                            'http://127.0.0.1:8000/hobo_user/general-settings-update-api/',
                            data=json.dumps(json_dict),
                            headers={'Content-type': 'application/json'})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        response = ast.literal_eval(dict_str)
        response = dict(response)
        error_messages = dict()

        if 'errors' in response:
            if 'first_name' in response['errors']:
                error_messages['first_name'] = "This field is required"
            if 'last_name' in response['errors']:
                error_messages['last_name'] = "This field is required"
            if 'email' in response['errors']:
                error_messages['email'] = "This field is required"
        elif 'email_validation_error' in response:
            error_messages['email'] = response['email_validation_error']
        else:
            messages.success(self.request, 'General Settings Updated')
        user = self.request.user
        return render(request, 'user_pages/settings.html',
                      {'message': error_messages, 'user': user})


class ChangePasswordView(AuthPasswordChangeView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        print("request.user", self.request.user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": _("New password has been saved.")})
