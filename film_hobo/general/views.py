from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token

from .serializers import HelpSerializer

from .models import Help

from .forms import HelpForm
# Create your views here.


class HelpAPI(APIView):
    serializer_class = HelpSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        response = {}
        help_objects = Help.objects.filter(user=self.request.user)
        for item in help_objects:
            serializer = self.serializer_class(item).data
            response[item.subject] = serializer
        return Response(response)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            screenshot =  request.data['screenshot']
            help_obj = Help()
            help_obj.user = self.request.user
            help_obj.subject = data_dict['subject']
            help_obj.description = data_dict['description']
            help_obj.screenshot = screenshot
            help_obj.save()
            response = {'message': "Problem reported",
                        'status': status.HTTP_200_OK}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class HelpView(LoginRequiredMixin, TemplateView):
    template_name = 'user_pages/help.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = HelpForm

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        json_dict = {}
        json_dict['subject'] = self.request.POST.get('subject')
        json_dict['description'] = self.request.POST.get('description')
        json_dict['screenshot'] = self.request.POST.get('screenshot')
        user_response = requests.post(
                                'http://127.0.0.1:8000/hobo_user/help-api/',
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
                        self.request, "Failed to send message !!")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        messages.success(self.request, "Message received. Will get back to you soon.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))