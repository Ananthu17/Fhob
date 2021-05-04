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
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_auth.registration.views import RegisterView
from rest_framework.authtoken.models import Token
from rest_auth.views import LoginView as AuthLoginView
from rest_auth.views import LogoutView as AuthLogoutView
from rest_auth.views import PasswordChangeView as AuthPasswordChangeView
from rest_auth.views import PasswordResetView as AuthPasswordResetView
from rest_auth.views import PasswordResetConfirmView as AuthPasswordResetConfirmView


from authemail.views import SignupVerify

from .forms import SignUpForm, LoginForm, SignUpIndieForm, \
    SignUpFormCompany, SignUpProForm, ChangePasswordForm, \
    DisableAccountForm, BlockMemberForm, NotificationAccountSettingsForm, \
    ForgotPasswordEmailForm, ResetPasswordForm

from .models import CustomUser, IndiePaymentDetails, ProPaymentDetails, \
                    PromoCode, Country, DisabledAccount, CustomUserSettings, \
                    CompanyPaymentDetails

from .serializers import CustomUserSerializer, RegisterSerializer, \
    RegisterIndieSerializer, TokenSerializer, RegisterProSerializer, \
    SignupCodeSerializer, PaymentPlanSerializer, IndiePaymentSerializer, \
    ProPaymentSerializer, PromoCodeSerializer, GeneralSettingsSerializer, \
    RegisterCompanySerializer, DisableAccountSerializer, \
    PrivacySettingsSerializer, EnableAccountSerializer, \
    TrackingAccountSettingsSerializer, BlockMembersSerializer, \
    NotificationAccountSettingsSerializer, CompanyPaymentSerializer

CHECKBOX_MAPPING = {'on': True,
                    'off': False}


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
        obj = CustomUserSettings()
        obj.user = user
        obj.save()

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
        obj = CustomUserSettings()
        obj.user = user
        obj.save()

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
        obj = CustomUserSettings()
        obj.user = user
        obj.save()

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
        obj = CustomUserSettings()
        obj.user = user
        obj.save()

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

    def post(self, request):
        form = SignUpFormCompany(request.POST)
        must_validate_email = getattr(
            settings, "AUTH_EMAIL_VERIFICATION", True)
        if form.is_valid():
            # json_response = json.dumps(request.POST)
            # json_dict = ast.literal_eval(json_response)
            customuser_username = request.POST['email']
            if not request.POST._mutable:
                request.POST._mutable = True
            request.POST['username'] = customuser_username
            user_response = requests.post(
                'http://127.0.0.1:8000/hobo_user/registration_company/',
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
        else:
            print(form.errors)
        return render(request, 'user_pages/signup_company.html',
                      {'form': form})

    class Meta:
        model = get_user_model()


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
    permission_classes = (IsAuthenticated,)

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
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        payment_details = IndiePaymentDetails.get_solo()
        serializer = IndiePaymentSerializer(payment_details)
        return Response(serializer.data)


class ProPaymentDetailsAPI(APIView):
    serializer_class = ProPaymentSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        payment_details = ProPaymentDetails.get_solo()
        serializer = ProPaymentSerializer(payment_details)
        return Response(serializer.data)


class CompanyPaymentDetailsAPI(APIView):
    serializer_class = CompanyPaymentSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        payment_details = CompanyPaymentDetails.get_solo()
        serializer = CompanyPaymentSerializer(payment_details)
        return Response(serializer.data)


class SelectPaymentPlanIndieView(TemplateView):
    template_name = 'user_pages/payment_plan_indie.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.request.GET.get('email')
        user = CustomUser.objects.get(email=email)
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        user_response = requests.get(
                'http://127.0.0.1:8000/hobo_user/indie_payment_details_api/',
                headers={'Content-type': 'application/json',
                         'Authorization': token})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        payment_details = ast.literal_eval(dict_str)
        context['monthly_amount'] = payment_details['monthly_amount']
        context['annual_amount'] = payment_details['annual_amount']
        return context

    def post(self, request, *args, **kwargs):
        email = self.request.POST.get('email')
        user = CustomUser.objects.get(email=email)
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        user_response = requests.post(
                    'http://127.0.0.1:8000/hobo_user/select-payment-plan-api/',
                    data=json.dumps(request.POST),
                    headers={'Content-type': 'application/json',
                             'Authorization': token})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        response = ast.literal_eval(dict_str)
        email = response['email']
        return HttpResponseRedirect("/hobo_user/payment_indie?email="+email)


class SelectPaymentPlanProView(TemplateView):
    template_name = 'user_pages/payment_plan_pro.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.request.GET.get('email')
        user = CustomUser.objects.get(email=email)
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        user_response = requests.get(
                'http://127.0.0.1:8000/hobo_user/pro_payment_details_api/',
                headers={'Content-type': 'application/json',
                         'Authorization': token})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        payment_details = ast.literal_eval(dict_str)
        context['monthly_amount'] = payment_details['monthly_amount']
        context['annual_amount'] = payment_details['annual_amount']
        return context

    def post(self, request, *args, **kwargs):
        email = self.request.POST.get('email')
        user = CustomUser.objects.get(email=email)
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        user_response = requests.post(
                            'http://127.0.0.1:8000/hobo_user/select-payment-plan-api/',
                            data=json.dumps(request.POST),
                            headers={'Content-type': 'application/json',
                                     'Authorization': token})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        response = ast.literal_eval(dict_str)
        email = response['email']
        return HttpResponseRedirect("/hobo_user/payment_pro?email="+email)


class SelectPaymentPlanCompanyView(TemplateView):
    template_name = 'user_pages/payment_plan_company.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.request.GET.get('email')
        user = CustomUser.objects.get(email=email)
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        user_response = requests.get(
                'http://127.0.0.1:8000/hobo_user/company_payment_details_api/',
                headers={'Content-type': 'application/json',
                         'Authorization': token})
        print(user_response)
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        payment_details = ast.literal_eval(dict_str)
        context['monthly_amount'] = payment_details['monthly_amount']
        context['annual_amount'] = payment_details['annual_amount']
        return context

    def post(self, request, *args, **kwargs):
        email = self.request.POST.get('email')
        user = CustomUser.objects.get(email=email)
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        user_response = requests.post(
                            'http://127.0.0.1:8000/hobo_user/select-payment-plan-api/',
                            data=json.dumps(request.POST),
                            headers={'Content-type': 'application/json',
                                     'Authorization': token})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        response = ast.literal_eval(dict_str)
        email = response['email']
        return HttpResponseRedirect("/hobo_user/payment_company?email="+email)


class PaymentIndieView(TemplateView):
    template_name = 'user_pages/payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.request.GET.get('email')
        user = CustomUser.objects.get(email=email)
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        user_response = requests.get(
                'http://127.0.0.1:8000/hobo_user/indie_payment_details_api/',
                headers={'Content-type': 'application/json',
                         'Authorization': token})
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
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        user_response = requests.get(
                'http://127.0.0.1:8000/hobo_user/pro_payment_details_api/',
                headers={'Content-type': 'application/json',
                         'Authorization': token})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        payment_details = ast.literal_eval(dict_str)
        context['payment_details'] = payment_details
        context['payment_plan'] = user.payment_plan
        return context


class PaymentCompanyView(TemplateView):
    template_name = 'user_pages/payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.request.GET.get('email')
        user = CustomUser.objects.get(email=email)
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        user_response = requests.get(
                'http://127.0.0.1:8000/hobo_user/company_payment_details_api/',
                headers={'Content-type': 'application/json',
                         'Authorization': token})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        payment_details = ast.literal_eval(dict_str)
        context['payment_details'] = payment_details
        context['payment_plan'] = user.payment_plan
        return context


class CheckPromoCodeAPI(APIView):
    serializer_class = PromoCodeSerializer
    # permission_classes = (IsAuthenticated,)

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
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = GeneralSettingsSerializer(data=request.data)
        if serializer.is_valid():
            data_dict = serializer.data
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
                             ['User with this email id already exists',],
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


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'user_pages/settings.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_settings = CustomUserSettings.objects.get(user=user)

        block_member_form = BlockMemberForm
        already_blocked_users = user_settings.blocked_members.values_list(
                                'id', flat=True)
        already_blocked_users = list(already_blocked_users)
        already_blocked_users.append(self.request.user.id)
        modified_queryset = CustomUser.objects.exclude(
                            id__in=already_blocked_users)
        block_member_form.declared_fields[
            'blocked_members'].queryset = modified_queryset

        context['user_settings'] = user_settings
        context['change_password_form'] = ChangePasswordForm
        context['disable_account_form'] = DisableAccountForm
        context['notification_form'] = NotificationAccountSettingsForm(
                                        instance=user_settings)
        context['block_member_form'] = block_member_form
        context['user'] = user
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        json_response = json.dumps(request.POST)
        json_dict = ast.literal_eval(json_response)
        json_dict['user_id'] = user.id
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        user_response = requests.post(
                            'http://127.0.0.1:8000/hobo_user/general-settings-update-api/',
                            data=json.dumps(json_dict),
                            headers={'Content-type': 'application/json',
                                     'Authorization': token})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        response = ast.literal_eval(dict_str)
        response = dict(response)
        error_messages = dict()

        if 'errors' in response:
            if 'first_name' in response['errors']:
                error_messages['first_name'] = response['errors']['first_name']
            if 'last_name' in response['errors']:
                error_messages['last_name'] = response['errors']['last_name']
            if 'email' in response['errors']:
                error_messages['email'] = response['errors']['email']
            return render(request, 'user_pages/settings.html',
                          {'message': error_messages, 'user': user,
                           'change_password_form': ChangePasswordForm})
        elif 'email_validation_error' in response:
            error_messages['email'] = response['email_validation_error']
            return render(request, 'user_pages/settings.html',
                          {'message': error_messages, 'user': user,
                           'change_password_form': ChangePasswordForm})
        else:
            messages.success(self.request, 'General Settings Updated')
            return HttpResponseRedirect(reverse('hobo_user:settings'))

        return HttpResponseRedirect(reverse('hobo_user:settings'))


class ChangePasswordAPI(AuthPasswordChangeView):
    permission_classes = (IsAuthenticated,)
    # serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            user = request.user
            serializer.save()
            response = {'message':
                        'New password has been saved. Please Login to continue',
                        'status': status.HTTP_200_OK}
        else:
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST,
                        }

        return Response(response)


class ChangePasswordView(LoginRequiredMixin, TemplateView):
    template_name = 'user_pages/settings.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'
    form_class = ChangePasswordForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        change_password_form = self.form_class
        context['change_password_form'] = change_password_form
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        message = ""
        change_password_form = self.form_class
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        user_response = requests.post(
                            'http://127.0.0.1:8000/hobo_user/change-password-api/',
                            data=json.dumps(request.POST),
                            headers={'Content-type': 'application/json',
                                     'Authorization': token})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        response = ast.literal_eval(dict_str)
        response = dict(response)
        if 'message' in response:
            message = response['message']
        if 'status' in response:
            if response['status'] == 200:
                messages.success(self.request, 'Password Changed Successfully. Please login to continue')
                return HttpResponseRedirect(reverse('hobo_user:user_login'))
        return render(request, 'user_pages/settings.html',
                      {'change_password_messages': message,
                       'user': user,
                       'change_password_form': change_password_form,
                       'change_password_errors': response,
                       'disable_account_form': DisableAccountForm,
                       'block_member_form' : BlockMemberForm,
                       'notification_form': NotificationAccountSettingsForm})


class DisableAccountAPI(APIView):
    serializer_class = DisableAccountSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data_dict = serializer.data
            user = self.request.user
            user_email = user.email
            reason = data_dict['reason']
            try:
                DisabledAccount.objects.get(
                                user__email=user_email)
                response = {
                 'errors': "This account is already Disabled.",
                 'status': status.HTTP_400_BAD_REQUEST}
            except DisabledAccount.DoesNotExist:
                obj = DisabledAccount()
                obj.user = user
                obj.reason = reason
                obj.save()
                user_settings = CustomUserSettings.objects.get(user=user)
                user_settings.account_status = CustomUserSettings.DISABLED
                user_settings.save()
                response = {'message':
                            'Account Disabled',
                            'status': status.HTTP_200_OK}

        else:
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}

        return Response(response)


class DisableAccountView(LoginRequiredMixin, TemplateView):
    template_name = 'user_pages/settings.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'
    form_class = DisableAccountForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        disable_account_form = self.form_class
        context['disable_account_form'] = disable_account_form
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        disable_account_form = self.form_class
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        user_response = requests.post(
                            'http://127.0.0.1:8000/hobo_user/disable-account-api/',
                            data=json.dumps(request.POST),
                            headers={'Content-type': 'application/json',
                                     'Authorization': token})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        response = ast.literal_eval(dict_str)
        response = dict(response)
        if 'status' in response:
            if response['status'] == 200:
                messages.success(self.request, 'Account Disabled')
                return HttpResponseRedirect(reverse('hobo_user:enable-account'))
        return render(request, 'user_pages/settings.html',
                      {'disable_account_form': disable_account_form,
                       'disable_account_errors': response})


class PrivacySettingsAPI(APIView):
    serializer_class = PrivacySettingsSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data_dict = serializer.data
            user = self.request.user
            user_settings = CustomUserSettings.objects.get(user=user)
            user_settings.profile_visibility = data_dict['profile_visibility']
            user_settings.who_can_contact_me = data_dict['who_can_contact_me']
            user_settings.save()
            response = {'message': "Privacy Settings Updated", 'status':
                        status.HTTP_200_OK}
        else:
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}

        return Response(response)


class PrivacySettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'user_pages/settings.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_settings = CustomUserSettings.objects.get(user=self.request.user)
        context['user_settings'] = user_settings
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        data_dict = self.request.POST
        user_settings = CustomUserSettings.objects.get(user=self.request.user)
        privacy_setting_errors = ""

        if 'profile_visibility' in data_dict:
            profile_visibility = data_dict['profile_visibility']
            if(profile_visibility == 'members_with_rating' and 'visibility_rate' in data_dict):
                visibility_rate = data_dict['visibility_rate']
                if visibility_rate == '1':
                    visibility = CustomUserSettings.MEMBERS_WITH_RATING_1_STAR
                if visibility_rate == '2':
                    visibility = CustomUserSettings.MEMBERS_WITH_RATING_2_STAR
                if visibility_rate == '3':
                    visibility = CustomUserSettings.MEMBERS_WITH_RATING_3_STAR
                if visibility_rate == '4':
                    visibility = CustomUserSettings.MEMBERS_WITH_RATING_4_STAR
                if visibility_rate == '5':
                    visibility = CustomUserSettings.MEMBERS_WITH_RATING_5_STAR
            elif profile_visibility != 'members_with_rating':
                visibility = data_dict['profile_visibility']
            else:
                error_message = {"profile_visibility": ["Please provide ratings",]}
                return render(request, 'user_pages/settings.html',
                              {'privacy_setting_errors': error_message,
                               'disable_account_form': DisableAccountForm,
                               'change_password_form': ChangePasswordForm,
                               'user_settings': user_settings,
                               'block_member_form': BlockMemberForm,
                               'notification_form':
                               NotificationAccountSettingsForm
                               })
        else:
            visibility = ""

        if 'who_can_contact_me' in data_dict:
            contact_members = data_dict['who_can_contact_me']
            if(contact_members == 'members_with_rating' and 'rate' in data_dict):
                rate = data_dict['rate']
                if rate == '1':
                    contact_me = CustomUserSettings.MEMBERS_WITH_RATING_1_STAR
                if rate == '2':
                    contact_me = CustomUserSettings.MEMBERS_WITH_RATING_2_STAR
                if rate == '3':
                    contact_me = CustomUserSettings.MEMBERS_WITH_RATING_3_STAR
                if rate == '4':
                    contact_me = CustomUserSettings.MEMBERS_WITH_RATING_4_STAR
                if rate == '5':
                    contact_me = CustomUserSettings.MEMBERS_WITH_RATING_5_STAR
            elif contact_members != 'members_with_rating':
                contact_me = data_dict['who_can_contact_me']
            else:
                error_message = {"who_can_contact_me": ["Please provide ratings",]}
                return render(request, 'user_pages/settings.html',
                              {'privacy_setting_errors': error_message,
                               'disable_account_form': DisableAccountForm,
                               'change_password_form': ChangePasswordForm,
                               'block_member_form': BlockMemberForm,
                               'user_settings': user_settings
                               })
        else:
            contact_me = ""

        json_response = json.dumps(request.POST)
        json_dict = ast.literal_eval(json_response)
        json_dict['who_can_contact_me'] = contact_me
        json_dict['profile_visibility'] = visibility

        key = Token.objects.get(user=user).key
        token = 'Token '+key
        user_response = requests.post(
                            'http://127.0.0.1:8000/hobo_user/privacy-settings-api/',
                            data=json.dumps(json_dict),
                            headers={'Content-type': 'application/json',
                                     'Authorization': token})

        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        response = ast.literal_eval(dict_str)
        response = dict(response)
        if 'status' in response:
            if response['status'] == 200:
                messages.success(self.request, 'Privacy Settings Updated')
                return HttpResponseRedirect(reverse('hobo_user:settings'))
            else:
                privacy_setting_errors = response['errors']
        return render(request, 'user_pages/settings.html',
                      {'privacy_setting_errors': privacy_setting_errors,
                       'disable_account_form': DisableAccountForm,
                       'change_password_form': ChangePasswordForm,
                       'block_member_form' : BlockMemberForm
                      })


class EnableAccountAPI(APIView):
    serializer_class = EnableAccountSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data_dict = serializer.data
            if data_dict['account_status'] == 'enabled':
                user = self.request.user
                try:
                    user_settings = CustomUserSettings.objects.get(user=user)
                    user_settings.account_status = CustomUserSettings.ENABLED
                    try:
                        disabled_account = DisabledAccount.objects.get(user=user)
                        disabled_account.delete()
                        user_settings.save()
                        response = {'message': "Account Enabled",
                                    'status': status.HTTP_200_OK
                                    }
                    except DisabledAccount.DoesNotExist:
                        response = {'message': "Disabled Account not found",
                                    'status': status.HTTP_400_BAD_REQUEST
                                    }
                except CustomUserSettings.DoesNotExist:
                    response = {'message': "Custom User Settings not found",
                                'status': status.HTTP_400_BAD_REQUEST
                                }
            else:
                response = {'message': "Failed!!",
                            'status': status.HTTP_400_BAD_REQUEST
                            }
        else:
            response = {'message': "Invalid Serializer",
                        'errors': serializer.errors,
                        'status': status.HTTP_400_BAD_REQUEST
                        }
        return Response(response)


class EnableAccountView(LoginRequiredMixin, TemplateView):
    template_name = 'user_pages/enable-account.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        message =""
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        user_response = requests.post(
                            'http://127.0.0.1:8000/hobo_user/enable-account-api/',
                            data=json.dumps(request.POST),
                            headers={'Content-type': 'application/json',
                                     'Authorization': token})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        response = ast.literal_eval(dict_str)
        response = dict(response)
        if 'status' in response:
            if response['status'] == 200:
                messages.success(self.request, 'Account Enabled')
                return HttpResponseRedirect(reverse('hobo_user:user_home'))
            else:
                message = response['message']
        return render(request, 'user_pages/enable-account.html',
                      {'message': message})


class TrackingAccountSettingsAPI(APIView):
    serializer_class = TrackingAccountSettingsSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data_dict = serializer.data
            user = self.request.user
            user_settings = CustomUserSettings.objects.get(user=user)
            user_settings.who_can_track_me = data_dict['who_can_track_me']
            user_settings.save()
            response = {'message': "Tracking Account Settings Updated", 'status':
                        status.HTTP_200_OK}
        else:
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}

        return Response(response)


class TrackingAccountSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'user_pages/settings.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_settings = CustomUserSettings.objects.get(user=self.request.user)
        context['user_settings'] = user_settings
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        data_dict = self.request.POST
        user_settings = CustomUserSettings.objects.get(user=self.request.user)
        tracking_setting_errors = ""

        if 'who_can_track_me' in data_dict:
            who_can_track_me = data_dict['who_can_track_me']
            if(who_can_track_me == 'members_with_rating' and 'tracking_rate' in data_dict):
                tracking_rate = data_dict['tracking_rate']
                if tracking_rate == '1':
                    tracking = CustomUserSettings.MEMBERS_WITH_RATING_1_STAR
                if tracking_rate == '2':
                    tracking = CustomUserSettings.MEMBERS_WITH_RATING_2_STAR
                if tracking_rate == '3':
                    tracking = CustomUserSettings.MEMBERS_WITH_RATING_3_STAR
                if tracking_rate == '4':
                    tracking = CustomUserSettings.MEMBERS_WITH_RATING_4_STAR
                if tracking_rate == '5':
                    tracking = CustomUserSettings.MEMBERS_WITH_RATING_5_STAR
            elif who_can_track_me != 'members_with_rating':
                tracking = data_dict['who_can_track_me']
            else:
                error_message = {"who_can_track_me": ["Please provide ratings",]}
                return render(request, 'user_pages/settings.html',
                              {'tracking_setting_errors': error_message,
                               'disable_account_form': DisableAccountForm,
                               'change_password_form': ChangePasswordForm,
                               'user_settings': user_settings,
                               'block_member_form' : BlockMemberForm,
                               'notification_form': NotificationAccountSettingsForm
                               })
        else:
            tracking = ""

        json_response = json.dumps(request.POST)
        json_dict = ast.literal_eval(json_response)
        json_dict['who_can_track_me'] = tracking

        key = Token.objects.get(user=user).key
        token = 'Token '+key
        user_response = requests.post(
                            'http://127.0.0.1:8000/hobo_user/tracking-account-api/',
                            data=json.dumps(json_dict),
                            headers={'Content-type': 'application/json',
                                     'Authorization': token})

        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        response = ast.literal_eval(dict_str)
        response = dict(response)
        if 'status' in response:
            if response['status'] == 200:
                messages.success(self.request, 'Tracking Account Settings Updated')
                return HttpResponseRedirect(reverse('hobo_user:settings'))
            else:
                tracking_setting_errors = response['errors']
        return render(request, 'user_pages/settings.html',
                      {'tracking_setting_errors': tracking_setting_errors,
                       'disable_account_form': DisableAccountForm,
                       'change_password_form': ChangePasswordForm,
                       'block_member_form' : BlockMemberForm
                      })


class BlockMembersAPI(APIView):
    serializer_class = BlockMembersSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        blocked_members = list()
        response = dict()
        user_settings = CustomUserSettings.objects.get(user=user)
        if user_settings.blocked_members:
            for obj in user_settings.blocked_members.all():
                blocked_members.append(obj.id)
            response['blocked_members'] = blocked_members
        return Response(response)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data_dict = serializer.data
            block_user_id = data_dict['user_id']
            try:
                block_user = CustomUser.objects.get(pk=block_user_id)
                user = self.request.user
                user_settings = CustomUserSettings.objects.get(user=user)
                blocked_members = user_settings.blocked_members.all()
                blocked_members = list(blocked_members)
                if block_user in blocked_members:
                    response = {'errors': 'Already blocked user.',
                                'status': status.HTTP_400_BAD_REQUEST}
                else:
                    blocked_members.append(block_user)
                    user_settings.blocked_members.set(blocked_members)
                    user_settings.save()

                    response = {'message': "Blocked %s" % (
                                block_user.email),
                                'status': status.HTTP_200_OK}
            except CustomUser.DoesNotExist:
                response = {'errors': 'Invalid user id',
                            'status': status.HTTP_400_BAD_REQUEST}
        else:
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}

        return Response(response)


class BlockMembersView(LoginRequiredMixin, TemplateView):
    template_name = 'user_pages/settings.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'
    form_class = BlockMemberForm()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_settings = CustomUserSettings.objects.get(user=user)
        form = self.form_class()
        context['block_member_form'] = form
        context['user_settings'] = user_settings
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        user_settings = CustomUserSettings.objects.get(user=self.request.user)
        block_user_errors = ""
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        block_user = self.request.POST.get('blocked_members')
        block_user_obj = CustomUser.objects.get(id=block_user)
        json_response = json.dumps(request.POST)
        json_dict = ast.literal_eval(json_response)
        json_dict['user_id'] = block_user

        user_response = requests.post(
                            'http://127.0.0.1:8000/hobo_user/block-members-api/',
                            data=json.dumps(json_dict),
                            headers={'Content-type': 'application/json',
                                     'Authorization': token})

        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        response = ast.literal_eval(dict_str)
        response = dict(response)
        if 'status' in response:
            if response['status'] == 200:
                messages.success(self.request, 'Blocked user %s %s' % (
                    block_user_obj.first_name, block_user_obj.last_name))
                return HttpResponseRedirect(reverse('hobo_user:settings'))
            else:
                block_user_errors = response['errors']
        return render(request, 'user_pages/settings.html',
                      {'block_user_errors': block_user_errors,
                       'disable_account_form': DisableAccountForm,
                       'change_password_form': ChangePasswordForm,
                       'user_settings': user_settings,
                       'block_member_form': BlockMemberForm,
                       'notification_form': NotificationAccountSettingsForm
                       })


class UnBlockMembersAPI(APIView):
    serializer_class = BlockMembersSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data_dict = serializer.data
            block_user_id = data_dict['user_id']
            try:
                block_user = CustomUser.objects.get(pk=block_user_id)
                user = self.request.user
                user_settings = CustomUserSettings.objects.get(user=user)
                blocked_members = user_settings.blocked_members.all()
                blocked_members = list(blocked_members)
                if block_user not in blocked_members:
                    response = {'errors': 'This user is not blocked',
                                'status': status.HTTP_400_BAD_REQUEST}
                else:
                    blocked_members.remove(block_user)
                    user_settings.blocked_members.set(blocked_members)
                    user_settings.save()

                    response = {'message': "Un Blocked %s" % (
                                block_user.email),
                                'status': status.HTTP_200_OK}
            except CustomUser.DoesNotExist:
                response = {'errors': 'Invalid user id',
                            'status': status.HTTP_400_BAD_REQUEST}
        else:
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}

        return Response(response)


class NotificationAccountSettingsAPI(APIView):
    serializer_class = NotificationAccountSettingsSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data_dict = serializer.data
            user = self.request.user
            user_settings = CustomUserSettings.objects.get(user=user)
            if 'someone_tracks_me' in data_dict:
                user_settings.someone_tracks_me = data_dict['someone_tracks_me']
            if 'change_in_my_or_project_rating' in data_dict:
                user_settings.change_in_my_or_project_rating = data_dict[
                                        'change_in_my_or_project_rating']
            if 'review_for_my_work_or_project' in data_dict:
                user_settings.review_for_my_work_or_project = data_dict[
                                        'review_for_my_work_or_project']
            if 'new_project' in data_dict:
                user_settings.new_project = data_dict['new_project']
            if 'friend_request' in data_dict:
                user_settings.friend_request = data_dict['friend_request']
            if 'match_for_my_Interest' in data_dict:
                user_settings.match_for_my_Interest = data_dict[
                                        'match_for_my_Interest']
            user_settings.save()
            response = {'message': "Notification Account Settings Updated",
                        'status': status.HTTP_200_OK}
        else:
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}

        return Response(response)


class NotificationAccountSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'user_pages/settings.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'
    form_class = NotificationAccountSettingsForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_settings = CustomUserSettings.objects.get(user=user)
        context['notification_form'] = self.form_class(instance=user_settings)
        context['user_settings'] = user_settings
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        user_settings = CustomUserSettings.objects.get(user=self.request.user)
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        someone_tracks_me = CHECKBOX_MAPPING.get(
                            request.POST.get('someone_tracks_me', 'off'))
        change_in_my_or_project_rating = CHECKBOX_MAPPING.get(
                            request.POST.get(
                                'change_in_my_or_project_rating',
                                'off'))
        review_for_my_work_or_project = CHECKBOX_MAPPING.get(
                            request.POST.get(
                                'review_for_my_work_or_project',
                                'off'))
        new_project = CHECKBOX_MAPPING.get(
                            request.POST.get('new_project', 'off'))
        friend_request = CHECKBOX_MAPPING.get(
                            request.POST.get('friend_request', 'off'))
        match_for_my_Interest = CHECKBOX_MAPPING.get(
                            request.POST.get('match_for_my_Interest', 'off'))

        json_response = json.dumps(request.POST)
        json_dict = ast.literal_eval(json_response)
        json_dict['someone_tracks_me'] = someone_tracks_me
        json_dict['change_in_my_or_project_rating'] = change_in_my_or_project_rating
        json_dict['review_for_my_work_or_project'] = review_for_my_work_or_project
        json_dict['new_project'] = new_project
        json_dict['friend_request'] = friend_request
        json_dict['match_for_my_Interest'] = match_for_my_Interest

        user_response = requests.post(
            'http://127.0.0.1:8000/hobo_user/notification-account-settings-api/',
            data=json.dumps(json_dict),
            headers={'Content-type': 'application/json',
                     'Authorization': token
                     })
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        response = ast.literal_eval(dict_str)
        response = dict(response)
        if 'status' in response:
            if response['status'] == 200:
                messages.success(
                    self.request,
                    'Notification Account Settings Updated'
                    )
                return HttpResponseRedirect(reverse('hobo_user:settings'))
            else:
                notification_errors = response['errors']
        return render(request, 'user_pages/settings.html',
                      {'notification_errors': notification_errors,
                       'disable_account_form': DisableAccountForm,
                       'change_password_form': ChangePasswordForm,
                       'user_settings': user_settings,
                       'block_member_form': BlockMemberForm,
                       'notification_form': NotificationAccountSettingsForm
                       })


class ForgotPasswordAPI(AuthPasswordResetView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        # Create a serializer with request.data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Return the success message with OK HTTP status
        return Response(
            {"detail": "Password reset e-mail has been sent."},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(AuthPasswordResetConfirmView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        print("here-----------------")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password has been reset with the new password.",
             "status": status.HTTP_200_OK}
        )


class ForgotPasswordView(TemplateView):
    template_name = 'registration/password_reset.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'
    form_class = ForgotPasswordEmailForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class
        user_response = requests.post(
                            'http://127.0.0.1:8000/hobo_user/forgot-password-api/',
                            data=json.dumps(request.POST),
                            headers={'Content-type': 'application/json'})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        response = ast.literal_eval(dict_str)
        response = dict(response)
        if 'status' in response:
            if response['status'] == 200:
                return HttpResponseRedirect(reverse('hobo_user:forgot-password'))
        return render(request, 'registration/password_reset.html',
                      {'response': response,
                       'form': form,
                      })


class PasswordResetView(TemplateView):
    template_name = 'registration/password_reset_from_key.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'
    form_class = ResetPasswordForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class
        uid = request.POST.get('uid')
        token = request.POST.get('token')
        url = 'http://127.0.0.1:8000/password-reset-confirm/'+uid+"/"+token
        user_response = requests.post(
                            url,
                            data=json.dumps(request.POST),
                            headers={'Content-type': 'application/json'})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        response = ast.literal_eval(dict_str)
        response = dict(response)
        if 'status' in response:
            if response['status'] == 200:
                messages.success(
                                self.request,
                                'Password reset successfully.'
                                )
                return HttpResponseRedirect(reverse('hobo_user:user_login'))
        return render(request, 'registration/password_reset_from_key.html',
                      {'response': response,
                       'form': form,
                      })