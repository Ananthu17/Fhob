import ast
import json
from os import remove
from django.contrib.auth.models import User
from django.db.models.deletion import SET_NULL
import requests
import datetime
from braces.views import JSONResponseMixin
from authemail.models import SignupCode

from django.core.files import File
from django.db.models import Q
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
from rest_framework import serializers

from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from rest_auth.registration.views import RegisterView
from rest_framework.authtoken.models import Token
from rest_auth.views import LoginView as AuthLoginView
from rest_auth.views import LogoutView as AuthLogoutView
from rest_auth.views import PasswordChangeView as AuthPasswordChangeView
from rest_auth.views import PasswordResetView as AuthPasswordResetView
from rest_auth.views import PasswordResetConfirmView as AuthPasswordResetConfirmView
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser

from authemail.views import SignupVerify

from .forms import SignUpForm, LoginForm, SignUpIndieForm, \
    SignUpFormCompany, SignUpProForm, ChangePasswordForm, \
    ForgotPasswordEmailForm, ResetPasswordForm, PersonalDetailsForm, \
    EditProfileForm

from .models import CoWorker, CustomUser, GuildMembership, \
                    IndiePaymentDetails, Photo, ProPaymentDetails, \
                    PromoCode, Country, DisabledAccount, CustomUserSettings, \
                    CompanyPaymentDetails, AthleticSkill, AthleticSkillInline, \
                    EthnicAppearance, UserAgentManager, UserProfile, CoWorker, JobType, \
                    UserRating, UserRatingCombined, UserTacking, Photo

from .serializers import CustomUserSerializer, RegisterSerializer, \
    RegisterIndieSerializer, TokenSerializer, RegisterProSerializer, \
    SignupCodeSerializer, PaymentPlanSerializer, IndiePaymentSerializer, \
    ProPaymentSerializer, PromoCodeSerializer, \
    RegisterCompanySerializer, DisableAccountSerializer, \
    EnableAccountSerializer, BlockMembersSerializer, \
    CompanyPaymentSerializer, SettingsSerializer, \
    BlockedMembersQuerysetSerializer, PersonalDetailsSerializer, \
    PasswordResetSerializer, UserProfileSerializer, CoWorkerSerializer, \
    RemoveCoWorkerSerializer, RateUserSkillsSerializer, AgentManagerSerializer, \
    RemoveAgentManagerSerializer, TrackUserSerializer, UserSerializer, \
    GetSettingsSerializer, PhotoSerializer, UploadPhotoSerializer

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
        profile = UserProfile()
        profile.user = user
        profile.save()

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
        profile = UserProfile()
        profile.user = user
        profile.save()

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
        profile = UserProfile()
        profile.user = user
        profile.save()

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
        profile = UserProfile()
        profile.user = user
        profile.save()

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


class HowTo(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'user_pages/how_to.html')


class HomePage(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'user_pages/user_home.html')


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
        context['client-id'] = settings.PAYPAL_CLIENT_ID
        free_evaluation_time = payment_details['free_days']
        date_today = datetime.date.today()
        date_interval = datetime.timedelta(days=int(free_evaluation_time))
        bill_date = date_today + date_interval
        context['bill_date'] = bill_date
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
        # print(user_response)

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
        personal_settings['eyes'] = user.eyes
        personal_settings['ethnic_appearance'] = user.ethnic_appearance.ethnic_appearance

        athletic_skill_list = AthleticSkillInline.objects.filter(
                              creator=user).values_list('athletic_skill', flat=True)
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
            if 'ethnic_appearance' in data_dict:
                ethnic_appearance_id = data_dict['ethnic_appearance']
                obj = EthnicAppearance.objects.get(id=ethnic_appearance_id)
                user.ethnic_appearance = obj
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
        all_ethnic_appearances = EthnicAppearance.objects.all()
        athletic_skills = AthleticSkillInline.objects.filter(
                          creator=user).values_list('athletic_skill__id', flat=True)
        context['form'] = self.form_class(instance=user)
        context['user'] = user
        context['all_ethnic_appearances'] = all_ethnic_appearances
        context['all_athletic_skills_set1'] = all_athletic_skills[:15]
        context['all_athletic_skills_set2'] = all_athletic_skills[15:]
        context['athletic_skills'] = athletic_skills
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user

        athletic_skills = request.POST.getlist('checks[]')
        json_response = json.dumps(request.POST)
        json_dict = ast.literal_eval(json_response)
        json_dict['athletic_skills'] = athletic_skills
        lbs = request.POST.get('lbs')
        start_age = request.POST.get('start_age')
        stop_age = request.POST.get('stop_age')
        lbs = request.POST.get('lbs')
        if lbs == '':
            json_dict['lbs'] = None
        if start_age == '':
            json_dict['start_age'] = None
        if stop_age == '':
            json_dict['stop_age'] = None
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        user_response = requests.post(
                            'http://127.0.0.1:8000/hobo_user/personal-details-api/',
                            data=json.dumps(json_dict),
                            headers={'Content-type': 'application/json',
                                     'Authorization': token})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        response = ast.literal_eval(dict_str)
        response = dict(response)
        message = ""
        if 'status' in response:
            if response['status'] == 200:
                messages.success(self.request, 'Personal details updated')
                return HttpResponseRedirect(
                    reverse('hobo_user:edit-profile'))
            else:
                if 'errors' in response:
                    errors = response['errors']
                    all_athletic_skills = AthleticSkill.objects.all()
                    all_ethnic_appearances = EthnicAppearance.objects.all()
                    athletic_skills = AthleticSkillInline.objects.filter(
                          creator=user).values_list('athletic_skill__id', flat=True)
                    messages.warning(self.request, "Failed to update personal details.")
                    return render(request, 'user_pages/personal-details.html',
                                  {'errors': errors,
                                   'form': PersonalDetailsForm,
                                   'all_ethnic_appearances': all_ethnic_appearances,
                                   'all_athletic_skills_set1': all_athletic_skills[:15],
                                   'all_athletic_skills_set2': all_athletic_skills[15:],
                                   'athletic_skills': athletic_skills,
                                   'user': user
                                  })
        return HttpResponseRedirect(reverse('hobo_user:edi-profile'))


class UserProfileAPI(APIView):
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        profile = UserProfile.objects.get(user=user)
        profile_data = {}
        job_type_list = {}
        guild_membership_dict = {}
        job_types = profile.job_types.all()
        guild_membership = user.guild_membership.all()

        profile_data['first_name'] = user.first_name
        profile_data['middle_name'] = user.middle_name
        profile_data['last_name'] = user.last_name
        profile_data['membership'] = user.membership
        for item in job_types:
            job_type_list[item.id] = item.title
        for item in guild_membership:
            guild_membership_dict[item.id] = item.membership
        profile_data['guild_membership'] = guild_membership_dict
        profile_data['job_types'] = job_type_list
        profile_data['company'] = profile.company
        profile_data['company_position'] = profile.company_position
        profile_data['company_website'] = profile.company_website
        profile_data['imdb'] = profile.imdb
        profile_data['bio'] = profile.bio
        if user.membership == CustomUser.PRODUCTION_COMPANY:
            coworkers = CoWorker.objects.filter(company=user)
            coworkers_dict = {}
            for obj in coworkers:
                coworkers_dict[obj.id] = obj.position.title
        profile_data['coworkers'] = coworkers_dict
        response = {"profile_data": profile_data}
        return Response(response)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        user = request.user
        profile = UserProfile.objects.get(user=user)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            if 'first_name' in data_dict:
                user.first_name = data_dict['first_name']
            if 'middle_name' in data_dict:
                user.middle_name = data_dict['middle_name']
            if 'last_name' in data_dict:
                user.last_name = data_dict['last_name']
            if 'guild_membership' in data_dict:
                user.guild_membership.set(data_dict['guild_membership'])
            user.save()
            if 'company' in data_dict:
                profile.company = data_dict['company']
            if 'company_position' in data_dict:
                profile.company_position = data_dict['company_position']
            if 'company_website' in data_dict:
                profile.company_website = data_dict['company_website']
            if 'imdb' in data_dict:
                profile.imdb = data_dict['imdb']
            if 'bio' in data_dict:
                profile.bio = data_dict['bio']
            profile.save()
            response = {'message': "Profile Updated",
                        'status': status.HTTP_200_OK}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}

        return Response(response)


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'user_pages/edit-profile.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'
    form_class = EditProfileForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile = UserProfile.objects.get(user=user)
        all_agents = UserAgentManager.objects.filter(user=self.request.user)
        context['all_agents'] = all_agents
        context['guild_membership'] = GuildMembership.objects.all()
        context['user'] = user
        context['profile'] = profile
        pos_list = [2, 3, 4]
        all_photos = Photo.objects.filter(user=user)
        photos = all_photos.filter(position__in=pos_list)
        context['photos'] = photos[:3]
        context['all_photos'] = all_photos[:4]
        context['form'] = self.form_class(instance=profile)

        # exclude super user and current user
        user_ids = []
        super_users = CustomUser.objects.filter(is_staff=True).values_list('id', flat=True)
        for id in super_users:
            user_ids.append(id)
        user_ids.append(user.id)
        all_users = CustomUser.objects.exclude(id__in=user_ids)

        context['all_users'] = all_users
        context['job_types'] = JobType.objects.all()

        coworkers = CoWorker.objects.filter(company=user)
        context['coworkers'] = coworkers

        track_obj = UserTacking.objects.get(user=user)
        trackers_list = track_obj.tracked_by.all()
        tracking_list = UserTacking.objects.filter(
                        tracked_by=user)
        context['trackers_list'] = trackers_list
        context['tracking_list'] = tracking_list
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        profile = UserProfile.objects.get(user=user)
        guild_membership_all = GuildMembership.objects.all()
        all_agents = UserAgentManager.objects.filter(user=self.request.user)
        guild_membership = request.POST.getlist('guild_membership')
        remove_agents = request.POST.getlist('remove-agent')
        json_response = json.dumps(request.POST)
        json_dict = ast.literal_eval(json_response)
        json_dict['guild_membership'] = guild_membership

        agent_dict = {}
        remove_dict = {}
        agent_name_list = request.POST.get('agent_name')
        agent_phone_list = request.POST.get('agent_phone')
        agent_email_list = request.POST.get('agent_email')
        agent_manager_list = list(request.POST.getlist('agent_type'))
        agent_job_list = request.POST.get('agent_job_type')
        agent_manager_count = len(agent_manager_list)

        # edit agent/manager
        edit_agent_dict = {}
        edit_agent_id_list = request.POST.getlist('edit_agent_id')
        edit_agent_name_list = request.POST.getlist('edit_agent_name')
        edit_agent_phone_list = request.POST.getlist('edit_agent_phone')
        edit_agent_email_list = request.POST.getlist('edit_agent_email')
        edit_agent_manager_list = request.POST.getlist('edit_agent_type')
        edit_agent_job_list = request.POST.getlist('edit_agent_job_type')
        edit_count = len(edit_agent_manager_list)

        for i in range(edit_count):
            edit_agent_dict['id'] = edit_agent_id_list[i]
            edit_agent_dict['agent_name'] = edit_agent_name_list[i]
            edit_agent_dict['agent_type'] = edit_agent_manager_list[i]
            edit_agent_dict['agent_job_type'] = edit_agent_job_list[i]
            edit_agent_dict['agent_phone'] = edit_agent_phone_list[i]
            if edit_agent_email_list[i] != "":
                edit_agent_dict['agent_email'] = edit_agent_email_list[i]
            else:
                edit_agent_dict['agent_email'] = ""
            # call edit-agent api
            user_response = requests.post(
                    'http://127.0.0.1:8000/hobo_user/edit-agent-manager-api/',
                    data=json.dumps(edit_agent_dict),
                    headers={'Content-type': 'application/json',
                            'Authorization': token})
            byte_str = user_response.content
            dict_str = byte_str.decode("UTF-8")
            response = ast.literal_eval(dict_str)
            response = dict(response)
            if 'status' in response:
                if response['status'] != 200:
                    if 'errors' in response:
                        errors = response['errors']
                        if 'agent_phone' in errors and 'agent_email' in errors:
                            messages.warning(self.request,
                            "Failed to update Agent/Manager.Enter valid phone number and email address.")
                        elif 'agent_phone' in errors:
                            messages.warning(self.request,
                            "Failed to update Agent/Manager. Enter valid phone number.")
                        elif 'agent_email' in errors:
                            messages.warning(self.request,
                            "Failed to update Agent/Manager. Enter valid email address.")
                        return HttpResponseRedirect(
                                reverse('hobo_user:edit-profile'))

        if agent_name_list == "":
            agent_count = 0
        else:
            agent_name_list = list(request.POST.getlist('agent_name'))
            agent_count = len(agent_name_list)

        if agent_job_list == "":
            agent_job_count = 0
        else:
            agent_job_list = list(request.POST.getlist('agent_job_type'))
            agent_job_count = len(agent_job_list)

        if agent_phone_list == "":
            agent_phone_count = 0
        else:
            agent_phone_list = list(request.POST.getlist('agent_phone'))
            agent_phone_count = len(agent_phone_list)

        if agent_email_list == "":
            agent_email_count = 0
        else:
            agent_email_list = list(request.POST.getlist('agent_email'))
            agent_email_count = len(agent_email_list)

        if((agent_count != 0) and
           (agent_count != agent_manager_count) or
           (agent_count != agent_phone_count) or
           (agent_count != agent_job_count)
           ):
            messages.warning(
                self.request,
                "Failed to update Agent/Manager. Provide agent name, job & phone number.")
            return HttpResponseRedirect(reverse('hobo_user:edit-profile'))

        if((agent_count == agent_manager_count) and
           (agent_count == agent_phone_count) and
           (agent_count == agent_job_count) and
           (agent_count != 0)
           ):
            for i in range(agent_count):
                agent_dict['agent_name'] = agent_name_list[i]
                agent_dict['agent_type'] = agent_manager_list[i]
                agent_dict['agent_job_type'] = agent_job_list[i]
                agent_dict['agent_phone'] = agent_phone_list[i]
                if agent_email_count != 0:
                    if agent_email_list[i] != "":
                        agent_dict['agent_email'] = agent_email_list[i]
                    else:
                        agent_dict['agent_email'] = ""

                # save agents/manager
                user_response = requests.post(
                                    'http://127.0.0.1:8000/hobo_user/add-agent-manager-api/',
                                    data=json.dumps(agent_dict),
                                    headers={'Content-type': 'application/json',
                                            'Authorization': token})
                byte_str = user_response.content
                dict_str = byte_str.decode("UTF-8")
                response = ast.literal_eval(dict_str)
                response = dict(response)
                if 'status' in response:
                    if response['status'] != 200:
                        if 'errors' in response:
                            errors = response['errors']
                            if 'agent_phone' in errors and 'agent_email' in errors:
                                messages.warning(self.request,
                                "Failed to update Agent/Manager.Enter valid phone number and email address.")
                            elif 'agent_phone' in errors:
                                messages.warning(self.request,
                                "Failed to update Agent/Manager. Enter valid phone number.")
                            elif 'agent_email' in errors:
                                messages.warning(self.request,
                                "Failed to update Agent/Manager. Enter valid email address.")
                            return HttpResponseRedirect(
                                    reverse('hobo_user:edit-profile'))
        if remove_agents:
            remove_dict['id'] = remove_agents
            user_response = requests.post(
                                'http://127.0.0.1:8000/hobo_user/remove-agent-api/',
                                data=json.dumps(remove_dict),
                                headers={
                                    'Content-type': 'application/json',
                                    'Authorization': token})
            byte_str = user_response.content
            dict_str = byte_str.decode("UTF-8")
            response = ast.literal_eval(dict_str)
            response = dict(response)
            if 'status' in response:
                if response['status'] != 200:
                    if 'errors' in response:
                        # errors = response['errors']
                        messages.warning(
                            self.request, "Failed to remove Stuff !!")
                        return HttpResponseRedirect(
                            reverse('hobo_user:edit-profile'))

        # Update Profile
        user_response = requests.post(
                            'http://127.0.0.1:8000/hobo_user/profile-api/',
                            data=json.dumps(json_dict),
                            headers={'Content-type': 'application/json',
                                     'Authorization': token})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        response = ast.literal_eval(dict_str)
        response = dict(response)
        if 'status' in response:
            if response['status'] == 200:
                messages.success(self.request, 'Profile updated successfully')
                return HttpResponseRedirect("/hobo_user/profile/%s/" % (user.id))
            else:
                if 'errors' in response:
                    errors = response['errors']
                    messages.warning(self.request, "Failed to update profile !!")
                    return render(request, 'user_pages/edit-profile.html',
                                  {'errors': errors,
                                   'form': self.form_class(instance=profile),
                                   'profile': profile,
                                   'user': user,
                                   'guild_membership': guild_membership_all,
                                   'all_agents': all_agents
                                   })
        return HttpResponseRedirect("/hobo_user/profile/%s/" % (user.id))


class AddCoworkerAPI(APIView):
    serializer_class = CoWorkerSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        company = request.user
        if serializer.is_valid():
            data_dict = serializer.data
            if 'user' not in data_dict and 'name' not in data_dict:
                response = {'errors': "Either User id or Name is required", 'status':
                            status.HTTP_400_BAD_REQUEST}
            else:
                coworker = CoWorker()
                coworker.company = company
                if 'position' in data_dict:
                    position = JobType.objects.get(id=data_dict['position'])
                    coworker.position = position
                if 'user' in data_dict:
                    user = CustomUser.objects.get(id=data_dict['user'])
                    coworker.user = user
                    coworker.name = user.get_full_name()
                    profile = UserProfile.objects.get(user=user)
                    profile.update_job_type(position.id)
                    profile.save()
                if 'name' in data_dict:
                    coworker.name = data_dict['name']
                coworker.save()
                response = {'message': "Stuff Added",
                            'status': status.HTTP_200_OK}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class EditCoworkerAPI(APIView):
    serializer_class = CoWorkerSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            id = data_dict['id']
            try:
                coworker = CoWorker.objects.get(id=id)
                if coworker.company == request.user:
                    if 'position' in data_dict:
                        position = JobType.objects.get(id=data_dict['position'])
                        coworker.position = position
                    if 'user' in data_dict and data_dict['user']!="":
                        user_id = data_dict['user']
                        user = CustomUser.objects.get(id=user_id)
                        coworker.user = user
                        coworker.name = user.get_full_name()
                        profile = UserProfile.objects.get(user=user)
                        profile.update_job_type(position.id)
                        profile.save()
                    if 'name' in data_dict and data_dict['name'] != "":
                        coworker.name = data_dict['name']
                    coworker.save()
                    response = {'message': "Stuffs Updated",
                                'status': status.HTTP_200_OK}
                else:
                    response = {'errors': "Invalid Token", 'status':
                                status.HTTP_400_BAD_REQUEST}
            except CoWorker.DoesNotExist:
                response = {'errors': "Object Not found", 'status':
                            status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class AddAgentManagerAPI(APIView):
    serializer_class = AgentManagerSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            obj = UserAgentManager()
            obj.user = self.request.user
            if 'agent_type' in data_dict:
                obj.agent_type = data_dict['agent_type']
            if 'agent_name' in data_dict:
                obj.agent_name = data_dict['agent_name']
            if 'agent_phone' in data_dict:
                obj.agent_phone = data_dict['agent_phone']
            if 'agent_email' in data_dict:
                obj.agent_email = data_dict['agent_email']
            if 'agent_job_type' in data_dict:
                obj.agent_job_type = data_dict['agent_job_type']

            obj.save()
            response = {'message': "Agent-Manager Added",
                        'status': status.HTTP_200_OK}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class EditAgentManagerAPI(APIView):
    serializer_class = AgentManagerSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            id = data_dict['id']
            try:
                obj = UserAgentManager.objects.get(id=id)
                if request.user == obj.user:
                    if 'agent_type' in data_dict:
                        obj.agent_type = data_dict['agent_type']
                    if 'agent_name' in data_dict:
                        obj.agent_name = data_dict['agent_name']
                    if 'agent_phone' in data_dict:
                        obj.agent_phone = data_dict['agent_phone']
                    if 'agent_email' in data_dict:
                        obj.agent_email = data_dict['agent_email']
                    if 'agent_job_type' in data_dict:
                        obj.agent_job_type = data_dict['agent_job_type']

                    obj.save()
                    response = {'message': "Agent-Manager Updated",
                                'status': status.HTTP_200_OK}
                else:
                    response = {'errors': "Invalid Token",
                                'status': status.HTTP_400_BAD_REQUEST}
            except UserAgentManager.DoesNotExist:
                response = {'errors': "Object not found", 'status':
                            status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class GetAgentManagerAPI(APIView):
    serializer_class = AgentManagerSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        agent_dict = {}
        agents = UserAgentManager.objects.filter(user=self.request.user)
        for agent in agents:
            agent_dict[agent.id ]= self.serializer_class(agent).data
        response = {'Agents and managers': agent_dict}
        return Response(response)


class GetSettingsAPI(APIView):
    serializer_class = GetSettingsSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        settings_dict = {}
        response = {}
        try:
            user_settings = CustomUserSettings.objects.get(user=user)
            settings_dict = self.serializer_class(user_settings).data
            response = {'User Settings': settings_dict}
        except CustomUserSettings.DoesNotExist:
            response = {'message': "Custom User Settings not found",
                        'status': status.HTTP_400_BAD_REQUEST}
        return Response(response)


class RemoveCoworkerAPI(APIView):
    serializer_class = RemoveCoWorkerSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            remove_ids = data_dict['id']
            for id in remove_ids:
                try:
                    obj = CoWorker.objects.get(id=id)

                    # Remove job type from this profile if this user doesnot
                    # participate in any other projects in this job type

                    # if obj.user:
                    #     profile = UserProfile.objects.get(user=obj.user)
                    #     profile.remove_job_type(obj.position.id)
                    #     profile.save()

                    obj.delete()
                    response = {'message': "Stuff Removed",
                                'status': status.HTTP_200_OK}
                except CoWorker.DoesNotExist:
                    response = {'message': "Invalid Id",
                                'status': status.HTTP_400_BAD_REQUEST}
                    return Response(response)
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class RemoveAgentManagerAPI(APIView):
    serializer_class = RemoveAgentManagerSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            remove_ids = data_dict['id']
            for id in remove_ids:
                try:
                    obj = UserAgentManager.objects.get(id=id)
                    obj.delete()
                    response = {'message': "Agent-Manager Removed",
                                'status': status.HTTP_200_OK}
                except UserAgentManager.DoesNotExist:
                    response = {'message': "Invalid Id",
                                'status': status.HTTP_400_BAD_REQUEST}
                    return Response(response)

        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class AddCoworkersView(LoginRequiredMixin, TemplateView):

    def post(self, request, *args, **kwargs):
        user = self.request.user
        json_dict = {}
        edit_dict = {}
        remove_ids = request.POST.getlist('remove')

        users = list(request.POST.getlist('user'))
        position = list(request.POST.getlist('position'))
        designation = list(request.POST.getlist('designation'))

        saved_id = list(request.POST.getlist('saved_id'))
        saved_user = list(request.POST.getlist('saved_user'))
        saved_name = list(request.POST.getlist('saved_name'))
        saved_position = list(request.POST.getlist('saved_position'))

        edit_count = len(saved_position)
        user_count = len(users)
        position_count = len(position)
        designation_count = len(designation)

        new_users = request.POST.get('name')
        if new_users == "":
            new_users_count = 0
        else:
            new_users = list(request.POST.getlist('name'))
            new_users_count = len(new_users)
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        if(
           (user_count != position_count) or
           (new_users_count != designation_count)
           ):
            messages.warning(
                self.request,
                "Failed to update Stuff. Provide name & position")
            return HttpResponseRedirect(reverse('hobo_user:edit-profile'))

        if((user_count == position_count) and (user_count != 0)):
            for i in range(user_count):
                json_dict['user'] = users[i]
                json_dict['position'] = position[i]
                user_response = requests.post(
                                    'http://127.0.0.1:8000/hobo_user/add-coworker-api/',
                                    data=json.dumps(json_dict),
                                    headers={'Content-type': 'application/json',
                                            'Authorization': token})
                byte_str = user_response.content
                dict_str = byte_str.decode("UTF-8")
                response = ast.literal_eval(dict_str)
                response = dict(response)
                if 'status' in response:
                    if response['status'] != 200:
                        if 'errors' in response:
                            # errors = response['errors']
                            messages.warning(
                                self.request, "Failed to update Stuff !!")
                            return HttpResponseRedirect(
                                reverse('hobo_user:edit-profile'))
        json_dict = {}
        if((new_users_count == designation_count) and (new_users_count != 0)):
            for i in range(new_users_count):
                json_dict['name'] = new_users[i]
                json_dict['position'] = designation[i]
                user_response = requests.post(
                                    'http://127.0.0.1:8000/hobo_user/add-coworker-api/',
                                    data=json.dumps(json_dict),
                                    headers={
                                        'Content-type': 'application/json',
                                        'Authorization': token})
                byte_str = user_response.content
                dict_str = byte_str.decode("UTF-8")
                response = ast.literal_eval(dict_str)
                response = dict(response)
                if 'status' in response:
                    if response['status'] != 200:
                        if 'errors' in response:
                            # errors = response['errors']
                            messages.warning(
                                self.request, "Failed to update Stuff !!")
                            return HttpResponseRedirect(
                                reverse('hobo_user:edit-profile'))

        for i in range(edit_count):
            edit_dict['id'] = saved_id[i]
            edit_dict['name'] = saved_name[i]
            edit_dict['position'] = saved_position[i]
            edit_dict['user'] = saved_user[i]
            user_response = requests.post(
                                'http://127.0.0.1:8000/hobo_user/edit-coworker-api/',
                                data=json.dumps(edit_dict),
                                headers={
                                    'Content-type': 'application/json',
                                    'Authorization': token})
            byte_str = user_response.content
            dict_str = byte_str.decode("UTF-8")
            response = ast.literal_eval(dict_str)
            response = dict(response)
            if 'status' in response:
                if response['status'] != 200:
                    if 'errors' in response:
                        messages.warning(
                            self.request, "Failed to update Stuff !!")
                        return HttpResponseRedirect(
                            reverse('hobo_user:edit-profile'))
        json_dict = {}
        if remove_ids:
            json_dict['id'] = remove_ids
            user_response = requests.post(
                                'http://127.0.0.1:8000/hobo_user/remove-coworker-api/',
                                data=json.dumps(json_dict),
                                headers={
                                    'Content-type': 'application/json',
                                    'Authorization': token})
            byte_str = user_response.content
            dict_str = byte_str.decode("UTF-8")
            response = ast.literal_eval(dict_str)
            response = dict(response)
            if 'status' in response:
                if response['status'] != 200:
                    if 'errors' in response:
                        # errors = response['errors']
                        messages.warning(
                            self.request, "Failed to remove Stuff !!")
                        return HttpResponseRedirect(
                            reverse('hobo_user:edit-profile'))
        messages.success(self.request, 'Stuffs updated successfully')
        return HttpResponseRedirect("/hobo_user/profile/%s/" % (user.id))


class AddCoworkerFormAjaxView(View, JSONResponseMixin):
    template_name = 'user_pages/add-coworker-form1.html'

    def get(self, *args, **kwargs):
        context = dict()
        user = self.request.user
        count = self.request.GET.get('count')
        all_users_dict = {}
        job_types_dict = {}

        # exclude super user and current user
        user_ids = []
        super_users = CustomUser.objects.filter(is_staff=True).values_list('id', flat=True)
        for id in super_users:
            user_ids.append(id)
        user_ids.append(user.id)
        all_users = CustomUser.objects.exclude(id__in=user_ids)

        job_types = JobType.objects.all()
        for usr in all_users:
            all_users_dict[usr.id] = usr.first_name+" "+usr.last_name
        for job in job_types:
            job_types_dict[job.id] = job.title
        add_coworker_form_html = render_to_string(
                                'user_pages/add-coworker-form1.html', {
                                    'all_users': all_users_dict,
                                    'job_types': job_types_dict,
                                    'count': count
                                    })
        context['add_coworker_form_html'] = add_coworker_form_html
        return self.render_json_response(context)


class AddNewCoworkerFormAjaxView(View, JSONResponseMixin):
    template_name = 'user_pages/add-coworker-form2.html'

    def get(self, *args, **kwargs):
        context = dict()
        count = self.request.GET.get('new_count')
        job_types_dict = {}
        job_types = JobType.objects.all()
        for job in job_types:
            job_types_dict[job.id] = job.title
        add_new_coworker_form_html = render_to_string(
                                'user_pages/add-coworker-form2.html', {
                                    'job_types': job_types_dict,
                                    'count': count
                                    })
        context['add_new_coworker_form_html'] = add_new_coworker_form_html
        return self.render_json_response(context)


class AddNewAgentFormAjaxView(View, JSONResponseMixin):
    template_name = 'user_pages/add-agent-form.html'

    def get(self, *args, **kwargs):
        context = dict()
        count = self.request.GET.get('agent_count')
        job_types_dict = {}
        job_types = JobType.objects.all()
        for job in job_types:
            job_types_dict[job.id] = job.title
        add_new_agent_form_html = render_to_string(
                                'user_pages/add-agent-form.html', {
                                    'job_types': job_types_dict,
                                    'count': count
                                    })
        context['add_new_agent_form_html'] = add_new_agent_form_html
        return self.render_json_response(context)


class MemberProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'user_pages/memberprofile.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(CustomUser, id=self.kwargs.get('id'))
        try:
            profile = UserProfile.objects.get(user=user)
            all_agents = UserAgentManager.objects.filter(user=user)
            context['all_agents'] = all_agents
            context['profile'] = profile
        except UserProfile.DoesNotExist:
            message = "No Data Available"
            context['message'] = message
        return context


class RateUserSkillsAPI(APIView):
    serializer_class = RateUserSkillsSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            user = CustomUser.objects.get(id=data_dict['user'])
            job_type = JobType.objects.get(id=data_dict['job_type'])
            try:
                user_rating = UserRating.objects.get(
                               Q(user=data_dict['user']) &
                               Q(rated_by=request.user) &
                               Q(job_type=data_dict['job_type'])
                               )
            except UserRating.DoesNotExist:
                user_rating = UserRating()
                user_rating.user = user
                user_rating.rated_by = self.request.user
                user_rating.job_type = job_type
            user_rating.rating = data_dict['rating']
            user_rating.save()
            # try:
            #     user_rating_combined = UserRatingCombined.objects.filter(
            #                             Q(user=data_dict['user']) &
            #                             Q(job_type=data_dict['job_type'])
            #                             )
            #     count = UserRating.objects.filter(
            #             Q(user=user) &
            #             Q(job_type=job_type)
            #             ).count()
            #     rating = user_rating_combined.rating
            #     total_rating = user_rating_combined.total_rating
            #     # new_rating = 
            # except UserRating.DoesNotExist:
            #     user_rating_combined = UserRatingCombined()
            #     user = CustomUser.objects.get(id=data_dict['user'])
            #     job_type = JobType.objects.get(id=data_dict['job_type'])
            #     user_rating_combined.user = user
            #     user_rating_combined.job_type = job_type
            #     user_rating_combined.rating = data_dict['rating']

            response = {'message': "User skill rated sucessfully",
                        'status': status.HTTP_200_OK}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class TrackUserAPI(APIView):
    serializer_class = TrackUserSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        try:
            trackers_dict = {}
            tracking_dict = {}
            track_obj = UserTacking.objects.get(user=user)
            trackers_list = track_obj.tracked_by.all()
            # trackers_list_ids = trackers_list.values_list('id', flat=True)
            tracking_list = UserTacking.objects.filter(
                            tracked_by=user)
            tracking_list_ids = tracking_list.values_list(
                                'user__id', flat=True)
            for user in trackers_list:
                trackers_dict[user.id] = UserSerializer(user).data
            tracking_users = CustomUser.objects.filter(id__in=tracking_list_ids)
            for user in tracking_users:
                tracking_dict[user.id] = UserSerializer(user).data
            response = {'Trackers': trackers_dict,
                        'Tracking': tracking_dict,
                        'status': status.HTTP_200_OK}
        except UserTacking.DoesNotExist:
            response = {'errors': "Trackers list is empty", 'status':
                        status.HTTP_200_OK}
        return Response(response)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            track_id = data_dict['track_id']
            track_user = CustomUser.objects.get(id=track_id)
            track_by_user = self.request.user

            can_track = False
            track_user_settings = CustomUserSettings.objects.get(user=track_user)
            permission = track_user_settings.who_can_track_me

            track_by_user_rating = UserRatingCombined.objects.filter(
                                   user=track_by_user)
            one_star_count = track_by_user_rating.filter(rating__gte=1).count()
            two_star_count = track_by_user_rating.filter(rating__gte=2).count()
            three_star_count = track_by_user_rating.filter(
                               rating__gte=3).count()
            four_star_count = track_by_user_rating.filter(
                              rating__gte=4).count()
            five_star_count = track_by_user_rating.filter(
                              rating__gte=5).count()

            if permission == 'no_one':
                can_track = False
            if permission == 'all_members':
                can_track = True
            if permission == 'pros_and_companies_only' and track_by_user.membership == 'COM':
                can_track = True
            if permission == 'members_with_rating_1_star' and one_star_count >= 1:
                can_track = True
            if permission == 'members_with_rating_2_star' and two_star_count >= 1:
                can_track = True
            if permission == 'members_with_rating_3_star' and three_star_count >= 1:
                can_track = True
            if permission == 'members_with_rating_4_star' and four_star_count >= 1:
                can_track = True
            if permission == 'members_with_rating_5_star' and five_star_count >= 1:
                can_track = True

            if can_track == True:
                try:
                    track_obj = UserTacking.objects.get(user=track_user)
                    trackers_list = track_obj.tracked_by.all()
                    if track_by_user in trackers_list:
                        response = {'message': "You are already tracking this user",
                                    'status': status.HTTP_400_BAD_REQUEST,
                                    'track_status': 'tracking'
                                    }
                        return Response(response)
                    track_obj.tracked_by.add(track_by_user.id)
                except UserTacking.DoesNotExist:
                    track_obj = UserTacking()
                    track_obj.user = track_user
                    track_obj.save()
                    track_obj.tracked_by.add(track_by_user.id)
                msg = "Started Tracking " + track_user.get_full_name()
                response = {'message': msg,
                            'status': status.HTTP_200_OK,
                            'track_status':'tracking'}
            else:
                response = {'message': "You cannot track this user",
                            'status': status.HTTP_200_OK,
                            'track_status':'not_tracking'}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class UnTrackUserAPI(APIView):
    serializer_class = TrackUserSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            track_id = data_dict['track_id']
            track_user = CustomUser.objects.get(id=track_id)
            track_by_user = self.request.user

            try:
                track_obj = UserTacking.objects.get(user=track_user)
                track_obj.tracked_by.remove(track_by_user.id)
            except UserTacking.DoesNotExist:
                response = {'errors': "invalid id", 'status':
                             status.HTTP_400_BAD_REQUEST}
            msg = "Stopped Tracking " + track_user.get_full_name()
            response = {'message': msg,
                        'status': status.HTTP_200_OK,
                        'track_status':'not_tracking'}

        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class FriendsAndFollowersView(LoginRequiredMixin, TemplateView):
    template_name = 'user_pages/friends-and-followers.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        track_obj = UserTacking.objects.get(user=user)
        trackers_list = track_obj.tracked_by.all()
        tracking_list = UserTacking.objects.filter(
                        tracked_by=user)
        photos = Photo.objects.filter(user=user).order_by('position')

        context['trackers_list'] = trackers_list
        context['tracking_list'] = tracking_list
        context['photos'] = photos
        context['user'] = user
        return context


class ChangePhotoPositionAPI(APIView):
    serializer_class = PhotoSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            id = data_dict['id']
            position = data_dict['position']
            try:
                swap_obj1 = Photo.objects.get(id=id)
                try:
                    swap_obj2 = Photo.objects.get(Q(position=position) & Q(user=user))
                    pos_1 = swap_obj1.position
                    pos_2 = swap_obj2.position
                    swap_obj1.position, swap_obj2.position  = swap_obj2.position, swap_obj1.position
                    swap_obj1.save()
                    swap_obj2.save()
                except Photo.DoesNotExist:
                    swap_obj1.position = position
                    swap_obj1.save()
            except Photo.DoesNotExist:
                response = {'errors': "invalid id provided", 'status':
                             status.HTTP_400_BAD_REQUEST}
            response = {'message': "Position Swapped",
                        'status': status.HTTP_200_OK}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class SwapImageAjaxView(View, JSONResponseMixin):
    template_name = 'user_pages/swap-images.html'

    def get(self, *args, **kwargs):
        context = dict()
        photos_dict = dict()
        user = self.request.user
        id = self.request.GET.get('id')
        position = self.request.GET.get('position')
        try:
            swap_obj1 = Photo.objects.get(id=id)
            try:
                swap_obj2 = Photo.objects.get(Q(position=position) & Q(user=user))
                pos_1 = swap_obj1.position
                pos_2 = swap_obj2.position
                swap_obj1.position, swap_obj2.position  = swap_obj2.position, swap_obj1.position
                swap_obj1.save()
                swap_obj2.save()
            except Photo.DoesNotExist:
                swap_obj1.position = position
                swap_obj1.save()

        except Photo.DoesNotExist:
            pass
        return self.render_json_response(context)


class UploadImageView(LoginRequiredMixin, TemplateView):
    template_name = 'user_pages/friends-and-followers.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        position = self.request.POST.get('position')
        file = self.request.FILES['image']

        photo_obj = Photo.objects.filter(Q(user=user) & Q(position=position)).first()
        if photo_obj:
            photo_obj.image = file
            photo_obj.save()
        else:
            photo_obj = Photo()
            photo_obj.image = file
            photo_obj.position = position
            photo_obj.user = user
            photo_obj.save()
        return HttpResponseRedirect(reverse("hobo_user:friends-and-followers"))


class UploadImageAPI(APIView):
    serializer_class = UploadPhotoSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            print(data_dict)
            user = self.request.user
            position = data_dict['position']
            file =  request.data['file']
            photo_obj = Photo.objects.filter(Q(user=user) & Q(position=position)).first()
            if photo_obj:
                photo_obj.image = file
                photo_obj.save()
            else:
                photo_obj = Photo()
                photo_obj.image = file
                photo_obj.position = position
                photo_obj.user = user
                photo_obj.save()
            response = {'message': "Image Uploaded",
                        'status': status.HTTP_200_OK}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)