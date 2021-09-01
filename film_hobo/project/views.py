import ast
import os
import io
import json
import requests
import boto3
import datetime
from django.utils import timezone
import mammoth
import fitz

import PIL
from fpdf import FPDF
from django.core import files
from io import BytesIO
from pdf2image import convert_from_path
from braces.views import JSONResponseMixin
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph, Spacer, Table, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from django.http import FileResponse, Http404, HttpResponse
from django.conf import settings
from django.db.models import Count, Sum
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.db.models import Sum
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render

from rest_framework.exceptions import ParseError
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import (ListAPIView,
                                     CreateAPIView, DestroyAPIView,
                                     UpdateAPIView, get_object_or_404)

from hobo_user.models import Location, Team, ProjectMemberRating, CustomUser, UserProject, \
     UserRating, JobType, UserRatingCombined, UserNotification, Project, \
     VideoRatingCombined
from .models import Audition, AuditionRating, AuditionRatingCombined, \
    Character, Comment, SceneImages, Sides, ProjectTracking, ProjectRating
from .serializers import RateUserSkillsSerializer, ProjectVideoURLSerializer, \
      CharacterSerializer, UpdateCharacterSerializer, \
      ProjectLastDateSerializer, RemoveCastSerializer, ReplaceCastSerializer, \
      SidesSerializer, AuditionSerializer, PostProjectVideoSerializer, \
      PasswordSerializer, ProjectLoglineSerializer, TrackProjectSerializer, \
      RateAuditionSerializer, AuditionStatusSerializer, ProjectRatingSerializer, \
      CommentSerializer, DeleteCommentSerializer, PdfToImageSerializer, \
      SceneImagesSerializer, SceneImageSerializer, CastRequestSerializer, \
      CancelCastRequestSerializer, UserProjectSerializer
from hobo_user.serializers import UserSerializer
from hobo_user.utils import notify, get_notifications_time
from .forms import VideoSubmissionLastDateForm, SubmitAuditionForm, AddSidesForm
from django.contrib.auth.hashers import make_password


class ProjectVideoPlayerView(LoginRequiredMixin, TemplateView):
    template_name = 'project/videoplayer.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('id')
        project = Project.objects.get(id=project_id)
        rating_dict = {}
        job_types_dict = {}
        team_members = Team.objects.filter(project=project_id)
        for team_member in team_members:
            if team_member.job_type in job_types_dict:
                job_types_dict[team_member.job_type].append(team_member)
            else:
                job_types_dict[team_member.job_type] = []
                job_types_dict[team_member.job_type].append(team_member)

        project_members_rating = ProjectMemberRating.objects.filter(
                                 project=project_id)
        # for obj in project_members_rating:
        #     team_objs = obj.user.team_user.all()
        #     key_obj = team_objs.filter(
        #             Q(project=obj.project) &
        #             Q(job_type=obj.job_type)
        #         ).first()
        #     key = key_obj.id
        #     rating_dict[key] = obj.rating*20

        for obj in team_members:
            rating_dict[obj] = 0
            try:
                project_members_rating = ProjectMemberRating.objects.get(
                                        Q(project=project_id) &
                                        Q(user=obj.user) &
                                        Q(job_type=obj.job_type)
                                        )
                rating_dict[obj.id] = project_members_rating.rating*20
            except ProjectMemberRating.DoesNotExist:
                rating_dict[obj.id] = 0

        comments = Comment.objects.filter(project=project).order_by('-created_time')

        # comments = Comment.objects.filter(
        #            Q(project=project) &
        #            Q(reply_to=None)
        #             ).order_by('created_time')
        # reply_dict = {}
        # for obj in comments:
        #     reply_dict[obj.id] = []
        #     reply_comments = Comment.objects.filter(
        #                         Q(project=project) &
        #                         Q(reply_to=obj)
        #                         ).order_by('created_time')
        #     reply_dict[obj.id] = reply_comments
        context['comments'] = comments
        # context['reply_dict'] = reply_dict

        context["rating_dict"] = rating_dict
        context["job_types_dict"] = job_types_dict
        context["project"] = project
        return context


class RateUserSkillsAPI(APIView):
    serializer_class = RateUserSkillsSerializer
    permission_classes = (IsAuthenticated,)

    def check_membership_change(self, user, job_type):
        count = 0
        project_member_rating = ProjectMemberRating.objects.filter(
                                Q(user=user) &
                                Q(job_type=job_type))
        project_count = project_member_rating.count()
        user_rating_count = 0
        project_ids = []
        print("project_count", project_count)

        # if user have participated in 5 projects for given job type
        if project_count >= 5:
            for item in project_member_rating:
                if item.rating >= 4:
                    count = count+1
                    project_ids.append(item.project.id)
            # if for 5 projects user has got rating more than or equal to 4
            if count >= 5:
                # check if these 5 projects have atleast 10 ratings each
                user_rating = UserRating.objects.filter(
                                    Q(user=user) &
                                    Q(job_type=job_type) &
                                    Q(project__id__in=project_ids)
                                )
                rating_count = user_rating.values('project').annotate(count=Count('project'))
                for item in rating_count:
                    if item['count'] >= 10:
                        user_rating_count += 1
                # if for those 5 projects he has got atleast 10 ratings each
                if user_rating_count >= 5:
                    user.membership = CustomUser.PRO
                    user.save()

                    #update notification table
                    notification = UserNotification()
                    notification.user = user
                    notification.notification_type = UserNotification.MEMBERSHIP_CHANGE
                    notification.message = "Congratulations!! Considering your profile rating we have upgraded your membership from Indie to PRO"
                    notification.save()
                    # send notification
                    room_name = "user_"+str(user.id)
                    notification_msg = {
                            'type': 'send_membership_notification',
                            'message': str(notification.message),
                            'from': "FilmHobo",
                            "event": "MEMBERSHIP_CHANGE"
                        }
                    notify(room_name, notification_msg)
                    # end notification section
                else:
                    return
            else:
                return
        else:
            return
        return

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        reason = ""
        if serializer.is_valid():
            data_dict = serializer.data
            project_member_id = data_dict['project_member_id']
            if 'reason' in data_dict:
                reason = data_dict['reason']
            rating = data_dict['rating']
            try:
                project_member_obj = Team.objects.get(
                                     id=project_member_id)
                user = project_member_obj.user
                job_type = project_member_obj.job_type
                project = project_member_obj.project

                # update user rating table
                user_rating = UserRating()
                user_rating.user = user
                user_rating.rated_by = self.request.user
                user_rating.job_type = job_type
                user_rating.rating = rating
                user_rating.reason = reason
                user_rating.project = project
                user_rating.save()

                # update combined rating
                try:
                    user_rating_combined = UserRatingCombined.objects.get(
                                            Q(user=user) &
                                            Q(job_type=job_type)
                                            )
                    count = UserRating.objects.filter(
                            Q(user=user) &
                            Q(job_type=job_type)
                            ).count()
                    aggregate_rating = UserRating.objects.filter(
                            Q(user=user) &
                            Q(job_type=job_type)
                            ).aggregate(Sum('rating'))
                    rating_sum = aggregate_rating['rating__sum']
                    new_rating = rating_sum/count
                    user_rating_combined.rating = new_rating
                    user_rating_combined.save()
                except UserRatingCombined.DoesNotExist:
                    user_rating_combined = UserRatingCombined()
                    user_rating_combined.user = user
                    user_rating_combined.job_type = job_type
                    user_rating_combined.rating = rating
                    user_rating_combined.save()

                # update combined project member rating
                try:
                    project_member_rating_obj = ProjectMemberRating.objects.get(
                                                 Q(user=user) &
                                                 Q(job_type=job_type) &
                                                 Q(project=project)
                                                )
                    count = UserRating.objects.filter(
                            Q(user=user) &
                            Q(job_type=job_type) &
                            Q(project=project)
                            ).count()
                    aggregate_rating = UserRating.objects.filter(
                            Q(user=user) &
                            Q(job_type=job_type)&
                            Q(project=project)
                            ).aggregate(Sum('rating'))
                    rating_sum = aggregate_rating['rating__sum']
                    new_rating = rating_sum/count
                    project_member_rating_obj.rating = new_rating
                    project_member_rating_obj.save()
                except ProjectMemberRating.DoesNotExist:
                    project_member_rating_obj = ProjectMemberRating()
                    project_member_rating_obj.job_type = job_type
                    project_member_rating_obj.user = user
                    project_member_rating_obj.project = project
                    project_member_rating_obj.rating = rating
                    project_member_rating_obj.save()

                # update total video rating
                video_rating_objs_count = ProjectMemberRating.objects.filter(
                                          project=project).count()
                video_aggregate_rating = ProjectMemberRating.objects.filter(
                                    project=project).aggregate(Sum('rating'))
                rating_sum = video_aggregate_rating['rating__sum']
                new_rating = rating_sum/video_rating_objs_count
                project.video_rating = new_rating*20
                project.save()


                #update notification table
                notification = UserNotification()
                notification.user = user
                notification.notification_type = UserNotification.USER_RATING
                notification.from_user = self.request.user
                notification.message = self.request.user.get_full_name()+" rated you "+rating+" stars as "+project_member_obj.job_type.title+" for the project "+project_member_obj.project.title
                notification.save()
                # send notification
                room_name = "user_"+str(user.id)
                notification_msg = {
                        'type': 'send_profile_rating_notification',
                        'message': str(notification.message),
                        'from': str(self.request.user.id),
                        "event": "USER_RATING"
                    }
                notify(room_name, notification_msg)
                # end notification section

                #update notification table - video rating
                notification = UserNotification()
                notification.user = project.creator
                notification.project = project
                notification.notification_type = UserNotification.VIDEO_RATING
                notification.message = project.title+" video rating reached "+str(round(new_rating,2))+"/5"
                notification.save()
                # send notification - video rating
                room_name = "user_"+str(project.creator.id)
                notification_msg = {
                        'type': 'send_video_rating_notification',
                        'message': str(notification.message),
                        'from': 'FilmHobo',
                        "event": "VIDEO_RATING"
                    }
                notify(room_name, notification_msg)
                # end notification section

                response = {'message': "%s rated sucessfully"%(
                            project_member_obj.user.get_full_name()),
                            'status': status.HTTP_200_OK,
                            'combined_rating': user_rating_combined.rating}
                msg = project_member_obj.job_type.title +" "+project_member_obj.user.get_full_name() +" rated with "+rating+"stars"
                messages.success(
                        self.request, msg
                        )
                # check if membership change is possible
                if user.membership == CustomUser.INDIE:
                    self.check_membership_change(user, job_type)

            except Team.DoesNotExist:
                response = {'errors': 'Invalid ID', 'status':
                            status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class GetMembershipChangeNotificationAjaxView(View, JSONResponseMixin):
    template_name = 'project/membership_change_notification.html'

    def get(self, *args, **kwargs):
        context = dict()
        message = self.request.GET.get('message')
        notification_html = render_to_string(
                                'project/membership_change_notification.html',
                                {'message': message})
        context['notification_html'] = notification_html
        return self.render_json_response(context)


class GetAuditionStatusNotificationAjaxView(View, JSONResponseMixin):
    template_name = 'user_pages/audition_status_notification.html'

    def get(self, *args, **kwargs):
        context = dict()
        notification = UserNotification.objects.filter(
                            Q(user=self.request.user) &
                            Q(notification_type=UserNotification.AUDITION_STATUS)
                            ).order_by('-created_time').first()
        notification_html = render_to_string(
                                'project/audition_status_notification.html',
                                {'notification': notification
                                })
        context['notification_html'] = notification_html
        return self.render_json_response(context)


class GetVideoRatingNotificationAjaxView(View, JSONResponseMixin):
    template_name = 'user_pages/audition_status_notification.html'

    def get(self, *args, **kwargs):
        context = dict()
        notification = UserNotification.objects.filter(
                            Q(user=self.request.user) &
                            Q(notification_type=UserNotification.VIDEO_RATING)
                            ).order_by('-created_time').first()
        notification_html = render_to_string(
                                'project/audition_status_notification.html',
                                {'notification': notification
                                })
        context['notification_html'] = notification_html
        return self.render_json_response(context)


class GetProjectRatingNotificationAjaxView(View, JSONResponseMixin):
    template_name = 'user_pages/audition_status_notification.html'

    def get(self, *args, **kwargs):
        context = dict()
        notification = UserNotification.objects.filter(
                            Q(user=self.request.user) &
                            Q(notification_type=UserNotification.PROJECT_RATING)
                            ).order_by('-created_time').first()
        notification_html = render_to_string(
                                'project/audition_status_notification.html',
                                {'notification': notification
                                })
        context['notification_html'] = notification_html
        return self.render_json_response(context)


class SingleFilmProjectView(LoginRequiredMixin, TemplateView):
    template_name = 'project/single_film_project.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'
    UPLOAD_FOLDER = "uploads"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('id')
        project = Project.objects.get(id=project_id)
        project_creator_rating = 0

        project_creator_job = JobType.objects.filter(
                               slug='project-creator'
                               ).first()
        if project_creator_job:
            try:
                project_creator = Team.objects.get(
                                    Q(project=project) &
                                    Q(job_type=project_creator_job) 
                                    ).user
                rating_object = UserRatingCombined.objects.filter(
                            Q(user=project_creator) &
                            Q(job_type=project_creator_job)
                        ).first()
                if rating_object:
                    project_creator_rating = rating_object.rating*20
                else:
                    project_creator_rating = 0
            except Team.DoesNotExist:
                project_creator = ""
            context['project_creator_rating'] = project_creator_rating

        characters = Character.objects.filter(project=project)
        context['characters'] = characters

        try:
            actoractress = JobType.objects.get(slug='actoractress')
        except JobType.DoesNotExist:
            actoractress = ""
        # try:
        #     actress = JobType.objects.get(slug='actress')
        # except JobType.DoesNotExist:
        #     actress = ""
        rating_dict = {}
        for character in characters:
            if character.attached_user:
                try:
                    rating_obj = UserRatingCombined.objects.get(
                                    Q(user=character.attached_user) &
                                    Q(job_type=actoractress)
                                )
                    rating_dict[character.attached_user.id] = (rating_obj.rating)*20
                except UserRatingCombined.DoesNotExist:
                    rating_dict[character.attached_user.id] = 0
        context['rating_dict'] = rating_dict
        context['project'] = project
        context['video_types'] = Project.VIDEO_TYPE_CHOICES
        return context


class AddProjectVideoView(LoginRequiredMixin, TemplateView):
    template_name = 'project/single_film_project.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'
    UPLOAD_FOLDER = "uploads"

    def post(self, request, *args, **kwargs):
        project_id = self.kwargs.get('id')
        print(self.request.POST)
        project = get_object_or_404(Project, pk=project_id)
        cover_image = self.request.FILES['video_cover_image']
        video_type = self.request.POST.get('video_type')
        url = self.request.POST.get('video_url')
        project.video_type = video_type
        project.video_cover_image = cover_image
        project.video_status = Project.UPLOADED

        if video_type == 'youtube':
            url_temp = url.split("v=")[1]
            video_url = url_temp.split("&")[0]
            project.video_url = video_url
        if video_type == 'vimeo':
            if url.startswith('https://vimeo.com/'):
                video_url = url.split('https://vimeo.com/')[1]
                project.video_url = video_url
            if url.startswith('http://vimeo.com/'):
                video_url = url.split('http://vimeo.com/')[1]
                project.video_url = video_url
            if url.startswith('vimeo.com/'):
                video_url = url.split('vimeo.com/')[1]
                project.video_url = video_url
        project.save()
        messages.success(self.request, "Video Uploaded")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class SaveProjectVideoUrlAPI(APIView):
    serializer_class = ProjectVideoURLSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            # print(data_dict)
            id = data_dict['id']
            video_url = data_dict['video_url']
            video_type = data_dict['video_type']
            try:
                project = Project.objects.get(pk=id)
                project.video_type = video_type
                project.video_url = video_url
                try:
                    cover_image = request.data['video_cover_image']
                    project.video_cover_image = cover_image
                except KeyError:
                    raise ParseError('Request has no cover image attached')
                project.video_status = Project.UPLOADED
                project.save()
                response = {'message': "Video URL Saved",
                            'status': status.HTTP_200_OK}
                messages.success(self.request, "Video URL saved")
            except Project.DoesNotExist:
                response = {'errors': 'Invalid project ID', 'status':
                            status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class PostProjectVideoAPI(APIView):
    serializer_class = PostProjectVideoSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            project_id = data_dict['project_id']
            try:
                project = Project.objects.get(pk=project_id)
                if project.video_status == Project.UPLOADED:
                    project.video_status = Project.POSTED
                    project.save()
                    response = {'message': "Video posted to screening room.",
                                'status': status.HTTP_200_OK}
                    messages.success(self.request, "Video posted to screening room.")
                elif project.video_status == Project.NOT_AVAILABLE:
                    response = {'errors': 'Video not available.', 'status':
                                status.HTTP_400_BAD_REQUEST}
                    messages.warning(self.request, "Video not available.")
                elif project.video_status == Project.POSTED:
                    response = {'errors': 'Video already posted to screening room.', 'status':
                                status.HTTP_400_BAD_REQUEST}
                    messages.warning(self.request, "Video already posted to screening room.")
            except Project.DoesNotExist:
                response = {'errors': 'Invalid project ID', 'status':
                            status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class SaveVideoUploadTypeAjaxView(View, JSONResponseMixin):
    template_name = 'user_pages/swap-images.html'

    def get(self, *args, **kwargs):
        response = {}
        id = self.request.GET.get('project_id')
        try:
            project = Project.objects.get(id=id)
            project.video_type = Project.UPLOAD_VIDEO
            project.video_url = ""
            project.save()
        except Project.DoesNotExist:
            response = {"message": "Invalid project id"}
        return self.render_json_response(response)


class CharacterCreateAPIView(APIView):
    serializer_class = CharacterSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            try:
                project = Project.objects.get(pk=data_dict['project'])
                character_obj = Character()
                character_obj.name = data_dict['name']
                character_obj.description = data_dict['description']
                character_obj.project = project
                character_obj.password = data_dict['password']
                # character_obj.sort_order = data_dict['sort_order']
                character_obj.save()
                response = {'message': "Character added",
                            'status': status.HTTP_200_OK}
            except Project.DoesNotExist:
                response = {'errors': "Invalid Project ID", 'status':
                            status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class CharacterUpdateAPIView(UpdateAPIView):
    queryset = Character.objects.all()
    permission_classes = (IsAuthenticated,)
    lookup_field = 'id'
    serializer_class = UpdateCharacterSerializer


class EditCharactersView(LoginRequiredMixin, TemplateView):
    template_name = 'project/edit-characters.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('id')
        project = Project.objects.get(pk=project_id)
        context['project'] = project
        characters = Character.objects.filter(project=project.id)
        context['characters'] = characters
        return context

    def post(self, request, *args, **kwargs):
        json_dict = {}
        project_id = self.kwargs.get('id')
        user = self.request.user
        character_ids = self.request.POST.getlist('character_id')
        names = self.request.POST.getlist('name')
        descriptions = self.request.POST.getlist('description')
        passwords = self.request.POST.getlist('password')
        count = len(names)
        key = Token.objects.get(user=user).key
        token = 'Token '+key

        json_dict['project'] = str(project_id)
        for i in range(count):
            json_dict['name'] = names[i]
            json_dict['description'] = descriptions[i]
            if passwords[i] != "":
                json_dict['password'] = passwords[i]
            else:
                json_dict['password'] = ""
            user_response = requests.put(
                                'http://127.0.0.1:8000/project/charater/update/'+character_ids[i]+'/',
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
                            self.request, "Failed to update cast !!")
                        return HttpResponseRedirect(
                            request.META.get('HTTP_REFERER', '/'))
        messages.success(self.request, "Cast updated successfully")
        return HttpResponseRedirect("/project/add-characters/%s/" % (project_id))


class AddCharactersView(LoginRequiredMixin, TemplateView):
    template_name = 'project/add-characters.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('id')
        sites_dict = {}
        try:
            project = Project.objects.get(pk=project_id)
            context['project'] = project
            characters = Character.objects.filter(project=project.id)
            context['characters'] = characters
            last_date_form = VideoSubmissionLastDateForm
            context['last_date_form'] = last_date_form
            sides = Sides.objects.filter(project=project)
            for obj in sides:
                sites_dict[obj.character.id] = "Scene 1: "+obj.scene_1+"Scene 2: "+obj.scene_2+"Scene 3: "+obj.scene_3
            context['sites_dict'] = sites_dict
        except Project.DoesNotExist:
            context["message"] = "Project not found !!"
        return context

    def post(self, request, *args, **kwargs):
        json_dict = {}
        project_id = self.kwargs.get('id')
        user = self.request.user
        names = self.request.POST.getlist('name')
        descriptions = self.request.POST.getlist('description')
        passwords = self.request.POST.getlist('password')
        # sort_order = self.request.POST.getlist('sort_order')
        count = len(names)
        key = Token.objects.get(user=user).key
        token = 'Token '+key

        for i in range(count):
            json_dict['name'] = names[i]
            json_dict['description'] = descriptions[i]
            # if sort_order[i] != "":
            #     json_dict['sort_order'] = sort_order[i]
            # else:
            #     json_dict['sort_order'] = 0
            if passwords[i] != "":
                json_dict['password'] = passwords[i]
            else:
                json_dict['password'] = None
            json_dict['project'] = project_id
            user_response = requests.post(
                                'http://127.0.0.1:8000/project/charater/create/',
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
                            self.request, "Failed to update cast !!")
                        return HttpResponseRedirect(
                            request.META.get('HTTP_REFERER', '/'))
        messages.success(self.request, "Cast updated successfully")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class AddSidesAjaxView(View, JSONResponseMixin):
    template_name = 'project/add-sides-form.html'

    def get(self, *args, **kwargs):
        context = dict()
        count = self.request.GET.get('count')
        form_html = render_to_string(
                                'project/add-sides-form.html',
                                {'count': count})
        context['form_html'] = form_html
        return self.render_json_response(context)


class AddProjectSidesLastDateAPIView(APIView):
    serializer_class = ProjectLastDateSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            print(data_dict)
            try:
                project = Project.objects.get(pk=data_dict['id'])
                print(project)
                project.last_date = data_dict['last_date']
                project.save()
                response = {'message': "Laste date added.",
                            'status': status.HTTP_200_OK}
            except Project.DoesNotExist:
                response = {'errors': "Invalid Project ID", 'status':
                            status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class SidesCreateAPIView(APIView):
    serializer_class = SidesSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            project_id = data_dict['project']
            character_id = data_dict['character']
            project = get_object_or_404(Project, pk=project_id)
            character = get_object_or_404(Character, pk=character_id)
            try:
                sides_obj = Sides.objects.get(
                            Q(project=project) &
                            Q(character=character)
                            )
                if data_dict['scene_1'] is not None:
                    sides_obj.scene_1 = data_dict['scene_1']
                if data_dict['scene_2'] is not None:
                    sides_obj.scene_2 = data_dict['scene_2']
                if data_dict['scene_3'] is not None:
                    sides_obj.scene_3 = data_dict['scene_3']
                sides_obj.save()
            except Sides.DoesNotExist:
                sides_obj = Sides()
                sides_obj.project = project
                sides_obj.character = character
                sides_obj.scene_1 = data_dict['scene_1']
                sides_obj.scene_2 = data_dict['scene_2']
                sides_obj.scene_3 = data_dict['scene_3']
                sides_obj.save()

            if sides_obj.scene_1:
                sides_obj.scene_1_pdf=None
                scene_img_objs = SceneImages.objects.filter(
                                Q(project=project) &
                                Q(character=character) &
                                Q(scene=SceneImages.SCENE_1)
                                )
                for img_obj in scene_img_objs:
                    img_obj.delete()
            if sides_obj.scene_2:
                sides_obj.scene_2_pdf=None
                scene_img_objs = SceneImages.objects.filter(
                                Q(project=project) &
                                Q(character=character) &
                                Q(scene=SceneImages.SCENE_2)
                                )
                for img_obj in scene_img_objs:
                    img_obj.delete()
            if sides_obj.scene_3:
                sides_obj.scene_3_pdf=None
                scene_img_objs = SceneImages.objects.filter(
                                Q(project=project) &
                                Q(character=character) &
                                Q(scene=SceneImages.SCENE_3)
                                )
                for img_obj in scene_img_objs:
                    img_obj.delete()
            sides_obj.save()

            response = {'message': "Scenes added",
                        'status': status.HTTP_200_OK}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class AddSidesView(LoginRequiredMixin, TemplateView):
    template_name = 'project/add-sides.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('id')
        character_id = self.request.GET.get('character_id')
        project = get_object_or_404(Project, pk=project_id)
        context['project'] = project
        try:
            character = Character.objects.get(
                            Q(project=project) &
                            Q(id=character_id)
                        )
            context['character'] = character
            try:
                sides = Sides.objects.get(
                            Q(project=project) &
                            Q(character=character)
                            )
                context['sides'] = sides
            except Sides.DoesNotExist:
                pass
        except Character.DoesNotExist:
            pass
        return context


class CastApplyAuditionView(LoginRequiredMixin, TemplateView):
    template_name = 'project/cast-apply-audition.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('id')
        project_creator_rating = 0
        character_id = self.request.GET.get('character_id')
        project = get_object_or_404(Project, pk=project_id)
        context['project'] = project
        character = get_object_or_404(Character, pk=character_id)
        context['character'] = character
        context['video_types'] = Project.VIDEO_TYPE_CHOICES
        context['locations'] = Location.objects.all()

        # check if logged user can apply for audition
        try:
            actoractress = JobType.objects.get(slug='actoractress')
        except JobType.DoesNotExist:
            actoractress = ""
        # try:
        #     actress = JobType.objects.get(slug='actress')
        # except JobType.DoesNotExist:
        #     actress = ""
        logged_user = self.request.user
        try:
            logged_user_rating_obj = UserRatingCombined.objects.get(
                                    Q(user=logged_user) &
                                    Q(job_type=actoractress)
                                )
            logged_user_rating = logged_user_rating_obj.rating
        except UserRatingCombined.DoesNotExist:
            logged_user_rating = 0
        context['logged_user_rating'] = logged_user_rating
        # end

        try:
            sides = Sides.objects.get(
                        Q(project=project) &
                        Q(character=character)
                        )
            context['sides'] = sides
        except Sides.DoesNotExist:
            pass

        project_creator_job = JobType.objects.filter(
                               slug='project-creator'
                               ).first()
        if project_creator_job:
            try:
                project_creator = Team.objects.get(
                                    Q(project=project) &
                                    Q(job_type=project_creator_job)
                                    ).user
                rating_object = UserRatingCombined.objects.filter(
                            Q(user=project_creator) &
                            Q(job_type=project_creator_job)
                        ).first()
                if rating_object:
                    project_creator_rating = rating_object.rating*20
                else:
                    project_creator_rating = 0
            except Team.DoesNotExist:
                project_creator = ""
            context['project_creator_rating'] = project_creator_rating
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        data_dict = {}
        json_response = json.dumps(request.POST)
        data_dict = ast.literal_eval(json_response)
        project_id = self.kwargs.get('id')
        character_id = self.request.POST.get('character_id')
        project = get_object_or_404(Project, pk=project_id)
        character = get_object_or_404(Character, pk=character_id)
        cover_image = self.request.FILES['cover_image']
        audition_obj = Audition()
        audition_obj.project = project
        audition_obj.character = character
        audition_obj.name = data_dict['name']
        audition_obj.user = self.request.user
        location_id = data_dict['location']
        audition_obj.location = get_object_or_404(Location, pk=location_id)
        audition_obj.agent_name = data_dict['agent_name']
        audition_obj.agent_email = data_dict['agent_email']
        try:
            agent_user = CustomUser.objects.get(email=data_dict['agent_email'])
            audition_obj.agent = agent_user
        except CustomUser.DoesNotExist:
            pass
        video_type = data_dict['video_type']
        url = data_dict['video_url']
        audition_obj.video_type = video_type
        audition_obj.cover_image = cover_image

        if video_type == 'youtube':
            url_temp = url.split("v=")[1]
            video_url = url_temp.split("&")[0]
            audition_obj.video_url = video_url
        if video_type == 'vimeo':
            if url.startswith('https://vimeo.com/'):
                video_url = url.split('https://vimeo.com/')[1]
                audition_obj.video_url = video_url
            if url.startswith('http://vimeo.com/'):
                video_url = url.split('http://vimeo.com/')[1]
                audition_obj.video_url = video_url
            if url.startswith('vimeo.com/'):
                video_url = url.split('vimeo.com/')[1]
                audition_obj.video_url = video_url
        audition_obj.save()
        # update user-project-table
        user_project_obj = UserProject()
        user_project_obj.user = self.request.user
        user_project_obj.project = project
        user_project_obj.relation_type = UserProject.APPLIED
        user_project_obj.audition = audition_obj
        user_project_obj.character = character
        user_project_obj.save()
        # end
        messages.success(self.request, "Audition submitted successfully")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def getpdf(request, **kwargs):
    buff = io.BytesIO()
    response = HttpResponse(content_type='application/pdf')
    project_id = kwargs.get('id')
    character_id = request.GET.get('character_id')
    project = get_object_or_404(Project, pk=project_id)
    character = get_object_or_404(Character, pk=character_id)
    try:
        sides = Sides.objects.get(
                    Q(project=project) &
                    Q(character=character)
                    )
        # generate pdf filename
        filename = project.title+" "+character.name
        list_string = []
        list_string = filename.split(" ")
        filename = '_'.join(list_string)
        filename = filename+".pdf"
        # create pdf
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        styles = getSampleStyleSheet()
        report = SimpleDocTemplate(buff, rightMargin=72,
                                   leftMargin=72, topMargin=72,
                                   bottomMargin=18)
        report_title = Paragraph("Sides", styles["h1"])
        report.build([report_title])
        scene_1 = Paragraph("Scene 1", styles["h3"])
        scene_1_data = Paragraph(sides.scene_1)
        scene_2 = Paragraph("Scene 2", styles["h3"])
        scene_2_data = Paragraph(sides.scene_2)
        scene_3 = Paragraph("Scene 3", styles["h3"])
        scene_3_data = Paragraph(sides.scene_3)
        report.build([report_title, scene_1, scene_1_data, scene_2,
                      scene_2_data, scene_3, scene_3_data])

        response.write(buff.getvalue())
        buff.close()
        return response



    except Sides.DoesNotExist:
        pass
    return response


class SubmitAuditionAPI(APIView):
    serializer_class = AuditionSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            project_id = data_dict['project']
            character_id = data_dict['character']
            project = get_object_or_404(Project, pk=project_id)
            character = get_object_or_404(Character, pk=character_id)
            audition_obj = Audition()
            audition_obj.project = project
            audition_obj.character = character
            audition_obj.name = data_dict['name']
            audition_obj.user = self.request.user
            location_id = data_dict['location']
            audition_obj.location = get_object_or_404(Location, pk=location_id)
            audition_obj.agent_name = data_dict['agent_name']
            audition_obj.agent_email = data_dict['agent_email']
            try:
                agent_user = CustomUser.objects.get(email=data_dict['agent_email'])
                audition_obj.agent = agent_user
            except CustomUser.DoesNotExist:
                pass
            video_type = data_dict['video_type']
            url = data_dict['video_url']
            audition_obj.video_type = video_type
            try:
                cover_image = request.data['cover_image']
                audition_obj.cover_image = cover_image
            except KeyError:
                raise ParseError('Request has no cover image attached')

            if video_type == 'youtube':
                url_temp = url.split("v=")[1]
                video_url = url_temp.split("&")[0]
                audition_obj.video_url = video_url
            if video_type == 'vimeo':
                if url.startswith('https://vimeo.com/'):
                    video_url = url.split('https://vimeo.com/')[1]
                    audition_obj.video_url = video_url
                if url.startswith('http://vimeo.com/'):
                    video_url = url.split('http://vimeo.com/')[1]
                    audition_obj.video_url = video_url
                if url.startswith('vimeo.com/'):
                    video_url = url.split('vimeo.com/')[1]
                    audition_obj.video_url = video_url
            if video_type == 'facebook':
                audition_obj.video_url = url
            audition_obj.save()

            # update user-project-table
            user_project_obj = UserProject()
            user_project_obj.user = self.request.user
            user_project_obj.project = project
            user_project_obj.relation_type = UserProject.APPLIED
            user_project_obj.audition = audition_obj
            user_project_obj.character = character
            user_project_obj.save()
            # end

            response = {'message': "Audition Submitted",
                        'status': status.HTTP_200_OK}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class AuditionListView(LoginRequiredMixin, TemplateView):
    template_name = 'project/audition-list.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        count_dict = {}
        character_dict = {}
        rating_dict = {}
        audition_rating_dict = {}
        casting_director_rating = 0
        project_id = self.kwargs.get('id')
        project = get_object_or_404(Project, pk=project_id)
        characters = Character.objects.filter(project=project).order_by('created_time')
        audition_list = Audition.objects.filter(project=project)
        casting_director_job = JobType.objects.filter(
                               slug='casting-director'
                               ).first()
        if casting_director_job:
            try:
                casting_director = Team.objects.get(
                                    Q(project=project) &
                                    Q(job_type=casting_director_job)
                                    ).user
                rating_object = UserRatingCombined.objects.filter(
                            Q(user=casting_director) &
                            Q(job_type=casting_director_job)
                        ).first()
                if rating_object:
                    casting_director_rating = rating_object.rating*20
                else:
                    casting_director_rating = 0
            except Team.DoesNotExist:
                casting_director = ""
            context['casting_director'] = casting_director
            context['casting_director_rating'] = casting_director_rating
        try:
            actoractress = JobType.objects.get(slug='actoractress')
        except JobType.DoesNotExist:
            actoractress = ""
        # try:
        #     actress = JobType.objects.get(slug='actress')
        # except JobType.DoesNotExist:
        #     actress = ""

        for audition_obj in audition_list:
            try:
                rating_obj = UserRatingCombined.objects.get(
                                Q(user=audition_obj.user) &
                                Q(job_type=actoractress)
                            )
                rating_dict[audition_obj.user.id] = (rating_obj.rating)*20
            except UserRatingCombined.DoesNotExist:
                rating_dict[audition_obj.user.id] = 0
            try:
                audition_rating_obj = AuditionRatingCombined.objects.get(
                                      audition=audition_obj)
                audition_rating_dict[audition_obj.id] = (audition_rating_obj.rating)*20
            except AuditionRatingCombined.DoesNotExist:
                audition_rating_dict[audition_obj.id] = 0

        for obj in audition_list:
            if obj.character in count_dict:
                count_dict[obj.character] += 1
            else:
                count_dict[obj.character] = 1
            if obj.character in character_dict:
                character_dict[obj.character].append(obj)
            else:
                character_dict[obj.character] = []
                character_dict[obj.character].append(obj)

        context['characters'] = characters
        context['project'] = project
        context['count_dict'] = count_dict
        context['character_dict'] = character_dict
        context['rating_dict'] = rating_dict
        context['audition_rating_dict'] = audition_rating_dict
        return context


class EditSidesView(LoginRequiredMixin, TemplateView):
    template_name = 'project/edit-sides.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('id')
        character_id = self.request.GET.get('character_id')
        project = get_object_or_404(Project, pk=project_id)
        context['project'] = project
        try:
            character = Character.objects.get(
                            Q(project=project) &
                            Q(id=character_id)
                        )
            context['character'] = character
            try:
                sides = Sides.objects.get(
                            Q(project=project) &
                            Q(character=character)
                            )
                context['sides'] = sides
                context['form'] = AddSidesForm(instance=sides)
            except Sides.DoesNotExist:
                context['form'] = AddSidesForm()
        except Character.DoesNotExist:
            pass

        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        data_dict = {}
        json_response = json.dumps(request.POST)
        data_dict = ast.literal_eval(json_response)
        project_id = self.kwargs.get('id')
        character_id = self.request.POST.get('character_id')
        data_dict['project'] = project_id
        data_dict['character'] = character_id
        key = Token.objects.get(user=user).key
        token = 'Token '+key
        user_response = requests.post(
                    'http://127.0.0.1:8000/project/add-sides-api/',
                    data=json.dumps(data_dict),
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
                        self.request, "Failed to update scenes !!")
                    return HttpResponseRedirect(
                        request.META.get('HTTP_REFERER', '/'))
        messages.success(self.request, "Sides updated successfully")
        url = "/project/add-sides/"+str(project_id)+"/?character_id="+str(character_id)
        return HttpResponseRedirect(url)


class AddSceneImagesView(LoginRequiredMixin, TemplateView):
    template_name = 'project/add-scene-images.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('id')
        character_id = self.request.GET.get('character_id')
        scene = self.request.GET.get('scene')
        project = get_object_or_404(Project, pk=project_id)
        context['project'] = project
        try:
            character = Character.objects.get(
                            Q(project=project) &
                            Q(id=character_id)
                        )
            context['character'] = character

            scene = 'scene_'+scene
            scene_image_objs = SceneImages.objects.filter(
                                Q(project=project) &
                                Q(character=character) &
                                Q(scene=scene)
                            ).order_by('created_time')
            context['scene_image_objs'] = scene_image_objs
        except Character.DoesNotExist:
            pass
        return context

    def post(self, request, *args, **kwargs):
        print(self.request.POST)
        scene = self.request.POST.get('scene')
        project_id = self.request.POST.get('project_id')
        character_id = self.request.POST.get('character_id')
        scene_image_obj = SceneImages()
        scene_image_obj.project = get_object_or_404(
                                  Project, pk = project_id)
        scene_image_obj.character = get_object_or_404(
                                    Character, pk = character_id)
        if scene == '1':
            scene_image_obj.scene = SceneImages.SCENE_1
        if scene == '2':
            scene_image_obj.scene = SceneImages.SCENE_2
        if scene == '3':
            scene_image_obj.scene = SceneImages.SCENE_3
        # scene_image_obj.image = 'media/script/project_6.jpg'
        url = "http://localhost:8000/media/script/project_"+project_id+".jpg"
        resp = requests.get(url)
        if resp.status_code != requests.codes.ok:
            pass

        fp = BytesIO()
        fp.write(resp.content)
        file_name = url.split("/")[-1]
        scene_image_obj.image.save(file_name, files.File(fp))
        scene_image_obj.save()

        x = float(self.request.POST.get('x'))
        y = float(self.request.POST.get('y'))
        w = float(self.request.POST.get('width'))
        h = float(self.request.POST.get('height'))

        image = PIL.Image.open(scene_image_obj.image)
        cropped_image = image.crop((x, y, w+x, h+y))
        # resized_image = cropped_image.resize((200, 200), PIL.Image.ANTIALIAS)
        cropped_image.save(scene_image_obj.image.path)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class GenerateSceneImagePDFAPI(APIView):
    serializer_class = SceneImagesSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            print(data_dict)

            project_id = data_dict['project_id']
            character_id = data_dict['character_id']
            scene = data_dict['scene']

            project = get_object_or_404(Project, pk=project_id)
            character = get_object_or_404(Character, pk=character_id)

            scene_image_objs = SceneImages.objects.filter(
                            Q(project=project) &
                            Q(character=character) &
                            Q(scene=scene)
                        ).order_by('created_time')

            pdf = FPDF()
            for img_obj in scene_image_objs:
                img_path = str(img_obj.image.url)[1:]
                cover = PIL.Image.open(img_path)
                width, height = cover.size
                # convert pixel in mm with 1px=0.264583 mm
                width, height = float(width * 0.264583), float(height * 0.264583)
                # given we are working with A4 format size
                pdf_size = {'P': {'w': 210, 'h': 297}, 'L': {'w': 297, 'h': 210}}
                # get page orientation from image size
                orientation = 'P' if width < height else 'L'
                #  make sure image size is not greater than the pdf format size
                width = width if width < pdf_size[orientation]['w'] else pdf_size[orientation]['w']
                height = height if height < pdf_size[orientation]['h'] else pdf_size[orientation]['h']
                pdf.add_page(orientation=orientation)
                pdf.image(img_path, 0, 0, width, height)

            output_path = "media/scene/"+scene+str(project_id)+str(character_id)+".pdf"
            pdf.output(output_path, "F")

            # Save PDF to db
            url = "http://localhost:8000/"+output_path
            resp = requests.get(url)
            if resp.status_code != requests.codes.ok:
                pass
            fp = BytesIO()
            fp.write(resp.content)
            file_name = url

            try:
                sides_obj = Sides.objects.get(
                            Q(project=project) &
                            Q(character=character)
                            )
                if scene == 'scene_1':
                    sides_obj.scene_1 = ""
                    sides_obj.scene_1_pdf.save(file_name, files.File(fp))
                    msg = "Scene 1 updated"
                if scene == 'scene_2':
                    sides_obj.scene_2 = ""
                    sides_obj.scene_2_pdf.save(file_name, files.File(fp))
                    msg = "Scene 2 updated"
                if scene == 'scene_3':
                    sides_obj.scene_3 = ""
                    sides_obj.scene_3_pdf.save(file_name, files.File(fp))
                    msg = "Scene 3 updated"
                sides_obj.save()
            except Sides.DoesNotExist:
                sides_obj = Sides()
                sides_obj.project = project
                sides_obj.character = character
                if scene == 'scene_1':
                    sides_obj.scene_1 = ""
                    sides_obj.scene_1_pdf.save(file_name, files.File(fp))
                    msg = "Scene 1 updated"
                if scene == 'scene_2':
                    sides_obj.scene_2 = ""
                    sides_obj.scene_2_pdf.save(file_name, files.File(fp))
                    msg = "Scene 2 updated"
                if scene == 'scene_3':
                    sides_obj.scene_3 = ""
                    sides_obj.scene_3_pdf.save(file_name, files.File(fp))
                    msg = "Scene 3 updated"
                sides_obj.save()

            messages.success(self.request, msg)
            response = {'message': "Scene Pdf uploaded",
                        'status': status.HTTP_200_OK}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class ScriptPasswordCheckAPI(APIView):
    serializer_class = PasswordSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            password = data_dict['password']
            project_id = data_dict['project_id']
            project = get_object_or_404(Project, pk=project_id)
            # if check_password(password, project.script_password):
            if password == project.script_password:
                response = {'message': "Password Verified",
                            'url': project.script.url,
                            'status': status.HTTP_200_OK}
            else:
                response = {'errors': 'Wrong Password', 'status':
                            status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class CastAuditionPasswordCheckAPI(APIView):
    serializer_class = PasswordSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            password = data_dict['password']
            project_id = data_dict['project_id']
            project = get_object_or_404(Project, pk=project_id)
            # if check_password(password, project.cast_audition_password):
            if password == project.cast_audition_password:
                response = {'message': "Password Verified",
                            'status': status.HTTP_200_OK}
            else:
                response = {'errors': 'Wrong Password', 'status':
                            status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class TeamSelectPasswordCheckAPI(APIView):
    serializer_class = PasswordSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            password = data_dict['password']
            project_id = data_dict['project_id']
            project = get_object_or_404(Project, pk=project_id)
            # if check_password(password, project.team_select_password):
            if password == project.team_select_password:
                response = {'message': "Password Verified",
                            'status': status.HTTP_200_OK}
            else:
                response = {'errors': 'Wrong Password', 'status':
                            status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class SaveProjectLoglineAPI(APIView):
    serializer_class = ProjectLoglineSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            print("data_dict----------",data_dict)
            id = data_dict['project_id']
            project = get_object_or_404(Project, pk=id)
            if 'logline' in data_dict and data_dict['logline'] is not None:
                project.logline = data_dict['logline']
            if 'project_info' in data_dict and data_dict['project_info'] is not None:
                project.project_info = data_dict['project_info']
            project.save()
            response = {'message': "Logline and project info updated",
                        'status': status.HTTP_200_OK}
            messages.success(self.request, 'Project Info updated')
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class ListProjectTrackersAPI(APIView):
    serializer_class = TrackProjectSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data_dict = serializer.data
            project = get_object_or_404(Project, pk=data_dict['project_id'])
            try:
                trackers_dict = {}
                track_obj = ProjectTracking.objects.get(project=project)
                trackers_list = track_obj.tracked_by.all()

                for user in trackers_list:
                    trackers_dict[user.id] = UserSerializer(user).data

                response = {'Trackers': trackers_dict,
                            'status': status.HTTP_200_OK}
            except ProjectTracking.DoesNotExist:
                response = {'Message': "Trackers list is empty", 'status':
                            status.HTTP_200_OK}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class TrackProjectAPI(APIView):
    serializer_class = TrackProjectSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            project_id = data_dict['project_id']
            project = get_object_or_404(Project, pk=project_id)
            track_by_user = self.request.user

            try:
                track_obj = ProjectTracking.objects.get(project=project)
                trackers_list = track_obj.tracked_by.all()
                if track_by_user in trackers_list:
                    response = {'message': "You are already tracking this user",
                                'status': status.HTTP_400_BAD_REQUEST,
                                'track_status': 'tracking'
                                }
                    return Response(response)
                track_obj.tracked_by.add(track_by_user.id)

            except ProjectTracking.DoesNotExist:
                track_obj = ProjectTracking()
                track_obj.project = project
                track_obj.save()
                track_obj.tracked_by.add(track_by_user.id)

            # update notification table
            notification = UserNotification()
            notification.user = project.creator
            notification.notification_type = UserNotification.PROJECT_TRACKING
            notification.from_user = track_by_user
            notification.project = project
            notification.message = track_by_user.get_full_name()+" started tracking your project "+project.title
            notification.save()

            # send notification
            room_name = "user_"+str(track_obj.project.creator.id)
            notification_msg = {
                    'type': 'send_project_tracking_notification',
                    'message': str(notification.message),
                    'track_by_user_id': str(self.request.user.id),
                    "event": "PROJECT_TRACKING"
                }
            notify(room_name, notification_msg)

            msg = "Started Tracking " + project.title
            response = {'message': msg,
                        'status': status.HTTP_200_OK,
                        'track_status': 'tracking'}

        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class GetProjectTrackingNotificationAjaxView(View, JSONResponseMixin):
    template_name = 'project/get-single-notification.html'

    def get(self, *args, **kwargs):
        context = dict()
        user = self.request.user
        id = self.request.GET.get('from_user')
        message = self.request.GET.get('message')
        from_user = CustomUser.objects.get(id=id)
        notification_id = UserNotification.objects.filter(
                            Q(user=user) &
                            Q(from_user=from_user) &
                            Q(notification_type=UserNotification.PROJECT_TRACKING)
                            ).order_by('-created_time').first().id
        notification_html = render_to_string(
                                'project/get-single-notification.html',
                                {'from_user': from_user,
                                 'message':message,
                                 'notification_id':notification_id,
                                })
        context['notification_html'] = notification_html
        return self.render_json_response(context)


class UnTrackProjectAPI(APIView):
    serializer_class = TrackProjectSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            project_id = data_dict['project_id']
            project = get_object_or_404(Project, pk=project_id)
            track_by_user = self.request.user

            try:
                track_obj = ProjectTracking.objects.get(project=project)
                track_obj.tracked_by.remove(track_by_user.id)
                # remove from notification table
                try:
                    notification = UserNotification.objects.get(
                        Q(project=project) &
                        Q(from_user=track_by_user) &
                        Q(notification_type=UserNotification.PROJECT_TRACKING)
                        )
                    notification.delete()
                except UserNotification.DoesNotExist:
                    pass
            except ProjectTracking.DoesNotExist:
                response = {'errors': "invalid id",
                            'status': status.HTTP_400_BAD_REQUEST}
            msg = "Stopped Tracking " + project.title
            response = {'message': msg,
                        'status': status.HTTP_200_OK,
                        'track_status':'not_tracking'}

        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class CastVideoAuditionView(LoginRequiredMixin, TemplateView):
    template_name = 'project/cast-video-audition.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        audition_id = self.kwargs.get('id')
        audition = get_object_or_404(Audition, pk=audition_id)
        context['audition'] = audition

        try:
            casting_director = JobType.objects.get(slug='casting-director')
            casting_directors = Team.objects.filter(
                    Q(project=audition.project) &
                    Q(job_type=casting_director)
                    )
        except JobType.DoesNotExist:
            casting_director = ""
            casting_directors = []
        try:
            director = JobType.objects.get(slug='director')
            directors = Team.objects.filter(
                    Q(project=audition.project) &
                    Q(job_type=director)
                    )
        except JobType.DoesNotExist:
            director = ""
            directors = []
        try:
            producer = JobType.objects.get(slug='producer')
            producers = Team.objects.filter(
                    Q(project=audition.project) &
                    Q(job_type=producer)
                    )
        except JobType.DoesNotExist:
            producer = ""
            producers = []
        try:
            writer = JobType.objects.get(slug='writer')
            writers = Team.objects.filter(
                        Q(project=audition.project) &
                        Q(job_type=writer)
                        )
        except JobType.DoesNotExist:
            writer = ""
            writers = []
        try:
            actoractress = JobType.objects.get(slug='actoractress')
        except JobType.DoesNotExist:
            actoractress = ""
        # try:
        #     actress = JobType.objects.get(slug='actress')
        # except JobType.DoesNotExist:
        #     actress = ""

        context['casting_directors'] = casting_directors
        context['directors'] = directors
        context['producers'] = producers
        context['writers'] = writers
        try:
            audition_user_rating = UserRatingCombined.objects.get(
                                    Q(user=audition.user) &
                                    Q(job_type=actoractress)
                                )
            audition_user_rating = audition_user_rating.rating*20
        except UserRatingCombined.DoesNotExist:
            audition_user_rating = 0
        context['audition_user_rating'] = audition_user_rating

        rating_dict = {}
        audition_user_ratings = AuditionRating.objects.filter(
                                    audition=audition)
        for obj in audition_user_ratings:
            rating_dict[obj.team_member] = obj.rating
        context['rating_dict'] = rating_dict
        context['audition_user_ratings'] = audition_user_ratings
        return context


class RateAuditionAPI(APIView):
    serializer_class = RateAuditionSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            audition_id = data_dict['audition']
            team_member_id = data_dict['team_member']
            rating = data_dict['rating']
            if 'review' in data_dict:
                review = data_dict['review']
            else:
                review = ""
            try:
                team_member = Team.objects.get(pk=team_member_id)
                try:
                    audition = Audition.objects.get(pk=audition_id)
                    try:
                        audition_rating_obj = AuditionRating.objects.get(
                                            Q(audition=audition) &
                                            Q(team_member=team_member)
                                            )
                        audition_rating_obj.rating = rating
                        audition_rating_obj.review = review
                        audition_rating_obj.save()
                    except AuditionRating.DoesNotExist:
                        audition_rating_obj = AuditionRating()
                        audition_rating_obj.audition = audition
                        audition_rating_obj.team_member = team_member
                        audition_rating_obj.rating = rating
                        audition_rating_obj.review = review
                        audition_rating_obj.save()

                    # update combined rating
                    try:
                        audition_rating_combined = AuditionRatingCombined.objects.get(
                                                   audition=audition)
                        count = AuditionRating.objects.filter(
                                audition=audition).count()
                        aggregate_rating = AuditionRating.objects.filter(
                                            audition=audition).aggregate(Sum('rating'))
                        rating_sum = aggregate_rating['rating__sum']
                        new_rating = rating_sum/count
                        audition_rating_combined.rating = new_rating
                        audition_rating_combined.save()
                    except AuditionRatingCombined.DoesNotExist:
                        audition_rating_combined = AuditionRatingCombined()
                        audition_rating_combined.audition = audition
                        audition_rating_combined.rating = rating
                        audition_rating_combined.save()


                    response = {'message': "Rating updated",
                                'status': status.HTTP_200_OK}
                    messages.success(self.request, "Rated Successfully")
                except Audition.DoesNotExist:
                    response = {'errors': "Invalid Audition ID", 'status':
                                status.HTTP_400_BAD_REQUEST}
            except Team.DoesNotExist:
                response = {'errors': "Invalid team member", 'status':
                            status.HTTP_400_BAD_REQUEST}

        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class UpdateAuditionStatusAPI(APIView):
    serializer_class = AuditionStatusSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            audition_id = data_dict['audition']
            audition_status = data_dict['status']
            try:
                audition = Audition.objects.get(pk=audition_id)
                audition.audition_status = audition_status
                audition.status_update_date = timezone.now()
                audition.save()
                response = {'message': "Audition status updated",
                            'status': status.HTTP_200_OK}

                if audition_status == 'attached':
                    character_obj = get_object_or_404(
                                    Character, pk=audition.character.id)
                    character_obj.attached_user = audition.user
                    character_obj.attached_user_name = audition.user.get_full_name()
                    character_obj.save()

                    # add to user-project table
                    try:
                        user_project_obj = UserProject.objects.get(
                                            Q(user=audition.user) &
                                            Q(project=audition.project) &
                                            Q(character=audition.character) &
                                            Q(relation_type=UserProject.ATTACHED)
                                            )
                    except UserProject.DoesNotExist:
                        user_project_obj = UserProject()
                        user_project_obj.user = audition.user
                        user_project_obj.project = audition.project
                        user_project_obj.character = audition.character
                        user_project_obj.relation_type = UserProject.ATTACHED
                        user_project_obj.save()
                    # end

                    # add to team
                    team_obj = Team()
                    team_obj.user = audition.user
                    team_obj.project = audition.project
                    team_obj.job_type = JobType.objects.get(slug='actoractress')
                    team_obj.save()
                    # end

                    # All other audition's status changed to passed
                    all_auditions = Audition.objects.filter(
                                    Q(character=character_obj) &
                                    ~Q(audition_status=Audition.PASSED)
                                    ).exclude(pk=audition.id)
                    for obj in all_auditions:
                        obj.audition_status = Audition.PASSED
                        obj.status_update_date = timezone.now()
                        obj.save()
                        #update notification table- for removed user
                        notification = UserNotification()
                        notification.user = obj.user
                        notification.project = character_obj.project
                        notification.notification_type = UserNotification.AUDITION_STATUS
                        notification.message = "Sorry!! Your audition for "+character_obj.project.title+" has been passed."
                        notification.save()
                        # send notification- for removed user
                        room_name = "user_"+str(obj.user.id)
                        notification_msg = {
                                'type': 'send_audition_status_notification',
                                'message': str(notification.message),
                                'from': character_obj.project.title,
                                "event": "AUDITION_STATUS"
                            }
                        notify(room_name, notification_msg)
                        # end notification section
                    # end

                    msg = "Attached "+audition.name+" to "+audition.project.title
                else:
                    msg = "Audition status updated to "+audition.get_status_display()

                #update notification table
                notification = UserNotification()
                notification.user = audition.user
                notification.project = audition.project
                notification.notification_type = UserNotification.AUDITION_STATUS
                if audition.audition_status == 'attached':
                    notification.message = "Congratulations!! You have been attached to project "+audition.project.title
                elif audition.audition_status == 'callback':
                    notification.message = "Your audition for "+audition.project.title+" has been sent to chemistry room."
                elif audition.audition_status == 'passed':
                    notification.message = "Sorry!! Your audition for "+audition.project.title+" has been passed."
                notification.save()
                # send notification
                room_name = "user_"+str(audition.user.id)
                notification_msg = {
                        'type': 'send_audition_status_notification',
                        'message': str(notification.message),
                        'from': audition.project.title,
                        "event": "AUDITION_STATUS"
                    }
                notify(room_name, notification_msg)
                # end notification section

                messages.success(self.request, msg)
            except Audition.DoesNotExist:
                response = {'errors': "Invalid Audition ID", 'status':
                            status.HTTP_400_BAD_REQUEST}
                messages.warning(self.request, "Invalid audition!!")
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors,
                        'status': status.HTTP_400_BAD_REQUEST}
        return Response(response)


class ChemistryRoomView(LoginRequiredMixin, TemplateView):
    template_name = 'project/chemistry-room.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('id')
        project = get_object_or_404(Project, pk=project_id)
        audition_list = Audition.objects.filter(
                        Q(project=project) &
                        Q(audition_status=Audition.CALLBACK)
                        )
        audition_dict = {}

        context['all_audition'] = audition_list
        for audition in audition_list:
            if audition.character in audition_dict:
                audition_dict[audition.character].append(audition)
            else:
                audition_dict[audition.character] = []
                audition_dict[audition.character].append(audition)

        try:
            actoractress = JobType.objects.get(slug='actoractress')
        except JobType.DoesNotExist:
            actoractress = ""

        rating_dict = {}
        audition_rating_dict = {}
        for audition_obj in audition_list:
            try:
                rating_obj = UserRatingCombined.objects.get(
                                Q(user=audition_obj.user) &
                                Q(job_type=actoractress)
                            )
                rating_dict[audition_obj.user.id] = (rating_obj.rating)*20
            except UserRatingCombined.DoesNotExist:
                rating_dict[audition_obj.user.id] = 0
            try:
                audition_rating_obj = AuditionRatingCombined.objects.get(
                                      audition=audition_obj)
                audition_rating_dict[audition_obj.id] = (audition_rating_obj.rating)*20
            except AuditionRatingCombined.DoesNotExist:
                audition_rating_dict[audition_obj.id] = 0

        context['project'] = project
        context['audition_dict'] = audition_dict
        context['audition_list'] = audition_list
        context['rating_dict'] = rating_dict
        context['audition_rating_dict'] = audition_rating_dict
        return context


class ProjectRatingAPI(APIView):
    serializer_class = ProjectRatingSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data_dict = serializer.data
            user = self.request.user
            project_id = data_dict['project']
            rating =  data_dict['rating']
            reason =  data_dict['reason']
            rating_obj = ProjectRating()
            project = get_object_or_404(Project, pk=project_id)
            rating_obj.project = project
            rating_obj.rating = rating
            rating_obj.reason = reason
            rating_obj.rated_by = user
            rating_obj.save()

            # update combined project rating
            ratings = ProjectRating.objects.filter(project=project_id)
            combined_rating = 0
            for item in ratings:
                combined_rating += item.rating
                print("combined_rating", combined_rating)
            combined_rating = combined_rating / len(ratings)
            project.rating = combined_rating*20
            project.save()

            #update notification table - video rating
            notification = UserNotification()
            notification.user = project.creator
            notification.from_user = user
            notification.project = project
            notification.rating = rating
            notification.notification_type = UserNotification.PROJECT_RATING
            notification.message = user.get_full_name()+" rated your project "+project.title+" as "+str(rating)+" stars"
            notification.save()
            # send notification - video rating
            room_name = "user_"+str(project.creator.id)
            notification_msg = {
                    'type': 'send_project_rating_notification',
                    'message': str(notification.message),
                    'from': str(user.id),
                    "event": "PROJECT_RATING"
                }
            notify(room_name, notification_msg)
            # end notification section

            msg = "Rated  "+project.title +" by "+str(rating_obj.rating)+" stars."
            messages.success(self.request, msg)
            response = {'message': "Rating success",
                        'status': status.HTTP_201_CREATED}

        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class CastAttachRemoveView(LoginRequiredMixin, TemplateView):
    template_name = 'project/cast-attach-remove.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('id')
        project = get_object_or_404(Project, pk=project_id)
        characters = Character.objects.filter(project=project).order_by('created_time')
        context['project'] = project
        context['characters'] = characters

        try:
            actoractress = JobType.objects.get(slug='actoractress')
        except JobType.DoesNotExist:
            actoractress = ""

        rating_dict = {}
        for character in characters:
            if character.attached_user:
                try:
                    rating_obj = UserRatingCombined.objects.get(
                                    Q(user=character.attached_user) &
                                    Q(job_type=actoractress)
                                )
                    rating_dict[character.attached_user.id] = (rating_obj.rating)*20
                except UserRatingCombined.DoesNotExist:
                    rating_dict[character.attached_user.id] = 0
        context['rating_dict'] = rating_dict
        users = CustomUser.objects.all()
        context['users'] = users
        return context


class RemoveAttachedCastAPI(APIView):
    serializer_class = RemoveCastSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        old_user = None
        if serializer.is_valid():
            data_dict = serializer.data
            character_id = data_dict['character']
            try:
                character = Character.objects.get(id=character_id)
                if character.attached_user or character.attached_user_name:
                    if character.attached_user:
                        old_user = character.attached_user
                        msg = "Removed "+character.attached_user.get_full_name()
                    elif character.attached_user_name:
                        msg = "Removed "+character.attached_user_name
                    character.attached_user = None
                    character.attached_user_name = None
                    character.save()
                    response = {'message': msg,
                                'status': status.HTTP_200_OK}
                    messages.success(self.request, msg)

                    if old_user:
                        audition_obj = Audition.objects.filter(
                                       Q(character=character) &
                                       Q(user=old_user)
                                        ).first()
                        if audition_obj:
                            audition_obj.audition_status = Audition.PASSED
                            audition_obj.status_update_date = timezone.now()
                            audition_obj.save()

                        # add to user-project table
                        try:
                            user_project_obj = UserProject.objects.get(
                                                Q(user=old_user) &
                                                Q(project=character.project) &
                                                Q(character=character) &
                                                Q(relation_type=UserProject.ATTACHED)
                                                )
                            user_project_obj.delete()
                        except UserProject.DoesNotExist:
                            pass
                        # end

                        # remove from team
                        try:
                            actor_actress = JobType.objects.get(slug='actoractress')
                            team_obj = Team.objects.filter(
                                        Q(user = old_user) &
                                        Q(project = character.project) &
                                        Q(job_type = actor_actress))
                            team_obj.delete()
                        except JobType.DoesNotExist:
                            pass
                        # end

                        #update notification table- for removed user
                        notification = UserNotification()
                        notification.user = old_user
                        notification.project = character.project
                        notification.notification_type = UserNotification.AUDITION_STATUS
                        notification.message = "Sorry!! You have been removed from project "+character.project.title
                        notification.save()
                        # send notification- for removed user
                        room_name = "user_"+str(old_user.id)
                        notification_msg = {
                                'type': 'send_audition_status_notification',
                                'message': str(notification.message),
                                'from': character.project.title,
                                "event": "AUDITION_STATUS"
                            }
                        notify(room_name, notification_msg)
                        # end notification section
                else:
                    response = {'message': "No users attached",
                                'status': status.HTTP_200_OK}
            except Character.DoesNotExist:
                response = {'errors': "Invalid ID", 'status':
                            status.HTTP_400_BAD_REQUEST}

        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class ReplaceAttachedCastAPI(APIView):
    serializer_class = ReplaceCastSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            user_id = None
            old_user = None
            name = ""
            data_dict = serializer.data
            character_id = data_dict['character']
            if 'user' in data_dict:
                user_id = data_dict['user']
            if 'name' in data_dict:
                name = data_dict['name']
            try:
                character = Character.objects.get(id=character_id)
                all_auditions = Audition.objects.filter(
                                Q(character=character) &
                                ~Q(audition_status=Audition.PASSED)
                                )
                if user_id:
                    try:
                        user = CustomUser.objects.get(id=user_id)
                        attached_user_audition = Audition.objects.filter(
                                                    Q(character=character) &
                                                    Q(user=user)).first()

                        if attached_user_audition:
                            if character.attached_user:
                                old_user = character.attached_user
                            character.attached_user = user
                            character.attached_user_name = user.get_full_name()
                            character.save()
                            response = {'message': "Replaced user",
                                        'status': status.HTTP_200_OK}
                            msg = "Attached "+user.get_full_name()+" to character-"+character.name
                            messages.success(self.request, msg)

                            attached_user_audition.audition_status = Audition.ATTACHED
                            attached_user_audition.status_update_date = timezone.now()
                            attached_user_audition.save()

                            # add to user-project table
                            try:
                                user_project_obj = UserProject.objects.get(
                                                        Q(user=attached_user_audition.user) &
                                                        Q(project=attached_user_audition.project) &
                                                        Q(character=attached_user_audition.character) &
                                                        Q(relation_type=UserProject.ATTACHED)
                                                    )
                            except UserProject.DoesNotExist:
                                user_project_obj = UserProject()
                                user_project_obj.user = attached_user_audition.user
                                user_project_obj.project = attached_user_audition.project
                                user_project_obj.character = attached_user_audition.character
                                user_project_obj.relation_type = UserProject.ATTACHED
                                user_project_obj.save()
                            # end

                            # add to team
                            team_obj = Team()
                            team_obj.user = attached_user_audition.user
                            team_obj.project = attached_user_audition.project
                            team_obj.job_type = JobType.objects.get(slug='actoractress')
                            team_obj.save()
                            # end

                            all_auditions = all_auditions.exclude(
                                            pk=attached_user_audition.id)


                            if old_user:
                                #update notification table- for removed user
                                notification = UserNotification()
                                notification.user = old_user
                                notification.project = character.project
                                notification.notification_type = UserNotification.AUDITION_STATUS
                                notification.message = "Sorry!! You have been removed from project "+character.project.title
                                notification.save()
                                # send notification- for removed user
                                room_name = "user_"+str(old_user.id)
                                notification_msg = {
                                        'type': 'send_audition_status_notification',
                                        'message': str(notification.message),
                                        'from': character.project.title,
                                        "event": "AUDITION_STATUS"
                                    }
                                notify(room_name, notification_msg)
                                # end notification section

                            #update notification table
                            notification = UserNotification()
                            notification.user = user
                            notification.project = character.project
                            notification.notification_type = UserNotification.AUDITION_STATUS
                            notification.message = "Congratulations!! You have been attached to project "+character.project.title
                            notification.save()
                            # send notification
                            room_name = "user_"+str(character.attached_user.id)
                            notification_msg = {
                                    'type': 'send_audition_status_notification',
                                    'message': str(notification.message),
                                    'from': character.project.title,
                                    "event": "AUDITION_STATUS"
                                }
                            notify(room_name, notification_msg)
                            # end notification section
                        else:
                            if character.attached_user:
                                old_user = character.attached_user
                            character.requested_user = user
                            character.attached_user = None
                            character.attached_user_name = ""
                            character.save()

                            #update notification table
                            notification = UserNotification()
                            notification.user = user
                            notification.project = character.project
                            notification.character = character
                            notification.notification_type = UserNotification.CAST_ATTACH_REQUEST
                            notification.message = str(character.project.creator)+" wants to attach you to character <b>"+str(character.name)+"</b> to his project <b>"+str(character.project.title)+"</b>"
                            notification.save()
                            # send attach request notification
                            room_name = "user_"+str(character.requested_user.id)
                            notification_msg = {
                                    'type': 'send_cast_attach_request_notification',
                                    'message': str(notification.message),
                                    'from': character.project.creator,
                                    "event": "CAST_ATTACH_REQUEST"
                                }
                            notify(room_name, notification_msg)
                            # end notification section

                            response = {'message': "Request Sent",
                                        'status': status.HTTP_200_OK}
                            msg = "Request sent to "+user.get_full_name()
                            messages.success(self.request, msg)

                            if old_user:
                                #update notification table- for removed user
                                notification = UserNotification()
                                notification.user = old_user
                                notification.project = character.project
                                notification.notification_type = UserNotification.AUDITION_STATUS
                                notification.message = "Sorry!! You have been removed from project "+character.project.title
                                notification.save()
                                # send notification- for removed user
                                room_name = "user_"+str(old_user.id)
                                notification_msg = {
                                        'type': 'send_audition_status_notification',
                                        'message': str(notification.message),
                                        'from': character.project.title,
                                        "event": "AUDITION_STATUS"
                                    }
                                notify(room_name, notification_msg)
                                # end notification section

                    except CustomUser.DoesNotExist:
                        response = {'errors': "Invalid user id", 'status':
                                    status.HTTP_400_BAD_REQUEST}
                if name:
                    character.attached_user = None
                    character.attached_user_name = name
                    character.save()
                    response = {'message': "Replaced user",
                                'status': status.HTTP_200_OK}
                    msg = "Attached "+name+" to character-"+character.name
                    messages.success(self.request, msg)

                # All other audition's status changed to passed
                for obj in all_auditions:
                    obj.audition_status = Audition.PASSED
                    obj.status_update_date = timezone.now()
                    obj.save()
                    #update notification table- for removed user
                    notification = UserNotification()
                    notification.user = obj.user
                    notification.project = character.project
                    notification.notification_type = UserNotification.AUDITION_STATUS
                    notification.message = "Sorry!! Your audition for "+character.project.title+" has been passed."
                    notification.save()
                    # send notification- for removed user
                    room_name = "user_"+str(obj.user.id)
                    notification_msg = {
                            'type': 'send_audition_status_notification',
                            'message': str(notification.message),
                            'from': character.project.title,
                            "event": "AUDITION_STATUS"
                        }
                    notify(room_name, notification_msg)
                    # end notification section


            except Character.DoesNotExist:
                response = {'errors': "Invalid ID", 'status':
                            status.HTTP_400_BAD_REQUEST}

        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class CommentAPI(APIView):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            print("data_dict", data_dict)
            try:
                project = Project.objects.get(id=data_dict['project'])
                if 'reply_to' in data_dict:
                    try:
                        reply_to = Comment.objects.get(pk=data_dict['reply_to'])
                        comment_obj = Comment()
                        comment_obj.user = self.request.user
                        comment_obj.comment_txt = data_dict['comment_txt']
                        comment_obj.project = project
                        comment_obj.reply_to = reply_to
                        comment_obj.save()
                        response = {'message': "Comment posted",
                                    'id':comment_obj.id,
                                    'status': status.HTTP_200_OK}

                        # send mention notifications
                        if 'mentioned_users' in data_dict:
                            user_list = json.loads(data_dict['mentioned_users'])
                            for user_id in user_list:
                                try:
                                    user_obj  = CustomUser.objects.get(pk=user_id)
                                    #update notification table
                                    notification = UserNotification()
                                    notification.user = user_obj
                                    notification.notification_type = UserNotification.COMMENTS_MENTION
                                    notification.from_user = self.request.user
                                    notification.project = project
                                    notification.message = self.request.user.get_full_name()+" mentioned you in "+project.title+"'s post."
                                    notification.save()
                                    # send notification
                                    room_name = "user_"+str(user_obj.id)
                                    notification_msg = {
                                            'type': 'send_comments_mention_notification',
                                            'message': str(notification.message),
                                            'from': str(self.request.user.id),
                                            "event": "COMMENTS_MENTION"
                                        }
                                    notify(room_name, notification_msg)
                                    # end notification section
                                except CustomUser.DoesNotExist:
                                    pass


                        #send reply notification
                        #update notification table
                        notification = UserNotification()
                        notification.user = reply_to.user
                        notification.notification_type = UserNotification.COMMENTS_REPLY
                        notification.from_user = self.request.user
                        notification.project = project
                        notification.message = self.request.user.get_full_name()+" replied to your comment on your project "+project.title+"'s video."
                        notification.save()
                        # send notification
                        room_name = "user_"+str(reply_to.user.id)
                        notification_msg = {
                                'type': 'send_comments_reply_notification',
                                'message': str(notification.message),
                                'from': str(self.request.user.id),
                                "event": "COMMENTS_REPLY"
                            }
                        notify(room_name, notification_msg)
                        # end notification section

                        messages.success(self.request, "Reply posted.")

                    except Comment.DoesNotExist:
                        response = {'errors': 'Invalid reply_to field', 'status':
                                     status.HTTP_400_BAD_REQUEST}
                else:
                    comment_obj = Comment()
                    comment_obj.user = self.request.user
                    comment_obj.comment_txt = data_dict['comment_txt']
                    comment_obj.project = project
                    comment_obj.reply_to = None
                    comment_obj.save()
                    if 'mentioned_users' in data_dict:
                        user_list = json.loads(data_dict['mentioned_users'])
                        for user_id in user_list:
                            try:
                                user_obj  = CustomUser.objects.get(pk=user_id)
                                #update notification table
                                notification = UserNotification()
                                notification.user = user_obj
                                notification.notification_type = UserNotification.COMMENTS_MENTION
                                notification.from_user = self.request.user
                                notification.project = project
                                notification.message = self.request.user.get_full_name()+" mentioned you in "+project.title+"'s post."
                                notification.save()
                                # send notification
                                room_name = "user_"+str(user_obj.id)
                                notification_msg = {
                                        'type': 'send_comments_mention_notification',
                                        'message': str(notification.message),
                                        'from': str(self.request.user.id),
                                        "event": "COMMENTS_MENTION"
                                    }
                                notify(room_name, notification_msg)
                                # end notification section
                            except CustomUser.DoesNotExist:
                                pass
                    response = {'message': "Comment posted",
                                'id':comment_obj.id,
                                'status': status.HTTP_200_OK}
                    messages.success(self.request, "Comment posted.")

                #send comment notification to project creator
                if self.request.user != project.creator:
                    #update notification table
                    notification = UserNotification()
                    notification.user = project.creator
                    notification.notification_type = UserNotification.COMMENTS
                    notification.from_user = self.request.user
                    notification.project = project
                    notification.message = self.request.user.get_full_name()+" commented on your project "+project.title+"'s video."
                    notification.save()
                    # send notification
                    room_name = "user_"+str(project.creator.id)
                    notification_msg = {
                            'type': 'send_comments_notification',
                            'message': str(notification.message),
                            'from': str(self.request.user.id),
                            "event": "COMMENTS"
                        }
                    notify(room_name, notification_msg)
                    # end notification section


            except Project.DoesNotExist:
                response = {'errors': 'Invalid project ID', 'status':
                            status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class DeleteCommentAPI(APIView):
    serializer_class = DeleteCommentSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            id = data_dict['comment_id']
            try:
                comment_obj = Comment.objects.get(pk=id)
                comment_obj.delete()
                response = {'message': "Comment deleted",
                            'status': status.HTTP_200_OK}
            except Comment.DoesNotExist:
                response = {'errors': "Invalid id", 'status':
                            status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class DeleteSceneImageAPI(APIView):
    serializer_class = SceneImageSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            id = data_dict['id']
            try:
                scene_image_obj = SceneImages.objects.get(pk=id)
                scene_image_obj.delete()
                response = {'message': "Scene Image deleted",
                            'status': status.HTTP_200_OK}
            except SceneImages.DoesNotExist:
                response = {'errors': "Invalid id", 'status':
                            status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class GetCommentsMentionNotificationAjaxView(View, JSONResponseMixin):
    template_name = 'project/comment_notification.html'

    def get(self, *args, **kwargs):
        context = dict()
        notification = UserNotification.objects.filter(
                            Q(user=self.request.user) &
                            Q(notification_type=UserNotification.COMMENTS_MENTION)
                            ).order_by('-created_time').first()
        notification_html = render_to_string(
                                'project/comment_notification.html',
                                {'notification': notification
                                })
        context['notification_html'] = notification_html
        return self.render_json_response(context)


class GetCommentsNotificationAjaxView(View, JSONResponseMixin):
    template_name = 'project/comment_notification.html'

    def get(self, *args, **kwargs):
        context = dict()
        notification = UserNotification.objects.filter(
                            Q(user=self.request.user) &
                            Q(notification_type=UserNotification.COMMENTS)
                            ).order_by('-created_time').first()
        notification_html = render_to_string(
                                'project/comment_notification.html',
                                {'notification': notification
                                })
        context['notification_html'] = notification_html
        return self.render_json_response(context)


class GetCommentsReplyNotificationAjaxView(View, JSONResponseMixin):
    template_name = 'project/comment_notification.html'

    def get(self, *args, **kwargs):
        context = dict()
        notification = UserNotification.objects.filter(
                            Q(user=self.request.user) &
                            Q(notification_type=UserNotification.COMMENTS_REPLY)
                            ).order_by('-created_time').first()
        notification_html = render_to_string(
                                'project/comment_notification.html',
                                {'notification': notification
                                })
        context['notification_html'] = notification_html
        return self.render_json_response(context)


class PdfToImageAPI(APIView):
    serializer_class = PdfToImageSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            path = data_dict['path']
            project_id = data_dict['project_id']
            page_no = int(data_dict['page_no'])
            if page_no>0:
                page_no = page_no-1
            print("page_no: ", page_no)
            pdffile = path
            doc = fitz.open(path)
            page = doc.loadPage(page_no)  # number of page

            zoom = 2    # zoom factor
            mat = fitz.Matrix(zoom, zoom)
            pix = page.getPixmap(matrix = mat)

            # pix = page.getPixmap()
            output = 'media/script/project_{0}.jpg'.format(str(project_id))
            pix.writePNG(output)


            response = {'message': "Image generated",
                        'image_path': output,
                        'status': status.HTTP_200_OK}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class CancelCastAttachRequestAPI(APIView):
    serializer_class = CancelCastRequestSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            character_id = data_dict['character_id']

            try:
                character = Character.objects.get(pk=character_id)
                notification_obj =UserNotification.objects.filter(
                                    Q(user = character.requested_user) &
                                    Q(character = character) &
                                    Q(notification_type = UserNotification.CAST_ATTACH_REQUEST)
                                )
                notification_obj.delete()
                character.requested_user = None
                character.save()
                if data_dict['type'] == 'decline':
                    # update notification table
                    notification = UserNotification()
                    notification.user = character.project.creator
                    notification.from_user = self.request.user
                    notification.project = character.project
                    notification.notification_type = UserNotification.CAST_ATTACH_RESPONSE
                    notification.message = self.request.user.get_full_name()+" declined your attach request for character <b>"+character.name+"</b> of the project <b>"+str(character.project.title)+"</b>"
                    notification.character = character
                    notification.save()
                    # send notification to project creator
                    room_name = "user_"+str(character.project.creator.id)
                    notification_msg = {
                            'type': 'send_cast_attach_response_notification',
                            'message': str(notification.message),
                            'from': notification.from_user.get_full_name(),
                            "event": "CAST_ATTACH_RESPONSE"
                        }
                    notify(room_name, notification_msg)
                    # end notification section
                response = {'message': "Cast Attach Request Removed",
                            'character': character.name,
                            'project': character.project.title,
                            'status': status.HTTP_200_OK}
            except Character.DoesNotExist:
                response = {'errors': 'Invalid ID', 'status':
                             status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class AcceptCastAttachRequestAPI(APIView):
    serializer_class = CastRequestSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            character_id = data_dict['character_id']

            try:
                character = Character.objects.get(pk=character_id)
                if  character.requested_user == self.request.user:
                    character.attached_user = character.requested_user
                    character.attached_user_name = character.requested_user.get_full_name()
                    character.requested_user = None
                    character.save()

                    # update user project table
                    user_project_obj = UserProject()
                    user_project_obj.user = self.request.user
                    user_project_obj.project = character.project
                    user_project_obj.character = character
                    user_project_obj.relation_type = UserProject.ATTACHED
                    user_project_obj.save()
                    # end

                    # add to team
                    team_obj = Team()
                    team_obj.user = self.request.user
                    team_obj.project = character.project
                    team_obj.job_type = JobType.objects.get(slug='actoractress')
                    team_obj.save()
                    # end

                    notification_obj = UserNotification.objects.filter(
                                        Q(user=self.request.user) &
                                        Q(notification_type=UserNotification.CAST_ATTACH_REQUEST) &
                                        Q(character=character)
                                       ).first()
                    notification_obj.delete()

                    # update notification table
                    notification = UserNotification()
                    notification.user = character.project.creator
                    notification.from_user = self.request.user
                    notification.project = character.project
                    notification.notification_type = UserNotification.CAST_ATTACH_RESPONSE
                    notification.message = self.request.user.get_full_name()+" accepted your attach request for character <b>"+character.name+"</b> of the project <b>"+str(character.project.title)+"</b>"
                    notification.character = character
                    notification.save()
                    # send notification to project creator
                    room_name = "user_"+str(character.project.creator.id)
                    notification_msg = {
                            'type': 'send_cast_attach_response_notification',
                            'message': str(notification.message),
                            'from': notification.from_user.get_full_name(),
                            "event": "CAST_ATTACH_RESPONSE"
                        }
                    notify(room_name, notification_msg)
                    # end notification section

                    response = {'message': "Cast Attach Request Accepted",
                                'character': character.name,
                                'project': character.project.title,
                                'status': status.HTTP_200_OK}
                else:
                    response = {'errors': 'Invalid user', 'status':
                                 status.HTTP_400_BAD_REQUEST}
            except Character.DoesNotExist:
                response = {'errors': 'Invalid ID', 'status':
                             status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)


class TopRatedMembersAjaxView(View, JSONResponseMixin):
    template_name = 'project/top-rated-members.html'

    def get(self, *args, **kwargs):
        context = dict()
        user_list = []
        user_rating_objs = UserRatingCombined.objects.all()

        try:
            actoractress = JobType.objects.get(slug='actoractress')
            actoractress_list = user_rating_objs.filter(job_type=actoractress).order_by('-rating')[:5]
        except JobType.DoesNotExist:
            actoractress_list = []

        try:
            director = JobType.objects.get(slug='director')
            director_list = user_rating_objs.filter(job_type=director).order_by('-rating')[:5]
        except JobType.DoesNotExist:
            director_list = []

        try:
            writer = JobType.objects.get(slug='writer')
            writer_list = user_rating_objs.filter(job_type=writer).order_by('-rating')[:5]
        except JobType.DoesNotExist:
            writer_list = []

        try:
            producer = JobType.objects.get(slug='producer')
            producer_list = user_rating_objs.filter(job_type=producer).order_by('-rating')[:5]
        except JobType.DoesNotExist:
            producer_list = []

        try:
            dp = JobType.objects.get(slug='director-of-photography')
            dp_list = user_rating_objs.filter(job_type=dp).order_by('-rating')[:5]
        except JobType.DoesNotExist:
            dp_list = []

        try:
            costume_designer = JobType.objects.get(slug='costume-designer')
            costume_designer_list = user_rating_objs.filter(job_type=costume_designer).order_by('-rating')[:5]
        except JobType.DoesNotExist:
            costume_designer_list = []

        try:
            art_director = JobType.objects.get(slug='art-director')
            art_director_list = user_rating_objs.filter(job_type=art_director).order_by('-rating')[:5]
        except JobType.DoesNotExist:
            art_director_list = []

        try:
            editor = JobType.objects.get(slug='editor')
            editor_list = user_rating_objs.filter(job_type=editor).order_by('-rating')[:5]
        except JobType.DoesNotExist:
            editor_list = []

        try:
            casting_director = JobType.objects.get(slug='casting-director')
            casting_director_list = user_rating_objs.filter(job_type=casting_director).order_by('-rating')[:5]
        except JobType.DoesNotExist:
            casting_director_list = []

        try:
            make_up_hair_artist = JobType.objects.get(slug='make-uphair-artist')
            make_up_hair_artist_list = user_rating_objs.filter(job_type=make_up_hair_artist).order_by('-rating')[:5]
        except JobType.DoesNotExist:
            make_up_hair_artist_list = []

        try:
            sound_designer = JobType.objects.get(slug='sound-designer')
            sound_designer_list = user_rating_objs.filter(job_type=sound_designer).order_by('-rating')[:5]
        except JobType.DoesNotExist:
            sound_designer_list = []

        try:
            composer = JobType.objects.get(slug='composer')
            composer_list = user_rating_objs.filter(job_type=composer).order_by('-rating')[:5]
        except JobType.DoesNotExist:
            composer_list = []


        top_rated_members_html = render_to_string(
                                'project/top-rated-members.html',
                                {
                                    'actoractress_list': actoractress_list,
                                    'director_list': director_list,
                                    'writer_list': writer_list,
                                    'producer_list': producer_list,
                                    'dp_list': dp_list,
                                    'costume_designer_list': costume_designer_list,
                                    'art_director_list': art_director_list,
                                    'editor_list': editor_list,
                                    'casting_director_list': casting_director_list,
                                    'make_up_hair_artist_list': make_up_hair_artist_list,
                                    'sound_designer_list': sound_designer_list,
                                    'composer_list': composer_list,
                                 })
        context['top_rated_members_html'] = top_rated_members_html
        return self.render_json_response(context)


class GetCastAtachRequestNotificationAjaxView(View, JSONResponseMixin):
    template_name = 'project/cast_attach_request_notification.html'

    def get(self, *args, **kwargs):
        context = dict()
        notification = UserNotification.objects.filter(
                            Q(user=self.request.user) &
                            Q(notification_type=UserNotification.CAST_ATTACH_REQUEST)
                            ).order_by('-created_time').first()
        notification_html = render_to_string(
                                'project/cast_attach_request_notification.html',
                                {'notification': notification
                                })
        context['notification_html'] = notification_html
        return self.render_json_response(context)


class GetCastAtachResponseNotificationAjaxView(View, JSONResponseMixin):
    template_name = 'project/cast_attach_response_notification.html'

    def get(self, *args, **kwargs):
        context = dict()
        notification = UserNotification.objects.filter(
                            Q(user=self.request.user) &
                            Q(notification_type=UserNotification.CAST_ATTACH_RESPONSE)
                            ).order_by('-created_time').first()
        notification_html = render_to_string(
                                'project/cast_attach_response_notification.html',
                                {'notification': notification
                                })
        context['notification_html'] = notification_html
        return self.render_json_response(context)



class AddToFavoritesAPI(APIView):
    serializer_class = UserProjectSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            project_id = data_dict['project']
            character_id = data_dict['character']
            user = self.request.user
            try:
                project = Project.objects.get(pk=project_id)
                try:
                    character = Character.objects.get(pk=character_id)
                    try:
                        user_project_obj = UserProject.objects.get(
                                                Q(user=user) &
                                                Q(project=project) &
                                                Q(character=character) &
                                                Q(relation_type=UserProject.FAVORITE)
                                            )
                        response = {'message': "Already added to favorites!!",
                                    'status': status.HTTP_200_OK}
                    except UserProject.DoesNotExist:
                        user_project_obj = UserProject()
                        user_project_obj.user = user
                        user_project_obj.project = project
                        user_project_obj.character = character
                        user_project_obj.relation_type = UserProject.FAVORITE
                        user_project_obj.save()
                        response = {'message': "Project added to favorites.",
                                    'status': status.HTTP_200_OK}

                except Character.DoesNotExist:
                    response = {'errors': 'Invalid Character ID', 'status':
                                status.HTTP_400_BAD_REQUEST}

            except Project.DoesNotExist:
                response = {'errors': 'Invalid Project ID', 'status':
                            status.HTTP_400_BAD_REQUEST}
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)