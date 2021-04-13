
import json
import requests

from authemail import wrapper
from authemail.models import SignupCode

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render, redirect
from django.http.response import HttpResponse
from django.conf import settings

from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_auth.registration.views import RegisterView
from rest_framework.authtoken.models import Token
from rest_auth.views import LoginView as AuthLoginView
from rest_auth.views import LogoutView as AuthLogoutView

from .forms import SignUpForm, LoginForm
from .models import CustomUser
from .serializers import CustomUserSerializer


# class ExtendedLoginView(AuthLoginView):
#     template_name = 'user_pages/login.html'

#     def get(self, request):
#         form = LoginForm()
#         return render(request, 'user_pages/login.html', {'form': form})

#     def post(self, request, *args, **kwargs):
#         form = LoginForm(data=request.POST)
#         print("-------",request.POST)
#         if form.is_valid():
#             self.request = request
#             self.serializer = self.get_serializer(data=self.request.data,
#                                                 context={'request': request})
#             self.serializer.is_valid(raise_exception=True)
#             self.login()
#             user_response = self.get_response()
#             if user_response.status_code == 200:
#                 return render(request, 'user_pages/user_home.html',
#                             {'user': request.user})
#             else:
#                 return HttpResponse('Could not login')
#         return render(request, 'user_pages/login.html', {'form': form})


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

    def post(self, request, *args, **kwargs):
        print("---------------",request.user)
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
    # serializer_class = CustomUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(self.get_response_data(user),
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def get_serializer(self, *args, **kwargs):
        """
        overide default serializer
        """
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)


class CustomUserSignupHobo(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'user_pages/signup_hobo.html'

    def get(self, request):
        form = SignUpForm()
        return render(request, 'user_pages/signup_hobo.html', {'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)
        must_validate_email = getattr(settings, "AUTH_EMAIL_VERIFICATION", True)
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
                    signup_code = SignupCode.objects.create_signup_code(new_user, ipaddr)
                    signup_code.send_signup_email()

                return render(request, 'user_pages/user_email_verification.html',
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
