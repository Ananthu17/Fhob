
import ast
import operator
import requests
import json

from django.db.models import Count
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

from .models import MessageStatus, SpamMessage, UserMessage, \
    MessageNotification, UserMessageImages, UserMessageFileUpload
from hobo_user.models import CustomUser, CustomUserSettings

from .serializers import UserMessageSerializer, MessageThreadSerializer
from project.serializers import IdSerializer
from hobo_user.utils import notify


class ComposeMessageView(LoginRequiredMixin, TemplateView):
    template_name = 'message/compose-message.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # users = CustomUser.objects.filter(is_staff=False)
        users = CustomUser.objects.exclude(pk=self.request.user.id)
        context['users'] = users
        return context

    def post(self, request, *args, **kwargs):
        data_dict = self.request.POST
        user = self.request.user
        images = []
        files = []
        if 'message' in data_dict:
            message = data_dict['message']
        if 'images' in self.request.FILES:
            images = self.request.FILES.getlist('images')
        if 'files' in self.request.FILES:
            files = self.request.FILES.getlist('files')

        key = Token.objects.get(user=user).key
        token = 'Token '+key
        if message or images or files:
            print("message", message)
            print("images", images)
            print("files", files)
            origin_url = settings.ORIGIN_URL
            complete_url = origin_url + '/message/compose-message-api/'
            user_response = requests.post(
                                complete_url,
                                data=json.dumps(data_dict),
                                headers={'Content-type': 'application/json',
                                         'Authorization': token})
            byte_str = user_response.content
            dict_str = byte_str.decode("UTF-8")
            response = ast.literal_eval(dict_str)
            response = dict(response)
            if 'msg_id' in response:
                try:
                    msg_obj = UserMessage.objects.get(pk=response['msg_id'])
                    if images:
                        for img in images:
                            img_obj = UserMessageImages()
                            img_obj.message = msg_obj
                            img_obj.image = img
                            img_obj.save()
                    if files:
                        for file in files:
                            file_obj = UserMessageFileUpload()
                            file_obj.message = msg_obj
                            file_obj.file = file
                            file_obj.save()
                    messages.success(self.request, "Message send.")
                except UserMessage.DoesNotExist:
                    messages.warning(self.request, "Failed to send message.")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            elif 'status' in response:
                if response['status'] != 200:
                    if 'errors' in response:
                        errors = response['errors']
                        print(errors)
                        messages.warning(
                            self.request, "Failed to send message.")
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class AllMessagesView(LoginRequiredMixin, TemplateView):
    template_name = 'message/all-messages.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chat_with = self.request.user
        logged_in_user = self.request.user

        msg_status_objs = MessageStatus.objects.filter(
                            Q(user=self.request.user) &
                            Q(is_spam=False)
                        ).values_list('msg_thread').distinct()

        user_messages = UserMessage.objects.filter(
                            Q(msg_thread__in=msg_status_objs) &
                            ~Q(delete_for=logged_in_user)
                            ).order_by('-created_time')

        chat_ids = user_messages.values('msg_thread').distinct()
        chat_dict = {}
        attachment_dict = {}
        read_status_dict = {}
        priority_status_dict = {}

        for id in chat_ids:
            chat_id = id['msg_thread']
            user_list = user_messages.filter(
                                    msg_thread=chat_id).order_by(
                                        '-created_time')
            last_msg = user_list.first()
            if last_msg.from_user == self.request.user:
                chat_with = last_msg.to_user
            else:
                chat_with = last_msg.from_user
            chat_dict[chat_with] = last_msg

            # check if there are attachments
            images = UserMessageImages.objects.filter(message=last_msg)
            pdf_files = UserMessageFileUpload.objects.filter(message=last_msg)
            if images:
                attachment_dict[last_msg.id] = True
            elif pdf_files:
                attachment_dict[last_msg.id] = True

            try:
                read_status_dict[chat_with.id] = MessageStatus.objects.get(
                            Q(msg_thread=chat_id) &
                            Q(user=self.request.user)
                        ).is_read
                priority_status_dict[chat_with.id] = MessageStatus.objects.get(
                            Q(msg_thread=chat_id) &
                            Q(user=self.request.user)
                        ).is_priority
            except MessageStatus.DoesNotExist:
                pass

        # print("status_dict: ", status_dict)
        sorted_dict = {k: v for k, v in sorted(chat_dict.items(), key=lambda item: item[1].created_time, reverse=True)}
        context['chat_dict'] = sorted_dict
        context['priority_status_dict'] = priority_status_dict
        context['read_status_dict'] = read_status_dict
        context['attachment_dict'] = attachment_dict
        return context


class ComposeMessageAPI(APIView):
    serializer_class = UserMessageSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        logged_in_user = self.request.user
        if serializer.is_valid():
            data_dict = serializer.data
            to_user_id = data_dict['to_user']
            try:
                to_user = CustomUser.objects.get(pk=to_user_id)
                try:
                    to_user_settings = CustomUserSettings.objects.get(
                                       user=to_user)
                    to_user_blocked_members = to_user_settings.blocked_members.values_list(
                                                'id', flat=True)

                    user_message_obj = UserMessage()
                    user_message_obj.to_user = to_user
                    user_message_obj.subject = data_dict['subject']
                    user_message_obj.message = data_dict['message']
                    user_message_obj.from_user = self.request.user
                    user_message_obj.msg_thread = user_message_obj.generate_msg_thread(
                                                    self.request.user.id,
                                                    to_user.id
                                                    )
                    user_message_obj.save()

                    # create message status objects for from and to users
                    try:
                        msg_status_to = MessageStatus.objects.get(
                                    Q(msg_thread=user_message_obj.msg_thread) &
                                    Q(user=to_user)
                        )
                        msg_status_to.is_read = False
                        # check if this is a spam message
                        if self.request.user.id in to_user_blocked_members:
                            msg_status_to.is_read = True
                            msg_status_to.is_spam = True
                            user_message_obj.delete_for.add(to_user)
                            user_message_obj.save()
                        msg_status_to.save()
                    except MessageStatus.DoesNotExist:
                        msg_status_to = MessageStatus()
                        msg_status_to.msg_thread = user_message_obj.msg_thread
                        msg_status_to.user = to_user
                        msg_status_to.is_read = False
                        # check if this is a spam message
                        if self.request.user.id in to_user_blocked_members:
                            msg_status_to.is_read = True
                            msg_status_to.is_spam = True
                            user_message_obj.delete_for.add(to_user)
                            user_message_obj.save()
                        msg_status_to.save()

                    try:
                        msg_status_from = MessageStatus.objects.get(
                                    Q(msg_thread=user_message_obj.msg_thread) &
                                    Q(user=self.request.user)
                        )
                        msg_status_from.is_read = True
                        msg_status_from.save()
                    except MessageStatus.DoesNotExist:
                        msg_status_from = MessageStatus()
                        msg_status_from.msg_thread = user_message_obj.msg_thread
                        msg_status_from.user = self.request.user
                        msg_status_from.is_read = True
                        msg_status_from.save()

                    # update message notification table
                    notification = MessageNotification()
                    notification.user = to_user
                    notification.from_user = logged_in_user
                    notification.notification_message = "You have a message from "+str(logged_in_user.get_full_name())
                    notification.save()
                    # send notification
                    room_name = "user_"+str(to_user.id)
                    notification_msg = {
                            'type': 'send_message_notification',
                            'message': str(notification.notification_message),
                            'from': logged_in_user.get_full_name(),
                            "event": "USER_MESSAGES"
                        }
                    notify(room_name, notification_msg)
                    # end notification section

                    messages.success(self.request, "Message Send")
                    response = {'message': "Message Send",
                                'msg_id':user_message_obj.id,
                                'status': status.HTTP_200_OK}
                except CustomUserSettings.DoesNotExist:
                    response = {'error': "Custom user settings not found",
                                'status': status.HTTP_200_OK}
            except CustomUser.DoesNotExist:
                response = {'error': "Invalid ID",
                            'status': status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class AddToPriorityAPI(APIView):
    serializer_class = MessageThreadSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            msg_thread = data_dict['msg_thread']
            try:
                msg_status = MessageStatus.objects.get(
                            Q(msg_thread=msg_thread) &
                            Q(user=self.request.user)
                            )
                msg_status.is_priority = True
                msg_status.save()
                response = {'message': "Message added to priority list.",
                            'status': status.HTTP_200_OK}
            except MessageStatus.DoesNotExist:
                response = {'error': "Invalid message ID",
                            'status': status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class RemoveFromPriorityAPI(APIView):
    serializer_class = MessageThreadSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            msg_thread = data_dict['msg_thread']

            try:
                msg_status = MessageStatus.objects.get(
                            Q(msg_thread=msg_thread) &
                            Q(user=self.request.user)
                            )
                msg_status.is_priority = False
                msg_status.save()
                response = {'message': "Message removed from priority list.",
                            'status': status.HTTP_200_OK}
                messages.success(self.request, "Message removed from priority list.")
            except MessageStatus.DoesNotExist:
                response = {'error': "Invalid message ID",
                            'status': status.HTTP_400_BAD_REQUEST}

        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class DeleteMessageAPI(APIView):
    serializer_class = MessageThreadSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            msg_thread = data_dict['msg_thread']

            try:
                user_messages = UserMessage.objects.filter(msg_thread=msg_thread)
                for msg in user_messages:
                    msg.delete_for.add(self.request.user)
                response = {'message': "Messages deleted",
                            'status': status.HTTP_200_OK}
                messages.success(self.request, "Messages Removed.")
            except MessageStatus.DoesNotExist:
                response = {'error': "Invalid message ID",
                            'status': status.HTTP_400_BAD_REQUEST}

        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class ReportSpamAPI(APIView):
    serializer_class = IdSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            msg_id = data_dict['id']
            try:
                spam_msg = UserMessage.objects.get(pk=msg_id)
                if spam_msg.from_user == self.request.user:
                    spam_user = spam_msg.to_user
                else:
                    spam_user = spam_msg.from_user
                msg_thread = spam_msg.msg_thread
                try:
                    # block user
                    user_settings = CustomUserSettings.objects.get(
                                    user=self.request.user)
                    user_settings.blocked_members.add(spam_user)
                    user_settings.save()

                    # report message
                    spam_msg_obj = SpamMessage()
                    spam_msg_obj.spam_user = spam_user
                    spam_msg_obj.reported_by = self.request.user
                    spam_msg_obj.save()

                    # remove messages from blocked user
                    try:
                        msg_status = MessageStatus.objects.get(
                                    Q(msg_thread=msg_thread) &
                                    Q(user=self.request.user)
                                    )
                        msg_status.is_spam = True
                        msg_status.save()
                        all_msgs = UserMessage.objects.filter(msg_thread=msg_thread)
                        for msg_obj in all_msgs:
                            msg_obj.delete_for.add(self.request.user)

                    except MessageStatus.DoesNotExist:
                        pass

                    response = {'message': "Message reported and sender is blocked.",
                                'status': status.HTTP_200_OK}
                    messages.success(self.request, "Message reported and sender is blocked.")
                except CustomUserSettings.DoesNotExist:
                    response = {'errors': "Custom User Settings not found",
                                'status': status.HTTP_400_BAD_REQUEST}
            except UserMessage.DoesNotExist:
                response = {'error': "Invalid ID",
                            'status': status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class PriorityMessagesView(LoginRequiredMixin, TemplateView):
    template_name = 'message/priority_messages.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        priority_messages = []
        attachment_dict = {}
        logged_in_user = self.request.user
        msg_status_objs = MessageStatus.objects.filter(
                            Q(user=self.request.user) &
                            Q(is_priority=True) &
                            Q(is_spam=False)
                        ).values_list('msg_thread').distinct()

        priority_messages = UserMessage.objects.filter(
                            Q(msg_thread__in=msg_status_objs) &
                            ~Q(delete_for=logged_in_user)
                            ).order_by('-created_time')
        chat_ids = priority_messages.values('msg_thread').distinct()
        chat_dict = {}
        status_dict = {}
        for id in chat_ids:
            chat_id = id['msg_thread']
            user_list = priority_messages.filter(
                                    msg_thread=chat_id).order_by(
                                        '-created_time')
            last_msg = user_list.first()
            if last_msg.from_user == self.request.user:
                chat_with = last_msg.to_user
            else:
                chat_with = last_msg.from_user
            chat_dict[chat_with] = last_msg

            # check if there are attachments
            images = UserMessageImages.objects.filter(message=last_msg)
            pdf_files = UserMessageFileUpload.objects.filter(message=last_msg)
            if images:
                attachment_dict[last_msg.id] = True
            elif pdf_files:
                attachment_dict[last_msg.id] = True

            try:
                status_dict[chat_with.id] = MessageStatus.objects.get(
                            Q(msg_thread=chat_id) &
                            Q(user=self.request.user)
                        ).is_read
            except MessageStatus.DoesNotExist:
                pass

        # print("status_dict: ", status_dict)
        sorted_dict = {k: v for k, v in sorted(chat_dict.items(), key=lambda item: item[1].created_time, reverse=True)}
        context['chat_dict'] = sorted_dict
        context['status_dict'] = status_dict
        context['attachment_dict'] = attachment_dict
        return context


class MessageDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'message/message-reply.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logged_in_user = self.request.user
        logged_in_user_id = logged_in_user.id
        chat_with_id = self.kwargs.get('id')
        img_dict = {}
        file_dict = {}

        if chat_with_id < logged_in_user_id:
            msg_thread = "chat_"+str(chat_with_id)+"_"+str(logged_in_user_id)
        else:
            msg_thread = "chat_"+str(logged_in_user_id)+"_"+str(chat_with_id)

        try:
            msg_status_obj = MessageStatus.objects.get(
                                Q(msg_thread=msg_thread) &
                                Q(user=self.request.user)
                            )
            # if msg_status_obj.is_spam is True or msg_status_obj.is_deleted is True:
            if msg_status_obj.is_spam is True:
                user_messages = []
            else:
                user_messages = UserMessage.objects.filter(
                                Q(msg_thread=msg_thread) &
                                ~Q(delete_for=logged_in_user)
                                ).order_by('-created_time')

                # check if there are attachments
                for msg in user_messages:
                    images = UserMessageImages.objects.filter(message=msg)
                    pdf_files = UserMessageFileUpload.objects.filter(message=msg)
                    if images:
                        img_dict[msg.id] = images
                    if pdf_files:
                        file_dict[msg.id] = pdf_files

                msg_status_obj.is_read = True
                msg_status_obj.save()

                # remove message notification
                try:
                    chat_with_user = CustomUser.objects.get(pk=chat_with_id)
                    unread_msg_notifications = MessageNotification.objects.filter(
                                        Q(user=self.request.user) &
                                        Q(from_user=chat_with_user) &
                                        Q(status_type=MessageNotification.UNREAD)
                                        )

                    for notification in unread_msg_notifications:
                        notification.status_type = MessageNotification.READ
                        notification.save()
                except MessageNotification.DoesNotExist:
                    pass
        except MessageStatus.DoesNotExist:
            user_messages = []

        context['user_messages'] = user_messages
        context['chat_with_id'] = chat_with_id
        context['img_dict'] = img_dict
        context['file_dict'] = file_dict
        return context

    def post(self, request, *args, **kwargs):
        data_dict = self.request.POST
        user = self.request.user
        images = []
        files = []
        if 'message' in data_dict:
            message = data_dict['message']
        if 'images' in self.request.FILES:
            images = self.request.FILES.getlist('images')
        if 'files' in self.request.FILES:
            files = self.request.FILES.getlist('files')
        print(data_dict)
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        if message or images or files:
            print("message", message)
            print("images", images)
            print("files", files)
            origin_url = settings.ORIGIN_URL
            complete_url = origin_url + '/message/compose-message-api/'
            user_response = requests.post(
                                complete_url,
                                data=json.dumps(data_dict),
                                headers={'Content-type': 'application/json',
                                         'Authorization': token})
            byte_str = user_response.content
            dict_str = byte_str.decode("UTF-8")
            response = ast.literal_eval(dict_str)
            response = dict(response)
            if 'msg_id' in response:
                try:
                    msg_obj = UserMessage.objects.get(pk=response['msg_id'])
                    if images:
                        for img in images:
                            img_obj = UserMessageImages()
                            img_obj.message = msg_obj
                            img_obj.image = img
                            img_obj.save()
                    if files:
                        for file in files:
                            file_obj = UserMessageFileUpload()
                            file_obj.message = msg_obj
                            file_obj.file = file
                            file_obj.save()
                except UserMessage.DoesNotExist:
                    messages.warning(self.request, "Failed to send message.")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            elif 'status' in response:
                if response['status'] != 200:
                    if 'errors' in response:
                        errors = response['errors']
                        print(errors)
                        messages.warning(
                            self.request, "Failed to send message.")
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class GetMessageNotificationAPI(APIView):
    # serializer_class = MessageNotificationSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        response = {}
        unread_msg_count = MessageNotification.objects.filter(
                            Q(user=self.request.user) &
                            Q(status_type=MessageNotification.UNREAD)
                            ).count()
        response['unread_msg_count'] = unread_msg_count
        return Response(response)