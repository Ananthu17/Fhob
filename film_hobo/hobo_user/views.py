import ast
import braintree
import datetime
import json
import requests
from authemail.models import SignupCode
from braces.views import JSONResponseMixin
from datetime import timedelta, date

from django.core.files import File
from django.db.models import Sum, Q, query
from django.template import loader
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.views import LoginView as DjangoLogin
from django.contrib.auth.views import LogoutView as DjangoLogout
from django.http import FileResponse

from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.generic import TemplateView, View, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework import authentication
from rest_framework import status
from rest_framework import permissions
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_auth.registration.views import RegisterView
from rest_auth.views import LoginView as AuthLoginView
from rest_auth.views import LogoutView as AuthLogoutView
from rest_auth.views import PasswordChangeView as AuthPasswordChangeView
from rest_auth.views import PasswordResetView as AuthPasswordResetView
from rest_auth.views import PasswordResetConfirmView as \
    AuthPasswordResetConfirmView
from rest_framework.generics import (ListAPIView,
                                     CreateAPIView, DestroyAPIView,
                                     UpdateAPIView, RetrieveAPIView)
from django_filters.rest_framework import DjangoFilterBackend
from authemail.views import SignupVerify

from .forms import SignUpForm, LoginForm, SignUpIndieForm, \
    SignUpFormCompany, SignUpProForm, ChangePasswordForm, \
    ForgotPasswordEmailForm, ResetPasswordForm, PersonalDetailsForm, \
    EditProfileForm, EditProductionCompanyProfileForm, UserInterestForm, \
    EditAgencyManagementCompanyProfileForm, CheckoutForm, \
    ProjectCreationForm, WriterForm

from .models import CoWorker, CompanyClient, CustomUser, FriendRequest, \
                    GuildMembership, GroupUsers, Video, \
                    IndiePaymentDetails, Photo, ProPaymentDetails, \
                    VideoRating, PromoCode, DisabledAccount, \
                    CustomUserSettings, CompanyPaymentDetails, \
                    AthleticSkill, AthleticSkillInline, \
                    EthnicAppearance, UserAgentManager, UserInterest, \
                    UserNotification, Friend, FriendGroup, \
                    Project, Team, UserProfile, JobType, \
                    UserRating, Location, UserRatingCombined, \
                    UserTracking, CompanyProfile, UserProject, \
                    Feedback, CompanyRating, CompanyRatingCombined, \
                    VideoRatingCombined, BetaTesterCodes
from payment.models import Transaction

from .serializers import CustomUserSerializer, RegisterSerializer, \
    RegisterIndieSerializer, TokenSerializer, RegisterProSerializer, \
    SignupCodeSerializer, PaymentPlanSerializer, IndiePaymentSerializer, \
    ProPaymentSerializer, PromoCodeSerializer, \
    RegisterCompanySerializer, DisableAccountSerializer, \
    EnableAccountSerializer, BlockMembersSerializer, \
    CompanyPaymentSerializer, SettingsSerializer, \
    BlockedMembersQuerysetSerializer, PersonalDetailsSerializer, \
    PasswordResetSerializer, UserProfileSerializer, CoWorkerSerializer, \
    RemoveCoWorkerSerializer, \
    AgentManagerSerializer, RemoveAgentManagerSerializer, \
    TrackUserSerializer, UserSerializer, \
    GetSettingsSerializer, PhotoSerializer, UploadPhotoSerializer, \
    UserNotificationSerializer, ChangeNotificationStatusSerializer, \
    ProductionCompanyProfileSerializer, UserInterestSerializer, \
    AgentManagementCompanyProfileSerializer, CompanyClientSerializer, \
    RemoveClientSerializer, FriendRequestSerializer, \
    AcceptFriendRequestSerializer, AddGroupSerializer, \
    AddFriendToGroupSerializer, RemoveFriendGroupSerializer, \
    FeedbackSerializer, RateCompanySerializer, \
    ProjectSerializer, TeamSerializer, \
    EditUserInterestSerializer, \
    VideoRatingSerializer, VideoSerializer, AddBetaTesterCodeSerializer
from payment.views import IsSuperUser

from .mixins import SegregatorMixin, SearchFilter
from .utils import notify, get_notifications_time
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

CHECKBOX_MAPPING = {'on': True,
                    'off': False}


class AdminAuthenticationPermission(permissions.BasePermission):
    ADMIN_ONLY_AUTH_CLASSES = [authentication.BasicAuthentication, authentication.SessionAuthentication]

    def has_permission(self, request, view):
        user = request.user
        if user and user.is_authenticated():
            return user.is_superuser or \
                not any(isinstance(
                    request._authenticator, x) for x in self.ADMIN_ONLY_AUTH_CLASSES)
        return False


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
        user_input_data['membership'] = CustomUser.PRODUCTION_COMPANY
        if user_input_data['beta_user'] == '':
            user_input_data['beta_user'] = False
        if user_input_data['beta_user_code'] == '':
            user_input_data['beta_user_code'] = None
        if user_input_data['beta_user_end'] == '':
            user_input_data['beta_user_end'] = None
        serializer = RegisterCompanySerializer(data=user_input_data)
        serializer.is_valid()
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        obj = CustomUserSettings()
        obj.user = user
        obj.save()
        profile = CompanyProfile()
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
            origin_url = settings.ORIGIN_URL
            complete_url = origin_url + '/hobo_user/registration/'
            user_response = requests.post(
                            complete_url,
                            data=json.dumps(request.POST),
                            headers={'Content-type': 'application/json'})
            if user_response.status_code == 201:
                new_user = CustomUser.objects.get(
                           email=request.POST['email'])
                new_user.registration_complete = True
                new_user.save()
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
        return Response()


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
            origin_url = settings.ORIGIN_URL
            complete_url = origin_url + '/hobo_user/registration_indie/'
            user_response = requests.post(
                complete_url,
                data=json.dumps(request.POST),
                headers={'Content-type': 'application/json'})
            if user_response.status_code == 201:
                new_user = CustomUser.objects.get(
                           email=request.POST['email'])
                new_user.registration_complete = True
                new_user.save()
                if must_validate_email:
                    ipaddr = self.request.META.get('REMOTE_ADDR', '0.0.0.0')
                    signup_code = SignupCode.objects.create_signup_code(
                            new_user, ipaddr)
                    signup_code.send_signup_email()

                return render(request,
                              'user_pages/user_email_verification.html',
                              {'user': new_user})
            else:
                return render(request, 'user_pages/signup_indie.html',
                              {'form': form})
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
            origin_url = settings.ORIGIN_URL
            complete_url = origin_url + '/hobo_user/registration_pro/'
            user_response = requests.post(
                complete_url,
                data=json.dumps(json_dict),
                headers={'Content-type': 'application/json'})
            if user_response.status_code == 201:
                new_user = CustomUser.objects.get(
                           email=request.POST['email'])
                new_user.registration_complete = True
                new_user.save()
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
            origin_url = settings.ORIGIN_URL
            complete_url = origin_url + '/hobo_user/registration_company/'
            user_response = requests.post(
                complete_url,
                data=json.dumps(request.POST),
                headers={'Content-type': 'application/json'})
            if user_response.status_code == 201:
                new_user = CustomUser.objects.get(
                           email=request.POST['email'])
                new_user.registration_complete = True
                new_user.save()
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
        origin_url = settings.ORIGIN_URL
        complete_url = origin_url + '/hobo_user/indie_payment_details_api/'
        user_response = requests.get(
                complete_url,
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
        origin_url = settings.ORIGIN_URL
        complete_url = origin_url + '/hobo_user/select-payment-plan-api/'
        user_response = requests.post(
                    complete_url,
                    data=json.dumps(request.POST),
                    headers={'Content-type': 'application/json',
                             'Authorization': token})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        response = ast.literal_eval(dict_str)
        email = response['email']
        if user.beta_user_code is not None:
            return_url = "/hobo_user/payment_indie?email=" + email + \
                        "&user_token=" + key + \
                        "&beta_code=" + user.beta_user_code.code
        else:
            return_url = "/hobo_user/payment_indie?email=" + email + \
                        "&user_token=" + key
        return HttpResponseRedirect(return_url)


class SelectPaymentPlanProView(TemplateView):
    template_name = 'user_pages/payment_plan_pro.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.request.GET.get('email')
        user = CustomUser.objects.get(email=email)
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        origin_url = settings.ORIGIN_URL
        complete_url = origin_url + '/hobo_user/pro_payment_details_api/'
        user_response = requests.get(
                complete_url,
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
        origin_url = settings.ORIGIN_URL
        complete_url = origin_url + '/hobo_user/select-payment-plan-api/'
        user_response = requests.post(
                            complete_url,
                            data=json.dumps(request.POST),
                            headers={'Content-type': 'application/json',
                                     'Authorization': token})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        response = ast.literal_eval(dict_str)
        email = response['email']
        if user.beta_user_code is not None:
            return_url = "/hobo_user/payment_pro?email=" + email + \
                        "&user_token=" + key + \
                        "&beta_code=" + user.beta_user_code.code
        else:
            return_url = "/hobo_user/payment_pro?email=" + email + \
                        "&user_token=" + key
        return HttpResponseRedirect(return_url)


class SelectPaymentPlanCompanyView(TemplateView):
    template_name = 'user_pages/payment_plan_company.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.request.GET.get('email')
        user = CustomUser.objects.get(email=email)
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        origin_url = settings.ORIGIN_URL
        complete_url = origin_url + '/hobo_user/company_payment_details_api/'
        user_response = requests.get(
                complete_url,
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
        origin_url = settings.ORIGIN_URL
        complete_url = origin_url + '/hobo_user/select-payment-plan-api/'
        user_response = requests.post(
                            complete_url,
                            data=json.dumps(request.POST),
                            headers={'Content-type': 'application/json',
                                     'Authorization': token})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        response = ast.literal_eval(dict_str)
        email = response['email']
        if user.beta_user_code is not None:
            return_url = "/hobo_user/payment_company?email=" + email + \
                        "&user_token=" + key + \
                        "&beta_code=" + user.beta_user_code.code
        else:
            return_url = "/hobo_user/payment_company?email=" + email + \
                        "&user_token=" + key
        return HttpResponseRedirect(return_url)


class PaymentIndieView(FormView):
    form_class = CheckoutForm
    template_name = 'user_pages/payment.html'

    def dispatch(self, request, *args, **kwargs):
        user_email = request.GET.get('email')
        self.user = CustomUser.objects.get(email=user_email)

        # if settings.BRAINTREE_PRODUCTION:
        #     braintree_env = braintree.Environment.Production
        # else:
        #     braintree_env = braintree.Environment.Sandbox

        # braintree.Configuration.configure(
        #     braintree_env,
        #     merchant_id=settings.BRAINTREE_MERCHANT_ID,
        #     public_key=settings.BRAINTREE_PUBLIC_KEY,
        #     private_key=settings.BRAINTREE_PRIVATE_KEY,
        # )
        # self.braintree_client_token = braintree.ClientToken.generate({})

        # gateway = braintree.BraintreeGateway(
        #     braintree.Configuration(
        #         braintree.Environment.Sandbox,
        #         merchant_id=settings.BRAINTREE_MERCHANT_ID,
        #         public_key=settings.BRAINTREE_PUBLIC_KEY,
        #         private_key=settings.BRAINTREE_PRIVATE_KEY
        #     )
        # )
        # self.braintree_client_token = \
        #     gateway.client_token.generate()

        return super(PaymentIndieView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.request.GET.get('email')
        user = CustomUser.objects.get(email=email)
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        origin_url = settings.ORIGIN_URL
        complete_url = origin_url + '/hobo_user/indie_payment_details_api/'
        user_response = requests.get(
                complete_url,
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
        # context['braintree_client_token'] = ''
        # context.update({
        #     'braintree_client_token': self.braintree_client_token,
        # })
        return context

    # def form_valid(self, form):
    #     # Braintree customer info
    #     email = self.request.GET.get('email')
    #     user = CustomUser.objects.get(email=email)

    #     customer_kwargs = {
    #         "first_name": user.first_name,
    #         "last_name": user.middle_name + ' ' + user.last_name,
    #         "email": email,
    #     }

    #     # Create a new Braintree customer
    #     # In this example we always create new Braintree users
    #     # You can store and re-use Braintree's customer IDs, if you want to
    #     result = braintree.Customer.create(customer_kwargs)
    #     if not result.is_success:
    #         context = self.get_context_data()

    #         # We re-generate the form and display the relevant braintree error
    #         context.update({
    #             'form': self.get_form(self.get_form_class()),
    #             'braintree_error': u'{} {}'.format(
    #                 result.message, _('Please get in contact.'))
    #         })
    #         return self.render_to_response(context)

    #     # If the customer creation was successful you might want to also
    #     # add the customer id to your user profile
    #     customer_id = result.customer.id

    #     """
    #     Create a new transaction and submit it.
    #     I don't gather the whole address in this example, but I can
    #     highly recommend to do that. It will help you to avoid any
    #     fraud issues, since some providers require matching addresses

    #     """
    #     address_dict = {
    #         "first_name": user.first_name,
    #         "last_name": user.middle_name + ' ' + user.last_name,
    #         "extended_address": user.address,
    #         "country_name": user.country.name,
    #     }

    #     result = braintree.Transaction.sale({
    #         "customer_id": customer_id,
    #         "amount": 100,
    #         "payment_method_nonce": form.cleaned_data['payment_method_nonce'],
    #         "descriptor": {
    #             "name": "Filmhobo.*test",
    #         },
    #         "billing": address_dict,
    #         "shipping": address_dict,
    #         "options": {
    #             'store_in_vault_on_success': True,
    #             'submit_for_settlement': True,
    #         },
    #     })
    #     if not result.is_success:
    #         context = self.get_context_data()
    #         context.update({
    #             'form': self.get_form(self.get_form_class()),
    #             'braintree_error': _(
    #                 'Your payment could not be processed. Please check your'
    #                 ' input or use another payment method and try again.')
    #         })
    #         return self.render_to_response(context)

    #     # Finally there's the transaction ID
    #     # You definitely want to send it to your database
    #     transaction_id = result.transaction.id
    #     # Now you can send out confirmation emails or update your metrics
    #     # or do whatever makes you and your customers happy :)
    #     return super(PaymentIndieView, self).form_valid(form)

    def get_success_url(self):
        return reverse('hobo_user:user_home')


class PaymentProView(TemplateView):
    template_name = 'user_pages/payment.html'

    def dispatch(self, request, *args, **kwargs):
        user_email = request.GET.get('email')
        self.user = CustomUser.objects.get(email=user_email)

        # if settings.BRAINTREE_PRODUCTION:
        #     braintree_env = braintree.Environment.Production
        # else:
        #     braintree_env = braintree.Environment.Sandbox

        # braintree.Configuration.configure(
        #     braintree_env,
        #     merchant_id=settings.BRAINTREE_MERCHANT_ID,
        #     public_key=settings.BRAINTREE_PUBLIC_KEY,
        #     private_key=settings.BRAINTREE_PRIVATE_KEY,
        # )
        # self.braintree_client_token = braintree.ClientToken.generate({})

        gateway = braintree.BraintreeGateway(
            braintree.Configuration(
                braintree.Environment.Sandbox,
                merchant_id=settings.BRAINTREE_MERCHANT_ID,
                public_key=settings.BRAINTREE_PUBLIC_KEY,
                private_key=settings.BRAINTREE_PRIVATE_KEY
            )
        )
        self.braintree_client_token = \
            gateway.client_token.generate()

        return super(PaymentProView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.request.GET.get('email')
        user = CustomUser.objects.get(email=email)
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        origin_url = settings.ORIGIN_URL
        complete_url = origin_url + '/hobo_user/pro_payment_details_api/'
        user_response = requests.get(
                complete_url,
                headers={'Content-type': 'application/json',
                         'Authorization': token})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        payment_details = ast.literal_eval(dict_str)
        context['user'] = user
        context['payment_details'] = payment_details
        context['payment_plan'] = user.payment_plan
        free_evaluation_time = payment_details['free_days']
        date_today = datetime.date.today()
        date_interval = datetime.timedelta(days=int(free_evaluation_time))
        bill_date = date_today + date_interval
        context['bill_date'] = bill_date
        context['braintree_client_token'] = ''
        context.update({
            'braintree_client_token': self.braintree_client_token,
        })
        return context


class PaymentCompanyView(TemplateView):
    template_name = 'user_pages/payment.html'

    def dispatch(self, request, *args, **kwargs):
        user_email = request.GET.get('email')
        self.user = CustomUser.objects.get(email=user_email)

        # if settings.BRAINTREE_PRODUCTION:
        #     braintree_env = braintree.Environment.Production
        # else:
        #     braintree_env = braintree.Environment.Sandbox

        # braintree.Configuration.configure(
        #     braintree_env,
        #     merchant_id=settings.BRAINTREE_MERCHANT_ID,
        #     public_key=settings.BRAINTREE_PUBLIC_KEY,
        #     private_key=settings.BRAINTREE_PRIVATE_KEY,
        # )
        # self.braintree_client_token = braintree.ClientToken.generate({})

        gateway = braintree.BraintreeGateway(
            braintree.Configuration(
                braintree.Environment.Sandbox,
                merchant_id=settings.BRAINTREE_MERCHANT_ID,
                public_key=settings.BRAINTREE_PUBLIC_KEY,
                private_key=settings.BRAINTREE_PRIVATE_KEY
            )
        )
        self.braintree_client_token = \
            gateway.client_token.generate()

        return super(PaymentCompanyView, self).dispatch(
            request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.request.GET.get('email')
        user = CustomUser.objects.get(email=email)
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        origin_url = settings.ORIGIN_URL
        complete_url = origin_url + '/hobo_user/company_payment_details_api/'
        user_response = requests.get(
                complete_url,
                headers={'Content-type': 'application/json',
                         'Authorization': token})
        byte_str = user_response.content
        dict_str = byte_str.decode("UTF-8")
        payment_details = ast.literal_eval(dict_str)
        context['user'] = user
        context['payment_details'] = payment_details
        context['payment_plan'] = user.payment_plan
        free_evaluation_time = payment_details['free_days']
        date_today = datetime.date.today()
        date_interval = datetime.timedelta(days=int(free_evaluation_time))
        bill_date = date_today + date_interval
        context['bill_date'] = bill_date
        context['braintree_client_token'] = ''
        context.update({
            'braintree_client_token': self.braintree_client_token,
        })
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
        message = ""
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        origin_url = settings.ORIGIN_URL
        complete_url = origin_url + '/hobo_user/enable-account-api/'
        user_response = requests.post(
                            complete_url,
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
                blocked_members[obj.id] = obj.first_name + " " + obj.last_name
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
        origin_url = settings.ORIGIN_URL
        complete_url = origin_url + '/hobo_user/forgot-password-api/'
        user_response = requests.post(
                            complete_url,
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
        origin_url = settings.ORIGIN_URL
        complete_url = origin_url + '/password-reset-confirm/'+uid+"/"+token
        user_response = requests.post(
                            complete_url,
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
            if 'hide_ratings' in data_dict:
                user_settings.hide_ratings = data_dict[
                                        'hide_ratings']
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
        context['transaction'] = \
            Transaction.objects.get(user_id=user.id)
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
        hide_ratings = CHECKBOX_MAPPING.get(
                            request.POST.get('hide_ratings', 'off'))

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
        json_dict['hide_ratings'] = hide_ratings
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        origin_url = settings.ORIGIN_URL
        complete_url = origin_url + '/hobo_user/update-settings-api/'
        user_response = requests.post(
                            complete_url,
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
        response = {"personal_settings": personal_settings}
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
        origin_url = settings.ORIGIN_URL
        complete_url = origin_url + '/hobo_user/personal-details-api/'
        user_response = requests.post(
                            complete_url,
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


class ProductionCompanyProfileAPI(APIView):
    serializer_class = ProductionCompanyProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        profile = CompanyProfile.objects.get(user=user)
        profile_data = {}

        profile_data['membership'] = user.membership
        profile_data['company_name'] = user.company_name
        profile_data['company_website'] = user.company_website
        profile_data['imdb'] = profile.imdb
        profile_data['bio'] = profile.bio
        profile_data['submission_policy_SAMR'] = profile.submission_policy_SAMR
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
        profile = CompanyProfile.objects.get(user=user)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            if 'company_name' in data_dict:
                user.company_name = data_dict['company_name']
            if 'company_website' in data_dict:
                user.company_website = data_dict['company_website']
            user.save()
            if 'imdb' in data_dict:
                profile.imdb = data_dict['imdb']
            if 'bio' in data_dict:
                profile.bio = data_dict['bio']
            if 'submission_policy_SAMR' in data_dict:
                profile.submission_policy_SAMR = data_dict[
                                                'submission_policy_SAMR']
            profile.save()
            response = {'message': "Profile Updated",
                        'status': status.HTTP_200_OK}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}

        return Response(response)


class AgencyManagementCompanyProfileAPI(APIView):
    serializer_class = AgentManagementCompanyProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        profile = CompanyProfile.objects.get(user=user)
        profile_data = {}

        profile_data['membership'] = user.membership
        profile_data['company_name'] = user.company_name
        profile_data['company_website'] = user.company_website
        profile_data['agency_management_type'] = user.agency_management_type
        profile_data['bio'] = profile.bio
        profile_data['submission_policy_SAMR'] = profile.submission_policy_SAMR
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
        profile = CompanyProfile.objects.get(user=user)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            if 'company_name' in data_dict:
                user.company_name = data_dict['company_name']
            if 'company_website' in data_dict:
                user.company_website = data_dict['company_website']
            if 'agency_management_type' in data_dict:
                user.agency_management_type = data_dict[
                                'agency_management_type']
            user.save()
            if 'bio' in data_dict:
                profile.bio = data_dict['bio']
            if 'submission_policy_SAMR' in data_dict:
                profile.submission_policy_SAMR = data_dict[
                                                'submission_policy_SAMR']
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
        all_photos = Photo.objects.filter(user=user).order_by('position')
        photos = all_photos.filter(position__in=pos_list).order_by('position')
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

        try:
            track_obj = UserTracking.objects.get(user=user)
            trackers_list = track_obj.tracked_by.all()
            context['trackers_list_count'] = trackers_list.count()
            context['trackers_list'] = trackers_list[:6]
        except UserTracking.DoesNotExist:
            context['trackers_list_count'] = 0
        tracking_list = UserTracking.objects.filter(tracked_by=user)
        context['tracking_list_count'] = tracking_list.count()
        context['tracking_list'] = tracking_list[:6]

        try:
            friend_obj = Friend.objects.get(user=user)
            friends = friend_obj.friends.all()
            context['friends'] = friends[:8]
        except Friend.DoesNotExist:
            pass
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
            origin_url = settings.ORIGIN_URL
            complete_url = origin_url + '/hobo_user/edit-agent-manager-api/'
            user_response = requests.post(
                    complete_url,
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
                origin_url = settings.ORIGIN_URL
                complete_url = origin_url + '/hobo_user/add-agent-manager-api/'
                user_response = requests.post(
                                    complete_url,
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
            origin_url = settings.ORIGIN_URL
            complete_url = origin_url + '/hobo_user/remove-agent-api/'
            user_response = requests.post(
                                complete_url,
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
        origin_url = settings.ORIGIN_URL
        complete_url = origin_url + '/hobo_user/profile-api/'
        user_response = requests.post(
                            complete_url,
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


class EditProductionCompanyView(LoginRequiredMixin, TemplateView):
    template_name = 'user_pages/edit-production.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'
    form_class = EditProductionCompanyProfileForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile = get_object_or_404(CompanyProfile, user=user)
        print(profile)
        print(user)
        context['user'] = user
        context['profile'] = profile
        pos_list = [2, 3, 4]
        all_photos = Photo.objects.filter(user=user)
        photos = all_photos.filter(position__in=pos_list).order_by('position')
        context['photos'] = photos[:3]
        context['all_photos'] = all_photos.order_by('position')[:4]
        context['form'] = self.form_class(instance=profile)

        coworkers = CoWorker.objects.filter(company=user)
        context['coworkers'] = coworkers
        context['job_types'] = JobType.objects.all()
        context['my_interest_form'] = UserInterestForm
        try:
            track_obj = UserTracking.objects.get(user=user)
            trackers_list = track_obj.tracked_by.all()
            context['trackers_list_count'] = trackers_list.count()
            context['trackers_list'] = trackers_list[:6]
        except UserTracking.DoesNotExist:
            context['trackers_list_count'] = 0
        tracking_list = UserTracking.objects.filter(tracked_by=user)
        context['tracking_list_count'] = tracking_list.count()
        context['tracking_list'] = tracking_list[:6]

        try:
            friend=Friend.objects.all()
            if(friend):
                friend_obj = Friend.objects.get(user=user)
                friends = friend_obj.friends.all()
                context['friends'] = friends[:8]
                context['friends_list_count']=friends.count()
        except FriendRequest.DoesNotExist:
            context['friends'] = 0
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        print(request.POST)
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        profile = CompanyProfile.objects.get(user=user)
        json_response = json.dumps(request.POST)
        json_dict = ast.literal_eval(json_response)
        if 'submission_policy_SAMR' in json_dict:
            submission_policy_SAMR = json_dict['submission_policy_SAMR']
            if(submission_policy_SAMR == 'members_with_rating' and 'rate' in json_dict):
                SAMR_rate = json_dict['rate']
                if SAMR_rate == '1':
                    submission_policy = CustomUserSettings.MEMBERS_WITH_RATING_1_STAR
                if SAMR_rate == '2':
                    submission_policy = CustomUserSettings.MEMBERS_WITH_RATING_2_STAR
                if SAMR_rate == '3':
                    submission_policy = CustomUserSettings.MEMBERS_WITH_RATING_3_STAR
                if SAMR_rate == '4':
                    submission_policy = CustomUserSettings.MEMBERS_WITH_RATING_4_STAR
                if SAMR_rate == '5':
                    submission_policy = CustomUserSettings.MEMBERS_WITH_RATING_5_STAR
            elif submission_policy_SAMR != 'members_with_rating':
                submission_policy = json_dict['submission_policy_SAMR']
            else:
                messages.warning(
                    self.request,
                    'Cannot save!! Please provide ratings for submission policy SAMR'
                    )
                return HttpResponseRedirect(reverse('hobo_user:edit-production-company-profile'))
        else:
            submission_policy = ""
        json_dict['submission_policy_SAMR'] = submission_policy
        # Update Profile
        origin_url = settings.ORIGIN_URL
        complete_url = origin_url + '/hobo_user/production-company-profile-api/'
        user_response = requests.post(
                            complete_url,
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
                return HttpResponseRedirect(
                    "/hobo_user/production-company-profile/%s/" % (user.id))
            else:
                if 'errors' in response:
                    errors = response['errors']
                    messages.warning(self.request, "Failed to update profile !!")
                    return render(request, 'user_pages/edit-production.html',
                                  {'errors': errors,
                                   'form': self.form_class(instance=profile),
                                   'profile': profile,
                                   'user': user,
                                   })
        return HttpResponseRedirect("/hobo_user/production-company-profile/%s/" % (user.id))


class EditAgencyManagementCompanyView(LoginRequiredMixin, TemplateView):
    template_name = 'user_pages/edit-agency-management.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'
    form_class = EditAgencyManagementCompanyProfileForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile = get_object_or_404(CompanyProfile, user=user)
        context['user'] = user
        context['profile'] = profile
        pos_list = [2, 3, 4]
        client_dict = {}
        all_photos = Photo.objects.filter(user=user).order_by('position')
        photos = all_photos.filter(position__in=pos_list).order_by('position')
        clients = CompanyClient.objects.filter(company=self.request.user)
        for obj in clients:
            if obj.position is not None and obj.position not in client_dict:
                client_dict[obj.position] = []
                client_dict[obj.position].append(obj)
            elif obj.position is None and obj.new_position not in client_dict:
                client_dict[obj.new_position] = []
                client_dict[obj.new_position].append(obj)
            elif obj.position is not None and obj.position in client_dict:
                client_dict[obj.position].append(obj)
            elif obj.position is None and obj.new_position in client_dict:
                client_dict[obj.new_position].append(obj)
            else:
                pass

        context['photos'] = photos[:3]
        context['all_photos'] = all_photos[:4]
        context['form'] = self.form_class(instance=profile)
        coworkers = CoWorker.objects.filter(company=user)
        context['coworkers'] = coworkers
        context['job_types'] = JobType.objects.all()
        context['my_interest_form'] = UserInterestForm
        context['client_dict'] = client_dict

        try:
            track_obj = UserTracking.objects.get(user=user)
            trackers_list = track_obj.tracked_by.all()
            context['trackers_list_count'] = trackers_list.count()
            context['trackers_list'] = trackers_list[:6]
        except UserTracking.DoesNotExist:
            context['trackers_list_count'] = 0
        tracking_list = UserTracking.objects.filter(tracked_by=user)
        context['tracking_list_count'] = tracking_list.count()
        context['tracking_list'] = tracking_list[:6]
        try:
            friend_obj = Friend.objects.get(user=user)
            friends = friend_obj.friends.all()
            context['friends'] = friends[:8]
        except FriendRequest.DoesNotExist:
            pass
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        profile = CompanyProfile.objects.get(user=user)
        json_response = json.dumps(request.POST)
        json_dict = ast.literal_eval(json_response)
        if 'submission_policy_SAMR' in json_dict:
            submission_policy_SAMR = json_dict['submission_policy_SAMR']
            if(submission_policy_SAMR == 'members_with_rating' and 'rate' in json_dict):
                SAMR_rate = json_dict['rate']
                if SAMR_rate == '1':
                    submission_policy = CustomUserSettings.MEMBERS_WITH_RATING_1_STAR
                if SAMR_rate == '2':
                    submission_policy = CustomUserSettings.MEMBERS_WITH_RATING_2_STAR
                if SAMR_rate == '3':
                    submission_policy = CustomUserSettings.MEMBERS_WITH_RATING_3_STAR
                if SAMR_rate == '4':
                    submission_policy = CustomUserSettings.MEMBERS_WITH_RATING_4_STAR
                if SAMR_rate == '5':
                    submission_policy = CustomUserSettings.MEMBERS_WITH_RATING_5_STAR
            elif submission_policy_SAMR != 'members_with_rating':
                submission_policy = json_dict['submission_policy_SAMR']
            else:
                messages.warning(
                    self.request,
                    'Cannot save!! Please provide ratings for submission policy SAMR'
                    )
                return HttpResponseRedirect(reverse('hobo_user:edit-agency-management-company-profile'))
        else:
            submission_policy = ""
        json_dict['submission_policy_SAMR'] = submission_policy
        # Update Profile
        origin_url = settings.ORIGIN_URL
        complete_url = origin_url + '/hobo_user/agency-management-company-profile-api/'
        user_response = requests.post(
                            complete_url,
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
                return HttpResponseRedirect(
                    "/hobo_user/agency-management-company-profile/%s/" % (user.id))
            else:
                if 'errors' in response:
                    errors = response['errors']
                    messages.warning(self.request, "Failed to update profile !!")
                    return render(request, 'user_pages/edit-agency-management.html',
                                  {'errors': errors,
                                   'form': self.form_class(instance=profile),
                                   'profile': profile,
                                   'user': user,
                                   })
        return HttpResponseRedirect("/hobo_user/agency-management-company-profile/%s/" % (user.id))


class AddCoworkerAPI(APIView):
    serializer_class = CoWorkerSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        company = request.user
        if serializer.is_valid():
            data_dict = serializer.data
            coworker = CoWorker()
            coworker.company = company
            if 'position' in data_dict:
                position = JobType.objects.get(id=data_dict['position'])
                coworker.position = position
            if 'name' in data_dict:
                coworker.name = data_dict['name']
            if 'email' in data_dict:
                coworker.email = data_dict['email']
                try:
                    user = CustomUser.objects.get(email=data_dict['email'])
                    coworker.user = user
                    coworker.name = user.get_full_name()
                except CustomUser.DoesNotExist:
                    pass
            coworker.save()
            response = {'message': "Staff Added",
                        'id': coworker.id,
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
                    if 'user' in data_dict and data_dict['user'] != "":
                        user_id = data_dict['user']
                        user = CustomUser.objects.get(id=user_id)
                        coworker.user = user
                        coworker.name = user.get_full_name()
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
            agent_dict[agent.id] = self.serializer_class(agent).data
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
            remove_id = data_dict['id']
            if remove_id:
                try:
                    obj = CoWorker.objects.get(Q(id=remove_id) &
                                               Q(company=self.request.user))
                    obj.delete()
                    response = {'message': "Staff Removed",
                                'id': remove_id,
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


class RemoveClientAPI(APIView):
    serializer_class = RemoveClientSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            id = data_dict['id']
            if id:
                try:
                    obj = CompanyClient.objects.get(Q(id=id) &
                                                    Q(company=self.request.user))
                    obj.delete()
                except CompanyClient.DoesNotExist:
                    response = {'message': "Invalid Id",
                                'status': status.HTTP_400_BAD_REQUEST}
                    return Response(response)
                response = {'message': "Client Removed",
                            'id': id,
                            'status': status.HTTP_200_OK}
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


class AttachCoworkerAjaxView(View, JSONResponseMixin):
    template_name = 'user_pages/attach-coworker.html'

    def get(self, *args, **kwargs):
        context = dict()
        id = self.request.GET.get('id')
        coworker = CoWorker.objects.get(id=id)
        attach_coworker_html = render_to_string(
                                'user_pages/attach-coworker.html', {
                                    'coworker': coworker
                                    })
        context['attach_coworker_html'] = attach_coworker_html
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
            track_obj = UserTracking.objects.get(user=user)
            trackers_list = track_obj.tracked_by.all()
            context['trackers_list_count'] = trackers_list.count()
            context['trackers_list'] = trackers_list[:6]
        except UserTracking.DoesNotExist:
            context['trackers_list_count'] = 0
        tracking_list = UserTracking.objects.filter(tracked_by=user)
        context['tracking_list_count'] = tracking_list.count()
        context['tracking_list'] = tracking_list[:6]

        try:
            friend_obj = Friend.objects.get(user=user)
            friends = friend_obj.friends.all()
            context['friends'] = friends[:8]
        except Friend.DoesNotExist:
            pass
        try:
            profile = UserProfile.objects.get(user=user)
            all_agents = UserAgentManager.objects.filter(user=user)
            context['all_agents'] = all_agents.filter(agent_type='agent')
            context['all_managers'] = all_agents.filter(agent_type='manager')
            context['profile'] = profile
            pos_list = [2, 3, 4]
            all_photos = Photo.objects.filter(user=user)
            photos = all_photos.filter(position__in=pos_list).order_by('position')
            context['photos'] = photos[:3]

            rating_dict = {}
            job_dict = {}
            for job in profile.job_types.all():
                try:
                    rating_obj = UserRatingCombined.objects.get(
                                Q(user=user) &
                                Q(job_type=job))
                    rating = rating_obj.rating * 20
                    job_dict[job.id] = job.title
                    rating_dict[job.id] = rating
                except UserRatingCombined.DoesNotExist:
                    rating_dict[job.id] = 0
                    job_dict[job.id] = job.title
            context['job_dict'] = job_dict
            context['rating_dict'] = rating_dict
        except UserProfile.DoesNotExist:
            message = "No Data Available"
            context['message'] = message

        try:
            settings = CustomUserSettings.objects.get(user=user)
            context['settings'] = settings
        except CustomUserSettings.DoesNotExist:
            pass

        user_projects = UserProject.objects.filter(user=user)
        my_projects = user_projects.filter(relation_type = UserProject.ATTACHED).order_by('-created_time')
        favorites = user_projects.filter(relation_type = UserProject.FAVORITE).order_by('-created_time')
        applied = user_projects.filter(relation_type = UserProject.APPLIED).order_by('-created_time')
        context['my_projects'] = my_projects
        context['favorites'] = favorites
        context['applied'] = applied
        return context


class ProductionCompanyProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'user_pages/production-company-profile.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(CustomUser, id=self.kwargs.get('id'))
        context['user'] = user
        pos_list = [2, 3, 4]
        all_photos = Photo.objects.filter(user=user)
        photos = all_photos.filter(position__in=pos_list).order_by('position')
        context['photos'] = photos[:3]
        try:
            track_obj = UserTracking.objects.get(user=user)
            trackers_list = track_obj.tracked_by.all()
            context['trackers_list'] = trackers_list[:6]
            context['trackers_list_count'] = trackers_list.count()
        except UserTracking.DoesNotExist:
            pass
        tracking_list = UserTracking.objects.filter(
            tracked_by=user)
        context['tracking_list_count'] = tracking_list.count()
        context['tracking_list'] = tracking_list[:6]

        try:
            friend_obj = Friend.objects.get(user=user)
            friends = friend_obj.friends.all()
            context['friends'] = friends[:8]
        except Friend.DoesNotExist:
            pass
        try:
            profile = CompanyProfile.objects.get(user=user)
            context['profile'] = profile
        except CompanyProfile.DoesNotExist:
            message = "No Data Available"
            context['message'] = message
        try:
            coworkers = CoWorker.objects.filter(company=user)
            context['staff'] = coworkers
        except CoWorker.DoesNotExist:
            pass
        try:
            rating_obj = CompanyRatingCombined.objects.get(company=user)
            rating = rating_obj.rating * 20
        except CompanyRatingCombined.DoesNotExist:
            rating = 0
        context['rating'] = rating
        try:
            settings = CustomUserSettings.objects.get(user=user)
            context['settings'] = settings
        except CustomUserSettings.DoesNotExist:
            pass
        return context


class AgencyManagementCompanyProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'user_pages/agency-management-company-profile.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(CustomUser, id=self.kwargs.get('id'))
        context['user'] = user
        pos_list = [2, 3, 4]
        all_photos = Photo.objects.filter(user=user)
        photos = all_photos.filter(position__in=pos_list).order_by('position')
        context['photos'] = photos[:3]

        try:
            track_obj = UserTracking.objects.get(user=user)
            trackers_list = track_obj.tracked_by.all()
            context['trackers_list_count'] = trackers_list.count()
            context['trackers_list'] = trackers_list[:6]
        except UserTracking.DoesNotExist:
            context['trackers_list_count'] = 0
        tracking_list = UserTracking.objects.filter(tracked_by=user)
        context['tracking_list_count'] = tracking_list.count()
        context['tracking_list'] = tracking_list[:6]

        try:
            friend_obj = Friend.objects.get(user=user)
            friends = friend_obj.friends.all()
            context['friends'] = friends[:8]
        except Friend.DoesNotExist:
            pass
        try:
            profile = CompanyProfile.objects.get(user=user)
            context['profile'] = profile
        except CompanyProfile.DoesNotExist:
            message = "No Data Available"
            context['message'] = message
        try:
            coworkers = CoWorker.objects.filter(company=user)
            context['staff'] = coworkers
        except CoWorker.DoesNotExist:
            pass
        try:
            clients = CompanyClient.objects.filter(company=user)
            client_count = clients.count()
            context['client_count'] = client_count
            client_dict = {}
            for obj in clients:
                if obj.position is not None and obj.position not in client_dict:
                    client_dict[obj.position] = []
                    client_dict[obj.position].append(obj)
                elif obj.position is None and obj.new_position not in client_dict:
                    client_dict[obj.new_position] = []
                    client_dict[obj.new_position].append(obj)
                elif obj.position is not None and obj.position in client_dict:
                    client_dict[obj.position].append(obj)
                elif obj.position is None and obj.new_position in client_dict:
                    client_dict[obj.new_position].append(obj)
                else:
                    pass
            context['client_dict'] = client_dict
        except CompanyClient.DoesNotExist:
            pass
        try:
            rating_obj = CompanyRatingCombined.objects.get(company=user)
            rating = rating_obj.rating * 20
        except CompanyRatingCombined.DoesNotExist:
            rating = 0
        context['rating'] = rating
        try:
            settings = CustomUserSettings.objects.get(user=user)
            context['settings'] = settings
        except CustomUserSettings.DoesNotExist:
            pass
        return context


class RateCompanyAPI(APIView):
    serializer_class = RateCompanySerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        print("here----------------------")
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            company_id = data_dict['company']
            reason = data_dict['reason']
            rating = int(data_dict['rating'])
            company = CustomUser.objects.get(id=company_id)
            try:
                company_rating = CompanyRating.objects.get(
                            Q(company=company) &
                            Q(rated_by=self.request.user)
                            )
            except CompanyRating.DoesNotExist:
                company_rating = CompanyRating()
                company_rating.company = company
                company_rating.rated_by = self.request.user
            company_rating.rating = rating
            company_rating.reason = reason
            company_rating.save()

            # update combined rating
            try:
                company_rating_combined = CompanyRatingCombined.objects.get(
                                        company=company)
                count = CompanyRating.objects.filter(
                        company=company).count()
                aggregate_rating = CompanyRating.objects.filter(
                        company=company).aggregate(Sum('rating'))
                rating_sum = aggregate_rating['rating__sum']
                new_rating = rating_sum/count
                company_rating_combined.rating = new_rating
                company_rating_combined.save()
            except CompanyRatingCombined.DoesNotExist:
                company_rating_combined = CompanyRatingCombined()
                company_rating_combined.company = company
                company_rating_combined.rating = data_dict['rating']
                company_rating_combined.save()

            #update notification table
            notification = UserNotification()
            notification.user = company
            notification.notification_type = UserNotification.USER_RATING
            notification.from_user = self.request.user
            notification.message = self.request.user.get_full_name()+" rated you with "+str(rating)+" stars"
            notification.save()
            # send notification
            room_name = "user_"+str(company.id)
            notification_msg = {
                    'type': 'send_profile_rating_notification',
                    'message': str(notification.message),
                    'from': str(self.request.user.id),
                    "event": "USER_RATING"
                }
            notify(room_name, notification_msg)
            # end notification section

            response = {'message': "Company rated sucessfully",
                        'status': status.HTTP_200_OK,
                        'combined_rating': company_rating_combined.rating}
            msg = 'Rated '+data_dict['rating']+' stars !!'
            messages.success(
                    self.request, msg
                    )
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
            track_obj = UserTracking.objects.get(user=user)
            trackers_list = track_obj.tracked_by.all()
            # trackers_list_ids = trackers_list.values_list('id', flat=True)
            tracking_list = UserTracking.objects.filter(
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
        except UserTracking.DoesNotExist:
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
                    track_obj = UserTracking.objects.get(user=track_user)
                    trackers_list = track_obj.tracked_by.all()
                    if track_by_user in trackers_list:
                        response = {'message': "You are already tracking this user",
                                    'status': status.HTTP_400_BAD_REQUEST,
                                    'track_status': 'tracking'
                                    }
                        return Response(response)
                    track_obj.tracked_by.add(track_by_user.id)

                except UserTracking.DoesNotExist:
                    track_obj = UserTracking()
                    track_obj.user = track_user
                    track_obj.save()
                    track_obj.tracked_by.add(track_by_user.id)

                # update notification table
                notification = UserNotification()
                notification.user = track_user
                notification.notification_type = UserNotification.TRACKING
                notification.from_user = track_by_user
                notification.save()

                # send email
                try:
                    user_settings = CustomUserSettings.objects.get(user=track_user)
                    if user_settings.someone_tracks_me == True:
                        subject = track_by_user.first_name + ' started tracking you'
                        message = ''
                        msg_html = loader.render_to_string('user_pages/tracking_email.html',
                                    {'track_by_user': track_by_user,
                                    'first_name':track_user.first_name })
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = [track_user.email, ]
                        send_mail( subject, message, email_from, recipient_list, html_message=msg_html)
                except CustomUserSettings.DoesNotExist:
                    pass

                # send notification
                room_name = "user_"+str(track_obj.user.id)
                notification_msg = {
                        'type': 'send_notification',
                        'message': str(track_by_user.get_full_name()),
                        'track_by_user_id': str(track_by_user.id),
                        "event": "TRACK"
                    }
                notify(room_name, notification_msg)

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
                track_obj = UserTracking.objects.get(user=track_user)
                track_obj.tracked_by.remove(track_by_user.id)
                # remove from notification table
                try:
                    notification = UserNotification.objects.get(
                        Q(user=track_user) &
                        Q(from_user=track_by_user) &
                        Q(notification_type=UserNotification.TRACKING)
                        )
                    notification.delete()
                except UserNotification.DoesNotExist:
                    pass
            except UserTracking.DoesNotExist:
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
        if user.membership == CustomUser.PRODUCTION_COMPANY:
            try:
                profile = CompanyProfile.objects.get(user=user)
                context['profile'] = profile
            except CompanyProfile.DoesNotExist:
                pass
        else:
            try:
                profile = UserProfile.objects.get(user=user)
                context['profile'] = profile
            except UserProfile.DoesNotExist:
                pass
        try:
            friend_obj = Friend.objects.get(user=user)
            friends = friend_obj.friends.all()
            paginator = Paginator(friends, 20)
            page = self.request.GET.get('page1')
            try:
                friends = paginator.page(page)
            except PageNotAnInteger:
                friends = paginator.page(1)
            except EmptyPage:
                friends = paginator.page(paginator.num_pages)
            context['all_friends'] = friends
            context['friends'] = friends[:8]

        except Friend.DoesNotExist:
            pass
        try:
            track_obj = UserTracking.objects.get(user=user)
            trackers_list = track_obj.tracked_by.all()
            context['trackers_list_count'] = trackers_list.count()
            paginator = Paginator(trackers_list, 5)
            page = self.request.GET.get('page1')
            try:
                trackers_list = paginator.page(page)
            except PageNotAnInteger:
                trackers_list = paginator.page(1)
            except EmptyPage:
                trackers_list = paginator.page(paginator.num_pages)
            context['trackers_list'] = trackers_list
        except UserTracking.DoesNotExist:
            context['trackers_list_count'] = 0
        tracking_list = UserTracking.objects.filter(tracked_by=user)
        context['tracking_list_count'] = tracking_list.count()
        paginator = Paginator(tracking_list, 20)
        page = self.request.GET.get('page1')
        try:
            tracking_list = paginator.page(page)
        except PageNotAnInteger:
            tracking_list = paginator.page(1)
        except EmptyPage:
            tracking_list = paginator.page(paginator.num_pages)
        context['tracking_list'] = tracking_list
        pos_list = [2, 3, 4]
        all_photos = Photo.objects.filter(user=user)
        photos = all_photos.filter(position__in=pos_list).order_by('position')
        context['photos'] = photos[:3]
        context['all_photos'] = all_photos.order_by('position')[:4]
        myinterests = UserInterest.objects.filter(user=user)

        friend_request = FriendRequest.objects.filter(
                         Q(user=user) &
                         Q(status=FriendRequest.REQUEST_SEND)
                        )
        context['friend_request'] = friend_request
        context['friend_request_count'] = friend_request.count()
        context['myinterests'] = myinterests
        context['user'] = user
        groups = FriendGroup.objects.filter(user=user)
        context['groups'] = groups
        context['my_interest_form'] = UserInterestForm
        context['positions'] = JobType.objects.all()
        context['locations'] = Location.objects.all()
        context['format'] = UserInterest.FORMAT_CHOICES
        context['budget'] = UserInterest.BUDGET_CHOICES
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
        position = ""
        file = ""
        if 'position' in self.request.POST:
            position = self.request.POST.get('position')
        if 'image' in self.request.FILES:
            file = self.request.FILES['image']
        if position and file:
            try:
                photo_obj = Photo.objects.get(Q(user=user) & Q(position=position))
                photo_obj.image = file
                photo_obj.save()
            except Photo.DoesNotExist:
                photo_obj = Photo()
                photo_obj.image = file
                photo_obj.position = position
                photo_obj.user = user
                photo_obj.save()
        elif position and not file:
            messages.warning(
                    self.request,
                    'Cannot save!! Please upload image'
                    )
        elif file and not position:
            messages.warning(
                    self.request,
                    'Cannot save!! Please choose position'
                    )
        elif not file and not position:
            messages.warning(
                    self.request,
                    'Cannot save!! Please upload image and choose position'
                    )
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class AddUserInterestAPI(APIView):
    serializer_class = UserInterestSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_interests = UserInterest.objects.filter(user=self.request.user)
        data_dict = {}
        for obj in user_interests:
             serializer = self.serializer_class(obj).data
             data_dict[obj.id] = serializer
        return Response(data_dict)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            obj = UserInterest()
            obj.user = self.request.user
            obj.position = JobType.objects.get(pk=data_dict['position'])
            obj.location = Location.objects.get(pk=data_dict['location'])
            obj.format = data_dict['format']
            obj.budget = data_dict['budget']
            obj.save()
            response = {'message': "User interest added.",
                        'status': status.HTTP_200_OK}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class EditUserInterestAPI(APIView):
    serializer_class = EditUserInterestSerializer
    permission_classes = (IsAuthenticated,)


    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            id = data_dict['id']
            try:
                obj = UserInterest.objects.get(Q(pk=id) & Q(user=self.request.user))
                obj.position = JobType.objects.get(pk=data_dict['position'])
                obj.location = Location.objects.get(pk=data_dict['location'])
                obj.format = data_dict['format']
                obj.budget = data_dict['budget']
                obj.save()
                response = {'message': "User interest updated.",
                           'status': status.HTTP_200_OK}
            except UserInterest.DoesNotExist:
                response = {'message': "Invalid ID, Object not found.",
                           'status': status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class AddUserInterestView(LoginRequiredMixin, TemplateView):
    template_name = 'user_pages/edit-production.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        positions = self.request.POST.getlist('position')
        formats = self.request.POST.getlist('format')
        locations = self.request.POST.getlist('location')
        budget = self.request.POST.getlist('budget')
        count = len(locations)
        json_dict = {}
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        for i in range(count):
            print("count", i)
            json_dict['position'] = positions[i]
            json_dict['format'] = formats[i]
            json_dict['location'] = locations[i]
            json_dict['budget'] = budget[i]
            origin_url = settings.ORIGIN_URL
            complete_url = origin_url + '/hobo_user/add-user-interest-api/'
            user_response = requests.post(
                                complete_url,
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
                        errors = response['errors']
                        print(errors)
                        messages.warning(
                            self.request, "Failed to update My interests !!")
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        messages.success(self.request, "My Interests updated successfully")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class UploadImageAPI(APIView):
    serializer_class = UploadPhotoSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
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


class GetNotificationAPI(APIView):
    serializer_class = UserNotificationSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        response = {}
        notifications = UserNotification.objects.filter(
                        user=request.user).order_by('-created_time')
        unread_count = notifications.filter(status_type=UserNotification.UNREAD).count()
        for notification_obj in notifications:
            response[notification_obj.id] = self.serializer_class(notification_obj).data
        response['unread_count'] = unread_count
        return Response(response)


class GetTrackingNotificationAjaxView(View, JSONResponseMixin):
    template_name = 'user_pages/tracking_notification.html'

    def get(self, *args, **kwargs):
        context = dict()
        user = self.request.user
        id = self.request.GET.get('from_user')
        from_user = CustomUser.objects.get(id=id)
        notification_id = UserNotification.objects.get(
                            Q(user=self.request.user) &
                            Q(from_user=from_user) &
                            Q(notification_type=UserNotification.TRACKING)).id
        tracking_notification_html = render_to_string(
                                'user_pages/tracking_notification.html',
                                {'from_user': from_user,
                                'notification_id':notification_id,
                                })
        context['tracking_notification_html'] = tracking_notification_html
        return self.render_json_response(context)


class GetFriendRequestNotificationAjaxView(View, JSONResponseMixin):
    template_name = 'user_pages/friend_request_notification.html'

    def get(self, *args, **kwargs):
        context = dict()
        user = self.request.user
        id = self.request.GET.get('from_user')
        from_user = CustomUser.objects.get(id=id)
        notification_id = UserNotification.objects.get(
                            Q(user=self.request.user) &
                            Q(from_user=from_user) &
                            Q(notification_type=UserNotification.FRIEND_REQUEST)).id
        notification_html = render_to_string(
                                'user_pages/friend_request_notification.html',
                                {'from_user': from_user,
                                'notification_id':notification_id,
                                })
        context['notification_html'] = notification_html
        return self.render_json_response(context)


class GetFriendRequestAcceptNotificationAjaxView(View, JSONResponseMixin):
    template_name = 'user_pages/friend_request_accept_notification.html'

    def get(self, *args, **kwargs):
        context = dict()
        user = self.request.user
        id = self.request.GET.get('from_user')
        from_user = CustomUser.objects.get(id=id)
        notification_id = UserNotification.objects.get(
                            Q(user=self.request.user) &
                            Q(from_user=from_user) &
                            Q(notification_type=UserNotification.FRIEND_REQUEST_ACCEPT)).id
        notification_html = render_to_string(
                                'user_pages/friend_request_accept_notification.html',
                                {'from_user': from_user,
                                'notification_id':notification_id,
                                })
        context['notification_html'] = notification_html
        return self.render_json_response(context)


class GetProfileRatingNotificationAjaxView(View, JSONResponseMixin):
    template_name = 'user_pages/get-profile-rating-notification.html'

    def get(self, *args, **kwargs):
        context = dict()
        user = self.request.user
        id = self.request.GET.get('from_user')
        message = self.request.GET.get('message')
        from_user = CustomUser.objects.get(id=id)
        notification_id = UserNotification.objects.filter(
                            Q(user=self.request.user) &
                            Q(from_user=from_user) &
                            Q(notification_type=UserNotification.USER_RATING)).order_by('-created_time').first().id
        notification_html = render_to_string(
                                'user_pages/get-profile-rating-notification.html',
                                {'from_user': from_user,
                                'message':message,
                                'notification_id':notification_id,
                                })
        context['notification_html'] = notification_html
        return self.render_json_response(context)


class GetScreeningProjectInviteNotificationAjaxView(View, JSONResponseMixin):
    template_name = 'user_pages/get-screening-project-invite.html'

    def get(self, *args, **kwargs):
        context = dict()
        user = self.request.user
        id = self.request.GET.get('from_user')
        message = self.request.GET.get('message')
        from_user = CustomUser.objects.get(id=id)
        notification_id = UserNotification.objects.filter(
                            Q(user=self.request.user) &
                            Q(from_user=from_user) &
                            Q(notification_type=UserNotification.INVITE)).order_by('-created_time').first().id
        notification_html = render_to_string(
                                'user_pages/get-screening-project-invite.html',
                                {'from_user': from_user,
                                'message':message,
                                'notification_id':notification_id,
                                })
        context['notification_html'] = notification_html
        return self.render_json_response(context)


class GetAllNotificationAjaxView(View, JSONResponseMixin):
    template_name = 'user_pages/all_notification.html'

    def get(self, *args, **kwargs):
        context = dict()
        user = self.request.user
        notifications = UserNotification.objects.filter(
                        user=self.request.user).order_by('-created_time')
        all_notification_html = render_to_string(
                                'user_pages/all_notification.html',
                                {'notifications': notifications}
                                )
        context['all_notification_html'] = all_notification_html
        return self.render_json_response(context)


class AddUserInterestAjaxView(View, JSONResponseMixin):
    template_name = 'user_pages/add-my-interest-form.html'

    def get(self, *args, **kwargs):
        context = dict()
        user = self.request.user
        count = self.request.GET.get('count')
        form = self.request.GET.get('form')
        if form:
             add_my_interests_form_html = render_to_string(
                                'user_pages/add-my-interest-form2.html',
                                {'my_interest_form': UserInterestForm,
                                 'count': count}
                                )
        else:
            add_my_interests_form_html = render_to_string(
                                    'user_pages/add-my-interest-form.html',
                                    {'my_interest_form': UserInterestForm,
                                    'count': count}
                                    )
        context['add_my_interests_form_html'] = add_my_interests_form_html
        return self.render_json_response(context)


class ChangeNotificationStatusAPI(APIView):
    serializer_class = ChangeNotificationStatusSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            print(data_dict)
            id = data_dict['id']
            obj = UserNotification.objects.get(pk=id)
            obj.status_type = data_dict['status_type']
            obj.save()
            response = {'message': "Status changed",
                        'status': status.HTTP_200_OK}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class CompanyClientAPI(APIView):
    serializer_class = CompanyClientSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        clients = CompanyClient.objects.filter(company=self.request.user)
        response = {}
        for client in clients:
            response[client.id] = self.serializer_class(client).data
        return Response(response)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        company = request.user
        if serializer.is_valid():
            data_dict = serializer.data
            client = CompanyClient()
            client.company = company
            if 'position' in data_dict and data_dict['position'] != 'new_job':
                position = JobType.objects.get(id=data_dict['position'])
                client.position = position
            if 'name' in data_dict:
                client.name = data_dict['name']
            if 'new_position' in data_dict:
                pos = data_dict['new_position']
                client.new_position = pos.capitalize()
            if 'email' in data_dict:
                client.email = data_dict['email']
                try:
                    user = CustomUser.objects.get(email=data_dict['email'])
                    client.user = user
                    client.name = user.get_full_name()
                except CustomUser.DoesNotExist:
                    pass
            client.save()
            response = {'message': "Client Added",
                        'id': client.id,
                        'status': status.HTTP_200_OK}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class SendFriendRequestAPI(APIView):
    serializer_class = FriendRequestSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            try:
                requested_by = self.request.user
                user = CustomUser.objects.get(id=data_dict['user'])
                try:
                    request_obj = FriendRequest.objects.get(
                                    Q(user=user) &
                                    Q(requested_by=requested_by)
                                    )
                    response = {'errors': "Request Already Send", 'status':
                                status.HTTP_400_BAD_REQUEST}
                except FriendRequest.DoesNotExist:
                    request_obj = FriendRequest()
                    request_obj.user = user
                    request_obj.requested_by = requested_by
                    request_obj.status = FriendRequest.REQUEST_SEND
                    request_obj.save()

                    # update notification table
                    notification = UserNotification()
                    notification.user = user
                    notification.notification_type = UserNotification.FRIEND_REQUEST
                    notification.from_user = requested_by
                    notification.save()

                    # send email
                    try:
                        user_settings = CustomUserSettings.objects.get(user=user)
                        if user_settings.friend_request == True:
                            subject = 'Friend Request'
                            message = ''
                            msg_html = loader.render_to_string('user_pages/friend_request_email.html',
                                        {'requested_by': requested_by, 'first_name':user.first_name })
                            email_from = settings.EMAIL_HOST_USER
                            recipient_list = [user.email, ]
                            send_mail( subject, message, email_from, recipient_list, html_message=msg_html)
                    except CustomUserSettings.DoesNotExist:
                        pass

                    # send notification
                    room_name = "user_"+str(user.id)
                    notification_msg = {
                            'type': 'send_friend_request_notification',
                            'message': str(user.get_full_name()),
                            'friend_request_from': str(requested_by.id),
                            "event": "FRIEND_REQUEST"
                        }
                    notify(room_name, notification_msg)

                    response = {'message': "Friend Request Send",
                                'status': status.HTTP_200_OK}
            except CustomUser.DoesNotExist:
                response = {'errors': "Invalid Id", 'status':
                            status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class AcceptFriendRequestAPI(APIView):
    serializer_class = AcceptFriendRequestSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            try:
                requested_by = CustomUser.objects.get(id=data_dict['requested_by'])
                user = self.request.user
                request_obj = FriendRequest.objects.get(
                                Q(user=user) &
                                Q(requested_by=requested_by) &
                                Q(status=FriendRequest.REQUEST_SEND))
                request_obj.delete()

                # update notification table
                notification = UserNotification()
                notification.user = requested_by
                notification.notification_type = UserNotification.FRIEND_REQUEST_ACCEPT
                notification.from_user = user
                notification.save()
                # update friends list of both users
                try:
                    friend_obj = Friend.objects.get(user=user)
                    friend_obj.friends.add(requested_by)
                except Friend.DoesNotExist:
                    friend_obj = Friend()
                    friend_obj.user = user
                    friend_obj.save()
                    friend_obj.friends.add(requested_by)
                try:
                    friend_obj = Friend.objects.get(user=requested_by)
                    friend_obj.friends.add(user)
                except Friend.DoesNotExist:
                    friend_obj = Friend()
                    friend_obj.user = requested_by
                    friend_obj.save()
                    friend_obj.friends.add(user)
                # send notification
                room_name = "user_"+str(requested_by.id)
                notification_msg = {
                        'type': 'send_friend_request_accept_notification',
                        'message': str(user.get_full_name()),
                        'from': str(user.id),
                        "event": "FRIEND_REQUEST_ACCEPT"
                    }
                notify(room_name, notification_msg)
                try:
                    notification = UserNotification.objects.get(
                        Q(user=user) &
                        Q(from_user=requested_by) &
                        Q(notification_type=UserNotification.FRIEND_REQUEST)
                        )
                    notification.delete()
                except UserNotification.DoesNotExist:
                    pass
                response = {'message': "Friend Request Accepted",
                            'name': requested_by.get_full_name(),
                            'status': status.HTTP_200_OK}
            except CustomUser.DoesNotExist:
                response = {'errors': "Invalid Id.", 'status':
                            status.HTTP_400_BAD_REQUEST}
            except FriendRequest.DoesNotExist:
                response = {'errors': "Invalid Id. Friend Request object not found", 'status':
                            status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class CancelFriendRequestAPI(APIView):
    serializer_class = FriendRequestSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            try:
                requested_by = self.request.user
                user = CustomUser.objects.get(id=data_dict['user'])
                request_obj = FriendRequest.objects.get(
                                Q(user=user) &
                                Q(requested_by=requested_by) &
                                Q(status=FriendRequest.REQUEST_SEND)
                                )
                request_obj.delete()
                try:
                    notification = UserNotification.objects.get(
                        Q(user=user) &
                        Q(from_user=requested_by) &
                        Q(notification_type=UserNotification.FRIEND_REQUEST)
                        )
                    notification.delete()
                except UserNotification.DoesNotExist:
                    pass
                response = {'message': "Friend Request Deleted",
                            'status': status.HTTP_200_OK}
            except CustomUser.DoesNotExist:
                response = {'errors': "Invalid Id.", 'status':
                            status.HTTP_400_BAD_REQUEST}
            except FriendRequest.DoesNotExist:
                response = {'errors': "Invalid Id. Friend Request object not found", 'status':
                            status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class DeleteFriendRequestAPI(APIView):
    serializer_class = AcceptFriendRequestSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            try:
                requested_by = CustomUser.objects.get(id=data_dict['requested_by'])
                user = self.request.user
                request_obj = FriendRequest.objects.get(
                                Q(user=user) &
                                Q(requested_by=requested_by) &
                                Q(status=FriendRequest.REQUEST_SEND)
                                )
                request_obj.delete()
                try:
                    notification = UserNotification.objects.get(
                        Q(user=user) &
                        Q(from_user=requested_by) &
                        Q(notification_type=UserNotification.FRIEND_REQUEST)
                        )
                    notification.delete()
                except UserNotification.DoesNotExist:
                    pass
                response = {'message': "Friend Request Deleted",
                            'status': status.HTTP_200_OK}
            except CustomUser.DoesNotExist:
                response = {'errors': "Invalid Id.", 'status':
                            status.HTTP_400_BAD_REQUEST}
            except FriendRequest.DoesNotExist:
                response = {'errors': "Invalid Id. Friend Request object not found", 'status':
                            status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class ListFriendRequestAPI(APIView):
    serializer_class = FriendRequestSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        friend_request_dict = {}
        user = request.user
        friend_requests = FriendRequest.objects.filter(
                          Q(user=user) &
                          Q(status=FriendRequest.REQUEST_SEND))
        for obj in friend_requests:
            friend_request_dict[obj.id] = self.serializer_class(obj).data
        response['friend_requests'] = friend_request_dict
        return Response(response)


class ListAllFriendsAPI(APIView):
    serializer_class = FriendRequestSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        friends_dict = {}
        user = request.user
        try:
            friend_obj = Friend.objects.get(user=user)
            for ind, obj in enumerate(friend_obj.friends.all()):
                        individual_friend_data = {'email': obj.email, 'user': obj.first_name +' '+ obj.last_name}
                        # individual_friend_data = {obj.email, obj.first_name +' '+ obj.last_name}
                        friends_dict[ind] = individual_friend_data
        except Friend.DoesNotExist:
            response['friends'] = {}
        response['friends'] = friends_dict
        return Response(response)


class UnFriendUserAPI(APIView):
    serializer_class = FriendRequestSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            try:
                requested_by = self.request.user
                user = CustomUser.objects.get(id=data_dict['user'])

                try:
                    friend_obj = Friend.objects.get(user=user)
                    friend_obj.friends.remove(requested_by)
                except Friend.DoesNotExist:
                    pass
                try:
                    friend_obj = Friend.objects.get(user=requested_by)
                    friend_obj.friends.remove(user)
                except Friend.DoesNotExist:
                    pass

                friend_groups = GroupUsers.objects.filter(user=user)
                for group in friend_groups:
                    if requested_by in group.friends.all():
                        group.friends.remove(requested_by)
                friend_groups = GroupUsers.objects.filter(user=requested_by)
                for group in friend_groups:
                    if user in group.friends.all():
                        group.friends.remove(user)

                # update notification table
                try:
                    notification = UserNotification.objects.get(
                        Q(user=user) &
                        Q(from_user=requested_by) &
                        Q(notification_type=UserNotification.FRIEND_REQUEST_ACCEPT)
                        )
                    notification.delete()
                except UserNotification.DoesNotExist:
                    pass
                try:
                    notification = UserNotification.objects.get(
                        Q(user=requested_by) &
                        Q(from_user=user) &
                        Q(notification_type=UserNotification.FRIEND_REQUEST_ACCEPT)
                        )
                    notification.delete()
                except UserNotification.DoesNotExist:
                    pass
                response = {'message': "UnFriend User",
                            'status': status.HTTP_200_OK}
            except CustomUser.DoesNotExist:
                response = {'errors': "Invalid Id.", 'status':
                            status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class AddGroupAPI(APIView):
    serializer_class = AddGroupSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            new_group = FriendGroup()
            new_group.title = data_dict['title']
            new_group.user = self.request.user
            new_group.save()
            response = {'message': "Group Added",
                        'status': status.HTTP_200_OK}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class AddFriendToGroupAPI(APIView):
    serializer_class = AddFriendToGroupSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        response = {}
        user = self.request.user
        friend = self.request.POST.get('friend')
        groups = self.request.POST.getlist('groups')
        # print("groups--", groups)
        if friend!=None and groups!=None :
            # remove previous groups
            friend_obj = CustomUser.objects.get(id=friend)
            friend_groups = friend_obj.group_members.all()
            for obj in friend_groups:
                obj.friends.remove(friend)

            # add new groups
            for group in groups:
                print("group--", group)
                try:
                    obj = GroupUsers.objects.get(
                            Q(user=user) &
                            Q(group=group)
                            )
                    obj.friends.add(friend)
                except GroupUsers.DoesNotExist:
                    obj = GroupUsers()
                    obj.group = FriendGroup.objects.get(id=group)
                    obj.user = user
                    obj.save()
                    obj.friends.add(friend)
            response = {'message': "User added to group",
                        'status': status.HTTP_200_OK}
        return Response(response)


class RemoveFriendGroupAPI(APIView):
    serializer_class =  RemoveFriendGroupSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            try:
                group = FriendGroup.objects.get(pk=data_dict['group'])
                group.delete()
                response = {'message': "Group Removed",
                'status': status.HTTP_200_OK}
            except FriendGroup.DoesNotExist:
                response = {'errors': 'Invalid Id', 'status':
                        status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class UpdateFriendGroupAjaxView(View, JSONResponseMixin):
    template_name = 'user_pages/add-my-interest-form.html'

    def get(self, *args, **kwargs):
        context = dict()
        user = self.request.user
        groups = FriendGroup.objects.filter(user=user)
        groups_html = render_to_string(
                                'user_pages/friend-group.html',
                                {'groups': groups}
                                )
        context['groups_html'] = groups_html
        return self.render_json_response(context)


class FilterFriendByGroupAjaxView(View, JSONResponseMixin):
    template_name = 'user_pages/filter-friends.html'

    def get(self, *args, **kwargs):
        context = dict()
        friends = []
        user = self.request.user
        group_id = self.request.GET.get('group')
        groups = FriendGroup.objects.filter(user=user)
        if group_id == "all":
            try:
                friend_obj = Friend.objects.get(user=user)
                friends = friend_obj.friends.all()
            except Friend.DoesNotExist:
                pass
        else:
            try:
                friend_obj = GroupUsers.objects.get(
                            Q(group=group_id) &
                            Q(user=user)
                            )
                friends = friend_obj.friends.all()
            except GroupUsers.DoesNotExist:
                friends = []
        friends_html = render_to_string(
                                'user_pages/filter-friends.html',
                                {'all_friends': friends,
                                'groups': groups}
                                )
        context['friends_html'] = friends_html
        return self.render_json_response(context)


class FeedbackAPIView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddBetaTesterCode(APIView):
    """
    API endpoint to add a beta tester code
    """
    permission_classes = (IsSuperUser,)

    def post(self, request, *args, **kwargs):
        initial_data = request.data
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
        if token_user_response.status_code == 200:
            access_token = json.loads(token_user_response.content)['access_token']
        else:
            return Response(
                {"status": "error in fetching paypal access token"},
                status=status.HTTP_404_NOT_FOUND)

        access_token_strting = 'Bearer ' + access_token

        #get the current plan details
        paypal_get_plan_details_api = "https://api-m.sandbox.paypal.com/v1/billing/plans/"

        #1
        indie_monthly_plan_details_api = paypal_get_plan_details_api + settings.INDIE_PAYMENT_MONTHLY
        indie_monthly_plan_details_api_response = requests.get(
                            indie_monthly_plan_details_api,
                            headers={'Content-Type': 'application/json',
                                     'Authorization': access_token_strting})
        if indie_monthly_plan_details_api_response.status_code == 200:
            indie_monthly_plan_value = find_values('value', indie_monthly_plan_details_api_response.text)[0]
        else:
            return Response(
                {"status": "error in fetching paypal plan"},
                status=status.HTTP_404_NOT_FOUND)
        #2
        indie_yearly_plan_details_api = paypal_get_plan_details_api + settings.INDIE_PAYMENT_YEARLY
        indie_yearly_plan_details_api_response = requests.get(
                            indie_yearly_plan_details_api,
                            headers={'Content-Type': 'application/json',
                                     'Authorization': access_token_strting})
        if indie_yearly_plan_details_api_response.status_code == 200:
            indie_yearly_plan_value = find_values('value', indie_yearly_plan_details_api_response.text)[0]
        else:
            return Response(
                {"status": "error in fetching paypal plan"},
                status=status.HTTP_404_NOT_FOUND)
        #3
        pro_monthly_plan_details_api = paypal_get_plan_details_api + settings.PRO_PAYMENT_MONTHLY
        pro_monthly_plan_details_api_response = requests.get(
                            pro_monthly_plan_details_api,
                            headers={'Content-Type': 'application/json',
                                     'Authorization': access_token_strting})
        if pro_monthly_plan_details_api_response.status_code == 200:
            pro_monthly_plan_value = find_values('value', pro_monthly_plan_details_api_response.text)[0]
        else:
            return Response(
                {"status": "error in fetching paypal plan"},
                status=status.HTTP_404_NOT_FOUND)
        #4
        pro_yearly_plan_details_api = paypal_get_plan_details_api + settings.PRO_PAYMENT_YEARLY
        pro_yearly_plan_details_api_response = requests.get(
                            pro_yearly_plan_details_api,
                            headers={'Content-Type': 'application/json',
                                     'Authorization': access_token_strting})
        if pro_yearly_plan_details_api_response.status_code == 200:
            pro_yearly_plan_value = find_values('value', pro_yearly_plan_details_api_response.text)[0]
        else:
            return Response(
                {"status": "error in fetching paypal plan"},
                status=status.HTTP_404_NOT_FOUND)
        #5
        company_monthly_plan_details_api = paypal_get_plan_details_api + settings.COMPANY_PAYMENT_MONTHLY
        company_monthly_plan_details_api_response = requests.get(
                            company_monthly_plan_details_api,
                            headers={'Content-Type': 'application/json',
                                     'Authorization': access_token_strting})
        if company_monthly_plan_details_api_response.status_code == 200:
            company_monthly_plan_value = find_values('value', company_monthly_plan_details_api_response.text)[0]
        else:
            return Response(
                {"status": "error in fetching paypal plan"},
                status=status.HTTP_404_NOT_FOUND)
        #6
        company_yearly_plan_details_api = paypal_get_plan_details_api + settings.COMPANY_PAYMENT_YEARLY
        company_yearly_plan_details_api_response = requests.get(
                            company_yearly_plan_details_api,
                            headers={'Content-Type': 'application/json',
                                     'Authorization': access_token_strting})
        if company_yearly_plan_details_api_response.status_code == 200:
            company_yearly_plan_value = find_values('value', company_yearly_plan_details_api_response.text)[0]
        else:
            return Response(
                {"status": "error in fetching paypal plan"},
                status=status.HTTP_404_NOT_FOUND)

        # create plans based on the input
        paypal_create_plan_api = "https://api-m.sandbox.paypal.com/v1/billing/plans"

        plan_types = ['Indie Payment Monthly','Indie Payment Yearly',
                      'Pro Payment Monthly','Pro Payment Yearly',
                      'Company Payment Monthly','Company Payment Yearly']
        plan_ids = {'indie_monthly_plan_id': '',
                    'indie_yearly_plan_id': '',
                    'pro_monthly_plan_id': '',
                    'pro_yearly_plan_id': '',
                    'company_monthly_plan_id': '',
                    'company_yearly_plan_id': ''}
        for plan_type in plan_types:
            plan_name = 'Beta User Plan' + ' - ' + plan_type + ' - ' + request.data['code']
            if plan_type.find('Monthly'):
                plan_interval_unit = 'MONTH'
            else:
                plan_interval_unit = 'YEAR'

            if plan_type == 'Indie Payment Monthly':
                plan_interval_count = indie_monthly_plan_value
            elif plan_type == 'Indie Payment Yearly':
                plan_interval_count = indie_yearly_plan_value
            elif plan_type == 'Pro Payment Monthly':
                plan_interval_count = pro_monthly_plan_value
            elif plan_type == 'Pro Payment Yearly':
                plan_interval_count = pro_yearly_plan_value
            elif plan_type == 'Company Payment Monthly':
                plan_interval_count = company_monthly_plan_value
            elif plan_type == 'Company Payment Yearly':
                plan_interval_count = company_yearly_plan_value
            else:
                pass

            create_plan_json ={
                "name": plan_name,
                "description": plan_name,
                "product_id": settings.PRODUCT_ID,
                "billing_cycles": [
                    {
                        "frequency": {
                            "interval_unit": "DAY",
                            "interval_count": request.data['days']
                        },
                        "tenure_type": "TRIAL",
                        "sequence": 1,
                        "total_cycles": 1,
                        "pricing_scheme": {
                            "fixed_price": {
                                "value": "0",
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
        serializer = AddBetaTesterCodeSerializer(data=initial_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListBetaTesterCode(APIView):
    """
    API endpoint to list beta tester codes
    """
    permission_classes = (IsSuperUser,)

    def get(self, request, *args, **kwargs):
        filter_objs = BetaTesterCodes.objects.all()
        serialized_results = AddBetaTesterCodeSerializer(filter_objs, many=True)
        if serialized_results.is_valid:
            return Response(serialized_results.data, status=status.HTTP_200_OK)
        else:
            return Response(serialized_results.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteBetaTesterCode(APIView):
    """
    API endpoint to delete a beta tester code
    """
    permission_classes = (IsSuperUser,)

    def delete(self, request, *args, **kwargs):
        try:
            delete_obj_id = kwargs['id']
            delete_obj = BetaTesterCodes.objects.get(id=delete_obj_id)

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
            if token_user_response.status_code == 200:
                access_token = json.loads(token_user_response.content)['access_token']
            else:
                return Response(
                    {"status": "error in fetching paypal access token"},
                    status=status.HTTP_404_NOT_FOUND)

            access_token_strting = 'Bearer ' + access_token

            plan_ids = []
            deactivate_plan_base_url = 'https://api-m.sandbox.paypal.com/v1/billing/plans/'

            deactivate_indie_monthly_plan_url = deactivate_plan_base_url + delete_obj.indie_monthly_plan_id + '/deactivate'
            deactivate_indie_monthly_plan_url_response = requests.post(
                    deactivate_indie_monthly_plan_url,
                    headers={'Content-Type': 'application/json',
                             'Authorization': access_token_strting})
            if deactivate_indie_monthly_plan_url_response.status_code == 204:
                plan_id = delete_obj.indie_monthly_plan_id
                plan_ids.append(plan_id)

            deactivate_indie_yearly_plan_url = deactivate_plan_base_url + delete_obj.indie_yearly_plan_id + '/deactivate'
            deactivate_indie_yearly_plan_url_response = requests.post(
                    deactivate_indie_yearly_plan_url,
                    headers={'Content-Type': 'application/json',
                             'Authorization': access_token_strting})
            if deactivate_indie_yearly_plan_url_response.status_code == 204:
                plan_id = delete_obj.indie_yearly_plan_id
                plan_ids.append(plan_id)

            deactivate_pro_monthly_plan_url = deactivate_plan_base_url + delete_obj.pro_monthly_plan_id + '/deactivate'
            deactivate_pro_monthly_plan_url_response = requests.post(
                    deactivate_pro_monthly_plan_url,
                    headers={'Content-Type': 'application/json',
                             'Authorization': access_token_strting})
            if deactivate_pro_monthly_plan_url_response.status_code == 204:
                plan_id = delete_obj.pro_monthly_plan_id
                plan_ids.append(plan_id)

            deactivate_pro_yearly_plan_url = deactivate_plan_base_url + delete_obj.pro_yearly_plan_id + '/deactivate'
            deactivate_pro_yearly_plan_url_response = requests.post(
                    deactivate_pro_yearly_plan_url,
                    headers={'Content-Type': 'application/json',
                             'Authorization': access_token_strting})
            if deactivate_pro_yearly_plan_url_response.status_code == 204:
                plan_id = delete_obj.pro_yearly_plan_id
                plan_ids.append(plan_id)

            deactivate_company_monthly_plan_url = deactivate_plan_base_url + delete_obj.company_monthly_plan_id + '/deactivate'
            deactivate_company_monthly_plan_url_response = requests.post(
                    deactivate_company_monthly_plan_url,
                    headers={'Content-Type': 'application/json',
                             'Authorization': access_token_strting})
            if deactivate_company_monthly_plan_url_response.status_code == 204:
                plan_id = delete_obj.company_monthly_plan_id
                plan_ids.append(plan_id)

            deactivate_company_yearly_plan_url = deactivate_plan_base_url + delete_obj.company_yearly_plan_id + '/deactivate'
            deactivate_company_yearly_plan_url_response = requests.post(
                    deactivate_company_yearly_plan_url,
                    headers={'Content-Type': 'application/json',
                             'Authorization': access_token_strting})
            if deactivate_company_yearly_plan_url_response.status_code == 204:
                plan_id = delete_obj.company_yearly_plan_id
                plan_ids.append(plan_id)

            if len(plan_ids) >= 1:
                delete_obj.delete()
                final_response = 'successfully deleted the plans associated with the beta_user_code' + delete_obj.code
                return Response(
                    {'status': final_response}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'status': 'error in deleteing the beta-user-plan'}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response(
                {'status': 'code with this id does not exist'}, status=status.HTTP_400_BAD_REQUEST)


class EditBetaTesterCode(APIView):
    """
    API endpoint to edit a beta tester code
    """
    permission_classes = (IsSuperUser,)

    def put(self, request, *args, **kwargs):
        try:
            data = request.data
            unique_id = request.data['id']
            testercode_instance = BetaTesterCodes.objects.get(id=unique_id)
            serializer = AddBetaTesterCodeSerializer(testercode_instance,
                                             data=request.data, partial=True)
            if serializer.is_valid():
                serializer.update(BetaTesterCodes.objects.get(id=unique_id),
                                  request.data)
                return Response(
                    {"status": "success",
                     "message": "beta tester code updated successfully"})
            else:
                return Response(serializer.errors)
        except ObjectDoesNotExist:
            return Response(
                {"status": "beta tester code record not found"},
                status=status.HTTP_404_NOT_FOUND)


class CheckBetaTesterCode(APIView):
    """
    API endpoint to check a beta tester code
    """

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            unique_id = request.data['code']
            testercode_instance = BetaTesterCodes.objects.get(code=unique_id)
            if testercode_instance:
                return Response(
                    {"status": "success",
                     "message": "beta tester code exists",
                     "code": unique_id})
        except ObjectDoesNotExist:
            return Response(
                {"status": "beta tester code does not exist"},
                status=status.HTTP_404_NOT_FOUND)


class FeedbackWebView(View):
    # renderer_classes = [TemplateHTMLRenderer]
    # template_name = 'user_pages/feedback.html'
    """
    Web View to load the feedback page
    """

    def get(self, request, *args, **kwargs):
        template = loader.get_template("user_pages/feedback.html")
        return HttpResponse(template.render())

    def post(self, request, *args, **kwargs):
        serializer = FeedbackSerializer(data=json.dumps(request.POST))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 3

# Project CRUD
class ProjectAPIView(ListAPIView, SegregatorMixin):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    # permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['creator', 'title', 'format', 'genre',
                        'rating', 'video_url', 'video_type',
                        'last_date', 'location', 'visibility',
                        'visibility_password', 'cast_attachment',
                        'cast_pay_rate', 'cast_samr', 'timestamp']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        context = self.project_segregator(queryset)
        return Response(context)


class ProjectDateFilterAPI(APIView, SegregatorMixin):

    def post(self, request):
        received_data = json.loads(request.body)
        # day = received_data['day']
        if 'year' in received_data and 'month' in received_data:
            month = received_data['month']
            year = received_data['year']
            project = Project.objects.filter(timestamp__range=[year+"-"+month+"-01",
                                                               year+"-"+month+"-30"])
            context = self.project_segregator(project)
            return Response(context)

        elif 'year' in received_data:
            year = received_data['year']
            project = Project.objects.filter(timestamp__range=[year+"-01-01",
                                                               year+"-12-30"])
            context = self.project_segregator(project)
            return Response(context)

class ProjectSearchView(ListAPIView, SegregatorMixin):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = [SearchFilter]
    search_fields = ["title", "format", "genre",
                     "rating", "timestamp"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        context = self.project_segregator(queryset)
        return Response(context)


class ProjectCreateAPIView(CreateAPIView):
  permission_classes = (IsAuthenticated,)
  queryset = Project.objects.all()
  serializer_class = ProjectSerializer


class ProjectUpdateAPIView(UpdateAPIView):
    queryset = Project.objects.all()
    permission_classes = (IsAuthenticated,)
    lookup_field = 'id'
    serializer_class = ProjectSerializer

class ProjectDeleteAPIView(DestroyAPIView):
    queryset = Project.objects.all()
    permission_classes = (IsAuthenticated,)
    lookup_field = 'id'
    serializer_class = ProjectSerializer

# Team CRUD
class TeamAPIView(ListAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["title", "format", "genre",
                        "rating", "timestamp"]

class TeamCreateAPIView(CreateAPIView):
  queryset = Team.objects.all()
  serializer_class = TeamSerializer


class TeamUpdateAPIView(UpdateAPIView):
    queryset = Team.objects.all()
    permission_classes = (IsAuthenticated,)
    lookup_field = 'id'
    serializer_class = TeamSerializer

class TeamDeleteAPIView(DestroyAPIView):
    queryset = Team.objects.all()
    permission_classes = (IsAuthenticated,)
    lookup_field = 'id'
    serializer_class = TeamSerializer


class ProjectSearchView(ListAPIView, SegregatorMixin):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = [SearchFilter]
    search_fields = ["title", "format", "genre",
                     "rating", "timestamp"]

#     def list(self, request, *args, **kwargs):
#         queryset = self.filter_queryset(self.get_queryset())
#         context = self.project_segregator(queryset)
#         return Response(context)


#Search API for Pages

#API for Searching things in a page

class PageSearchView(ListAPIView):
    template_name = 'search_results.html'
    serializer_class = ProjectSerializer
    def get_queryset(self):

        query = self.request.GET.get('q')
        format_map = {v: k for k, v  in enumerate(Project.FORMAT_CHOICES)}
        genre_map = {i: j for j, i  in enumerate(Project.GENRE_CHOICES)}
        # get the corresponding key,value  from choice filed of model

        for val in format_map.keys():
            if(query==val[1]):
                query=val[0]

        for val in genre_map.keys():
            if(query==val[1]):
                query=val[0]
        object_list = Project.objects.filter(
            Q(title__icontains=query) | Q(format__icontains=query) | Q(genre__icontains=query) 
            | Q(rating__icontains=query) | Q(location__country__icontains=query)
        )
        return object_list


# Api to add rating to project video
class VideoRatingView(APIView):
    serializer_class = VideoRatingSerializer
    permission_classes = (IsAuthenticated,)

    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        allowed_members = ['IND','PRO','COM']
        if serializer.is_valid():
            user = self.request.user
            project = serializer.validated_data.get('project')
            rating = serializer.validated_data.get('rating')
            reason = serializer.validated_data.get('reason')
            rating_obj = VideoRating()

            if user.membership in allowed_members:
                # project = get_object_or_404(Project, pk=project_id)
                rating_obj.project = project
                rating_obj.rating = rating
                rating_obj.reason = reason
                rating_obj.rated_by = user
                rating_obj.save()
                self.refresh_rating(project.id)
                response = {'message': "Rating success",
                            'status': status.HTTP_201_CREATED}
            else:
                response = {'errors': "Unautharized access", 'status':
                            status.HTTP_401_UNAUTHORIZED}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)

    """
    Ratings are combined to a single rating
    and written to project everytime when user make a rating.
    """

    def refresh_rating(self, project_id):
        ratings = VideoRating.objects.filter(project=project_id)
        combined_rating = 0
        for item in ratings:
            combined_rating += item.rating
            print(combined_rating)
        combined_rating = combined_rating / len(ratings)
        try:
            video_rating_combined = VideoRatingCombined.objects.get(project=project_id)
            video_rating_combined.rating = combined_rating
            video_rating_combined.save()
        except VideoRatingCombined.DoesNotExist:
            video_rating_combined = VideoRatingCombined()
            project = get_object_or_404(Project, pk=project_id)
            video_rating_combined.project = project
            video_rating_combined.rating = combined_rating
            video_rating_combined.save()

# API to find rating of a video
class FindVideoRatingAPI(RetrieveAPIView):
    serializer_class = VideoSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Video.objects.all()
    lookup_field = 'id'

# Api to list Video based on rating
class VideoListAPI(ListAPIView):
    serializer_class = VideoSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Video.objects.all().order_by('-rating','-created')


class ProjectView(LoginRequiredMixin, TemplateView):
    template_name = 'user_pages/projects-page.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context['user'] = user
        context["scenes"] = Project.objects.filter(format="SCH").order_by('-id')
        context["toprated_scenes"] = Project.objects.filter(format="SCH").order_by('-rating')
        context["filims"] = Project.objects.filter(format="SHO").order_by('-id')
        context["toprated_filims"] = Project.objects.filter(format="SHO").order_by('-rating')
       
        return context



class GetAllUsersAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        super_users = CustomUser.objects.filter(is_superuser=True).values_list('id')
        all_users = CustomUser.objects.exclude(id__in=super_users)
        all_users = all_users.exclude(id=self.request.user.id)
        serializer_list = []
        name_list = []
        name_dict = {}
        for user in all_users:
            serializer_list.append(user.get_full_name())
            name_list.append(user.get_full_name())
            name_dict[user.get_full_name()]="<a href='"+user.get_profile_url()+"' id='"+str(user.id)+"' class='mention_user'>"+user.get_full_name()+"</a> "
        return Response({"serializer_list": serializer_list, "name_dict": name_dict, "name_list": name_list})

class ScreeningProjectDeatilView(LoginRequiredMixin, TemplateView):
    template_name = 'user_pages/screening_video_page.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('id')
        project_obj = Project.objects.get(id=project_id)
        context["project"] = project_obj
        return context


class UserHomeProjectInvite(APIView):

    def post(self, request, *args, **kwargs):
        emails = request.data['emails']
        content = request.data['project_url']

        subject, from_email, to = 'Subject', 'from@xxx.com', 'to@xxx.com'

        html_content = render_to_string('mail_template.html', {'varname':'value'})
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


class CreateProjectView(LoginRequiredMixin, TemplateView):
    template_name = 'user_pages/new-project.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ProjectCreationForm
        context['writerform'] = WriterForm
        return context

    def post(self, request):
        try:
            projectform = ProjectCreationForm(request.POST or None, request.FILES)
            
            writerform = WriterForm(request.POST or None)
            print("valid ahno project:", projectform.is_valid())
            print('form error project', projectform.errors)
            print("valid ahno writer:", writerform.is_valid())
            print('form error writer', writerform.errors)
            if projectform.is_valid() and writerform.is_valid():
                writer = writerform.save()
                project = projectform.save()
                writer.project = project
                writer.save()
                messages.success(request, "New project added.")
                return HttpResponseRedirect(
                                    reverse('hobo_user:projects'))
            messages.error(request, "Form not valid")
            return HttpResponseRedirect(
                                    reverse('hobo_user:projects'))
        except:
            messages.error(request, "Can't read data")
            return HttpResponseRedirect(
                                    reverse('hobo_user:projects'))


class ScreeningProjectDeatilInviteView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            # send notification
            logged_in_user = request.user
            to_user = CustomUser.objects.get(email=request.data['to_user_email'])
            project_url = request.data['project_url']
            project_id = project_url.rsplit('/', 2)[1]
            project_obj = Project.objects.get(id=project_id)

            #update notification table
            notification = UserNotification()
            notification.user = to_user
            notification.notification_type = UserNotification.INVITE
            notification.from_user = self.request.user
            notification.message = self.request.user.get_full_name()+" invited you to check his project titled "+str(project_obj.title)+""
            notification.invite_url = project_url
            notification.save()
            # send notification
            room_name = "user_"+str(logged_in_user.id)
            notification_msg = {
                    'type': 'send_profile_rating_notification',
                    'message': str(notification.message),
                    'from': str(request.user.id),
                    "event": "INVITE"
                }
            notify(room_name, notification_msg)
            # end notification section
            if notification_msg:
                return Response({"status": "invite success"}, status=status.HTTP_200_OK)
        except:
            return Response({"status": "invite failure"}, status=status.HTTP_400_BAD_REQUEST)


class GetBetaTesterCodeId(APIView):
    """
    API endpoint to get a beta tester code id
    """

    def post(self, request, *args, **kwargs):
        if request.data['code'] != None:
            try:
                data = request.data
                unique_id = request.data['code']
                testercode_instance = BetaTesterCodes.objects.get(code=unique_id)
                final_date = date.today() + timedelta(days=testercode_instance.days)
                if testercode_instance:
                    return Response(
                        {"status": "success",
                        "code_id": testercode_instance.id,
                        "code": testercode_instance.code,
                        "days": testercode_instance.days,
                        "final_day": final_date})
            except ObjectDoesNotExist:
                return Response(
                    {"status": "beta tester code does not exist"},
                    status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(
            {"status": "no content"},
            status=status.HTTP_204_NO_CONTENT)


class SentPaymentMail(APIView):

    def post(self, request):
        must_validate_email = getattr(settings,
                                        'AUTH_EMAIL_VERIFICATION', True)
        # key = request.POST['key']
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
            response = {'message': 'Invalid data'}
        return Response(response)
