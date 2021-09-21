
from django.shortcuts import render
from django.http import FileResponse, Http404, HttpResponse
from django.conf import settings
from django.db.models import Count, Sum
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.db.models import Q

from rest_framework import serializers, status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import UserMessage
from hobo_user.models import CustomUser

from .serializers import UserMessageSerializer


class ComposeMessageView(LoginRequiredMixin, TemplateView):
    template_name = 'message/compose-message.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = CustomUser.objects.filter(is_staff=False)
        context['users'] = users
        return context


class AllMessagesView(LoginRequiredMixin, TemplateView):
    template_name = 'message/all-messages.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_messages = UserMessage.objects.filter(to_user=self.request.user)
        context['user_messages'] = user_messages
        return context


class ComposeMessageAPI(APIView):
    serializer_class = UserMessageSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            to_user_id = data_dict['to_user']
            try:
                to_user = CustomUser.objects.get(pk=to_user_id)
                user_message_obj = UserMessage()
                user_message_obj.to_user = to_user
                user_message_obj.subject = data_dict['subject']
                user_message_obj.message = data_dict['message']
                user_message_obj.from_user = self.request.user
                user_message_obj.save()
                messages.success(self.request, "Message Send")
                response = {'message': "Message Send",
                            'status': status.HTTP_200_OK}
            except CustomUser.DoesNotExist:
                response = {'error': "Invalid ID",
                            'status': status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)
