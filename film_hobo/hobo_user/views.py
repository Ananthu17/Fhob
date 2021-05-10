import ast
import json
import requests
import datetime
from braces.views import JSONResponseMixin
from authemail.models import SignupCode

from django.template import loader
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.views import LoginView as DjangoLogin
from django.contrib.auth.views import LogoutView as DjangoLogout
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib import messages
from django.views.generic import TemplateView, View
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
    ForgotPasswordEmailForm, ResetPasswordForm, PersonalDetailsForm

from .models import CustomUser, IndiePaymentDetails, ProPaymentDetails, \
                    PromoCode, Country, DisabledAccount, CustomUserSettings, \
                    CompanyPaymentDetails, EthnicAppearanceInline, \
                    AthleticSkillInline, AthleticSkill

from .serializers import CustomUserSerializer, RegisterSerializer, \
    RegisterIndieSerializer, TokenSerializer, RegisterProSerializer, \
    SignupCodeSerializer, PaymentPlanSerializer, IndiePaymentSerializer, \
    ProPaymentSerializer, PromoCodeSerializer, \
    RegisterCompanySerializer, DisableAccountSerializer, \
    EnableAccountSerializer, BlockMembersSerializer, \
    CompanyPaymentSerializer, SettingsSerializer, \
    BlockedMembersQuerysetSerializer, PersonalDetailsSerializer, \
    PasswordResetSerializer

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
        context['user'] = user
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
        context['user'] = user
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
        context['user'] = user
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
            user_id = data_dict['user_id']
            promocode = data_dict['promo_code']
            try:
                promocode = PromoCode.objects.get(promo_code=promocode)
                life_span = promocode.life_span
                validity = promocode.valid_from + datetime.timedelta(
                        days=life_span)
                today = timezone.now()
                if today <= validity:
                    user = CustomUser.objects.get(id=user_id)
                    user_type = user.membership
                    if user_type == promocode.user_type:
                        response = {'message': 'Promo Code Applied', 'status':
                                    status.HTTP_200_OK}
                    else:
                        if user_type == 'IND':
                            membership = "Indie"
                        if user_type == 'PRO':
                            membership = "Pro"
                        if user_type == 'HOB':
                            membership = "Hobo"
                        if user_type == 'COM':
                            membership = "Production Company"
                        msg = 'This Promo Code is not available for '+membership+' users.'
                        response = {'message': msg, 'status':
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


class ChangePasswordAPI(AuthPasswordChangeView):
    permission_classes = (IsAuthenticated,)
    # serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        print("here")
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


class BlockMembersAPI(APIView):
    serializer_class = BlockMembersSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        blocked_members = dict()
        response = dict()
        user_settings = CustomUserSettings.objects.get(user=user)
        if user_settings.blocked_members:
            for obj in user_settings.blocked_members.all():
                blocked_members[obj.id]= obj.first_name + " "+ obj.last_name
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


class ForgotPasswordAPI(AuthPasswordResetView):
    serializer_class = PasswordResetSerializer
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
        form = self.form_class(request.POST)
        user_response = requests.post(
                            'http://127.0.0.1:8000/hobo_user/forgot-password-api/',
                            data=json.dumps(request.POST),
                            headers={'Content-type': 'application/json'})
        print(user_response)

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


class PasswordResetTemplateView(TemplateView):
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
        email = request.POST.get('email')
        url = 'http://127.0.0.1:8000/password-reset-confirm/'+uid+"/"+token
        user_response = requests.post(
                            url,
                            data=json.dumps(request.POST),
                            headers={'Content-type': 'application/json'})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        response = ast.literal_eval(dict_str)
        response = dict(response)
        print(response)
        if 'status' in response:
            if response['status'] == 200:
                # confirmation mail
                to_email =  []
                to_email.append(email)
                user = CustomUser.objects.get(email=email)
                subject = "Password Change on FilmHobo"
                message = 'text version of HTML message'
                html_message = loader.render_to_string(
                            'registration/change_password_confirmation_mail.html',
                            {
                                'name': user.first_name,
                            }
                        )
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                          to_email, fail_silently=True,
                          html_message=html_message)
                messages.success(
                                self.request,
                                'Password reset successfully.'
                                )
                return HttpResponseRedirect(reverse('hobo_user:user_login'))
        return render(request, 'registration/password_reset_from_key.html',
                      {'response': response,
                       'form': form,
                      })


class SettingsAPI(APIView):
    serializer_class = SettingsSerializer
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
            if 'who_can_track_me' in data_dict:
                user_settings.who_can_track_me = data_dict['who_can_track_me']
            if 'profile_visibility' in data_dict:
                user_settings.profile_visibility = data_dict[
                 'profile_visibility']
            if 'who_can_contact_me' in data_dict:
                user_settings.who_can_contact_me = data_dict[
                 'who_can_contact_me']
            if 'first_name' in data_dict:
                user.first_name = data_dict['first_name']
            if 'middle_name' in data_dict:
                user.middle_name = data_dict['middle_name']
            if 'last_name' in data_dict:
                user.last_name = data_dict['last_name']
            if 'email' in data_dict:
                email = data_dict['email']
                try:
                    id = user.id
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
                    user_settings.save()
                    response = {'message': "Settings Updated",
                                'status': status.HTTP_200_OK}
            else:
                user.save()
                user_settings.save()
                response = {'message': "Settings Updated",
                            'status': status.HTTP_200_OK}
        else:
            print(serializer.errors)
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

        already_blocked_users = user_settings.blocked_members.values_list(
                                'id', flat=True)
        already_blocked_users = list(already_blocked_users)
        already_blocked_users.append(self.request.user.id)

        # exclude super users
        super_users = CustomUser.objects.filter(is_staff=True).values_list('id', flat=True)
        for id in super_users:
            already_blocked_users.append(id)

        modified_queryset = CustomUser.objects.exclude(
                            id__in=already_blocked_users)

        disable_account_reasons = DisabledAccount.REASON_CHOICES
        context['user_settings'] = user_settings
        context['change_password_form'] = ChangePasswordForm
        context['disable_account_reasons'] = disable_account_reasons
        context['block_member_list'] = modified_queryset
        context['user'] = user
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        error_messages = dict()
        data_dict = self.request.POST
        user_settings = CustomUserSettings.objects.get(user=self.request.user)

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

        if 'profile_visibility' in data_dict:
            profile_visibility = data_dict['profile_visibility']
            if(profile_visibility == 'members_with_rating' and
               'visibility_rate' in data_dict):
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
                messages.warning(
                    self.request,
                    'Cannot save!! Please provide ratings for who can see my Profile'
                    )
                return HttpResponseRedirect(reverse('hobo_user:settings'))
        else:
            visibility = ""

        if 'who_can_contact_me' in data_dict:
            contact_members = data_dict['who_can_contact_me']
            if(contact_members == 'members_with_rating' and
               'contact_rate' in data_dict):
                contact_rate = data_dict['contact_rate']
                if contact_rate == '1':
                    contact_me = CustomUserSettings.MEMBERS_WITH_RATING_1_STAR
                if contact_rate == '2':
                    contact_me = CustomUserSettings.MEMBERS_WITH_RATING_2_STAR
                if contact_rate == '3':
                    contact_me = CustomUserSettings.MEMBERS_WITH_RATING_3_STAR
                if contact_rate == '4':
                    contact_me = CustomUserSettings.MEMBERS_WITH_RATING_4_STAR
                if contact_rate == '5':
                    contact_me = CustomUserSettings.MEMBERS_WITH_RATING_5_STAR
            elif contact_members != 'members_with_rating':
                contact_me = data_dict['who_can_contact_me']
            else:
                messages.warning(
                    self.request,
                    'Cannot save!! Please provide ratings for who can contact me'
                    )
                return HttpResponseRedirect(reverse('hobo_user:settings'))
        else:
            contact_me = ""

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
                messages.warning(
                    self.request,
                    'Cannot save!! Please provide ratings for who can track me'
                    )
                return HttpResponseRedirect(reverse('hobo_user:settings'))
        else:
            tracking = ""

        json_response = json.dumps(request.POST)
        json_dict = ast.literal_eval(json_response)
        json_dict['who_can_contact_me'] = contact_me
        json_dict['profile_visibility'] = visibility
        json_dict['who_can_track_me'] = tracking
        json_dict['someone_tracks_me'] = someone_tracks_me
        json_dict[
            'change_in_my_or_project_rating'] = change_in_my_or_project_rating
        json_dict[
            'review_for_my_work_or_project'] = review_for_my_work_or_project
        json_dict['new_project'] = new_project
        json_dict['friend_request'] = friend_request
        json_dict['match_for_my_Interest'] = match_for_my_Interest
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        user_response = requests.post(
                            'http://127.0.0.1:8000/hobo_user/update-settings-api/',
                            data=json.dumps(json_dict),
                            headers={'Content-type': 'application/json',
                                     'Authorization': token})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        response = ast.literal_eval(dict_str)
        response = dict(response)

        if response['status'] == 200:
            messages.success(self.request, 'General Settings Updated')
            return HttpResponseRedirect(reverse('hobo_user:settings'))
        else:
            print(response['errors'])
            error_messages = response['errors']
            if 'first_name' in error_messages:
                messages.warning(self.request, "First name cannot be empty")
            if 'last_name' in error_messages:
                messages.warning(self.request, "Last name cannot be empty")
            if 'email' in error_messages:
                messages.warning(self.request, "Enter valid email address, This field cannot be empty")
            if 'email_validation_error' in response:
                messages.warning(self.request, "Enter valid email id")
        return HttpResponseRedirect(reverse('hobo_user:settings'))


class GetUnblockedMembersAPI(APIView):
    serializer_class = BlockedMembersQuerysetSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        response = {}
        queryset = {}
        user_settings = CustomUserSettings.objects.get(user=user)
        already_blocked_users = user_settings.blocked_members.values_list(
                                'id', flat=True)
        already_blocked_users = list(already_blocked_users)
        already_blocked_users.append(self.request.user.id)

        # exclude super users
        super_users = CustomUser.objects.filter(is_staff=True).values_list('id', flat=True)
        for id in super_users:
            already_blocked_users.append(id)

        modified_queryset = CustomUser.objects.exclude(
                            id__in=already_blocked_users)
        if modified_queryset:
            for obj in modified_queryset:
                queryset[obj.id] = obj.first_name + " "+ obj.last_name
            response['queryset'] = queryset
        return Response(response)


class GetUnblockedMembersAjaxView(View, JSONResponseMixin):
    template_name = 'user_pages/blocking_dropdown_menu.html'

    def get(self, *args, **kwargs):
        context = dict()
        user = self.request.user
        user_settings = CustomUserSettings.objects.get(user=user)

        already_blocked_users = user_settings.blocked_members.values_list(
                                'id', flat=True)
        already_blocked_users = list(already_blocked_users)
        already_blocked_users.append(self.request.user.id)

        # exclude super users
        super_users = CustomUser.objects.filter(is_staff=True).values_list('id', flat=True)
        for id in super_users:
            already_blocked_users.append(id)
        print(already_blocked_users)

        modified_queryset = CustomUser.objects.exclude(
                            id__in=already_blocked_users)
        blocked_users_html = render_to_string(
                                'user_pages/blocking_dropdown_menu.html',
                                {'block_member_list': modified_queryset})
        context['blocked_users_html'] = blocked_users_html
        return self.render_json_response(context)


class PersonalDetailsAPI(APIView):
    serializer_class = PersonalDetailsSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        personal_settings = {}
        personal_settings['gender'] = user.gender
        personal_settings['feet'] = user.feet
        personal_settings['inch'] = user.inch
        personal_settings['lbs'] = user.lbs
        personal_settings['start_age'] = user.start_age
        personal_settings['stop_age'] = user.stop_age
        personal_settings['physique'] = user.physique
        personal_settings['hair_color'] = user.hair_color
        personal_settings['hair_length'] = user.hair_length
        personal_settings['eyes'] = user.eyes
        # ethnic_appearance_list = EthnicAppearanceInline.objects.filter(
        #                          creator=user)
        athletic_skill_list = AthleticSkillInline.objects.filter(
                              creator=user).values_list('athletic_skill', flat=True)
        print(athletic_skill_list)
        # personal_settings['ethnic_appearance'] = 
        personal_settings['athletic_skills'] = athletic_skill_list
        response = {"personal_settings" : personal_settings}
        return Response(response)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        user = request.user
        if serializer.is_valid():
            data_dict = serializer.data
            if 'gender' in data_dict:
                user.gender = data_dict['gender']
            if 'feet' in data_dict:
                user.feet = data_dict['feet']
            if 'inch' in data_dict:
                user.inch = data_dict['inch']
            if 'lbs' in data_dict:
                user.lbs = data_dict['lbs']
            if 'start_age' in data_dict:
                user.start_age = data_dict['start_age']
            if 'stop_age' in data_dict:
                user.stop_age = data_dict['stop_age']
            if 'physique' in data_dict:
                user.physique = data_dict['physique']
            if 'hair_color' in data_dict:
                user.hair_color = data_dict['hair_color']
            if 'hair_length' in data_dict:
                user.hair_length = data_dict['hair_length']
            if 'eyes' in data_dict:
                user.eyes = data_dict['eyes']
            user.save()
            if 'athletic_skills' in data_dict:
                old_skills = AthleticSkillInline.objects.filter(creator=user)
                if old_skills:
                    for obj in old_skills:
                        obj.delete()
                for item in data_dict['athletic_skills']:
                    skill = AthleticSkill.objects.get(id=item)
                    athletic_skills_inline = AthleticSkillInline()
                    athletic_skills_inline.athletic_skill = skill
                    athletic_skills_inline.creator = user
                    athletic_skills_inline.save()
            response = {'message': "Personal Details Updated",
                        'status': status.HTTP_200_OK}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}

        return Response(response)


class PersonalDetailsView(LoginRequiredMixin, TemplateView):
    template_name = 'user_pages/personal-details.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'
    form_class = PersonalDetailsForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        all_athletic_skills = AthleticSkill.objects.all()
        athletic_skills = AthleticSkillInline.objects.filter(
                          creator=user).values_list('athletic_skill__id', flat=True)
        context['form'] = self.form_class(instance=user)
        context['user'] = user
        context['all_athletic_skills'] = all_athletic_skills
        context['athletic_skills'] = athletic_skills
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        print(request.POST)
        # json_response = json.dumps(request.POST)
        # json_dict = ast.literal_eval(json_response)
        # key = Token.objects.get(user=user).key
        # token = 'Token '+key
        # user_response = requests.post(
        #                     'http://127.0.0.1:8000/hobo_user/personal-details-api/',
        #                     data=json.dumps(request.POST),
        #                     headers={'Content-type': 'application/json',
        #                              'Authorization': token})
        # byte_str = user_response.content
        # dict_str = byte_str.decode("UTF-8")
        # response = ast.literal_eval(dict_str)
        # response = dict(response)
        # if 'status' in response:
        #     if response['status'] == 200:
        #         messages.success(self.request, 'Personal details updated')
        #         return HttpResponseRedirect(
        #             reverse('hobo_user:personal-details'))
        #     else:
        #         message = response['message']
        # return render(
        #     request, 'user_pages/personal-details.html',
        #     {'message': message})
        return HttpResponseRedirect(reverse('hobo_user:personal-details'))