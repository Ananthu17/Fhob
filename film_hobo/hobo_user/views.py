
import json
import requests

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render, redirect
from django.http.response import HttpResponse
from django.conf import settings

from authemail.models import SignupCode
from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_auth.registration.views import RegisterView
from rest_framework.authtoken.models import Token
from rest_auth.views import LoginView as AuthLoginView
from rest_auth.views import LogoutView as AuthLogoutView

from .forms import SignUpForm, LoginForm, SignUpIndieProForm, \
    SignUpFormCompany
from .models import CustomUser
from .serializers import CustomUserSerializer, RegisterSerializer, RegisterIndieProSerializer


class ExtendedLoginView(AuthLoginView):

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data,
                                              context={'request': request})
        self.serializer.is_valid(raise_exception=True)
        self.login()
        print("hello",request.user)
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
   

class CustomUserLogin(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'user_pages/login.html'

    def get(self, request):
        form = LoginForm()
        return render(request, 'user_pages/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user_response = requests.post(
                            'http://127.0.0.1:8000/hobo_user/authentication/',
                            data=json.dumps(request.POST),
                            headers={'Content-type': 'application/json'})
            
            print("hello",request.user)
            # print("user_response--- ",user_response. __dict__ )
            if user_response.status_code == 200:
                response_json = user_response.json()
                token = response_json['key']
                token = Token.objects.get(key=token)
                user = CustomUser.objects.get(id=token.user_id)
                request.user = user
                return render(request, 'user_pages/user_home.html',
                            {'user': user})
            else:
                return HttpResponse('Could not login')
        else:
            print("Invalid")
            print(form.errors)
        return render(request, 'user_pages/login.html', {'form': form})


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


class ExtendedRegisterIndieProView(RegisterView):
    serializer_class = RegisterIndieProSerializer

    def create(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        print("request.data....",request.data)
        serializer.is_valid()
        print("errors....",serializer.errors)
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


class CustomUserSignupIndieProView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'user_pages/signup_indie_pro.html'

    def get(self, request):
        form = SignUpIndieProForm()
        return render(request, 'user_pages/signup_indie_pro.html', {'form': form})

    def post(self, request):
        form = SignUpIndieProForm(request.POST)
        choice = request.GET.get('choice')
        must_validate_email = getattr(settings, "AUTH_EMAIL_VERIFICATION", True)
        if form.is_valid():
            customuser_username = request.POST['email']
            print(request.POST)
            if not request.POST._mutable:
                request.POST._mutable = True
            request.POST['username'] = customuser_username
            user_response = requests.post(
                            'http://127.0.0.1:8000/hobo_user/registration_indie_pro/',
                            data=json.dumps(request.POST),
                            headers={'Content-type': 'application/json'})
            if user_response.status_code == 201:
                new_user = CustomUser.objects.get(
                           email=request.POST['email'])
                
                # if must_validate_email:
                #     ipaddr = self.request.META.get('REMOTE_ADDR', '0.0.0.0')
                #     signup_code = SignupCode.objects.create_signup_code(new_user, ipaddr)
                #     signup_code.send_signup_email()

                return render(request, 'user_pages/user_email_verification.html',
                              {'user': new_user})
            else:
                return HttpResponse('Could not save data')
        return render(request, 'user_pages/signup_indie_pro.html', {'form': form})

    class Meta:
        model = get_user_model()


class CustomUserSignupCompany(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'user_pages/signup_company.html'

    def get(self, request):
        form = SignUpFormCompany()
        return render(request, 'user_pages/signup_company.html',
                      {'form': form})

