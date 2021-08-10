import ast
import io
import json
import requests


from braces.views import JSONResponseMixin
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet

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
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password

from rest_framework.exceptions import ParseError
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import (UpdateAPIView,
                                     get_object_or_404)

from hobo_user.models import Location, Team, ProjectMemberRating, CustomUser, \
     UserRating, JobType, UserRatingCombined, UserNotification, Project
from .models import Audition, AuditionRating, AuditionRatingCombined, \
    Character, Sides, ProjectTracking, ProjectRating
from .serializers import RateUserSkillsSerializer, ProjectVideoURLSerializer, \
      CharacterSerializer, UpdateCharacterSerializer, \
      ProjectLastDateSerializer, \
      SidesSerializer, AuditionSerializer, PostProjectVideoSerializer, \
      PasswordSerializer, ProjectLoglineSerializer, TrackProjectSerializer, \
      RateAuditionSerializer, AuditionStatusSerializer, ProjectRatingSerializer
from hobo_user.serializers import UserSerializer
from hobo_user.utils import notify
from .forms import VideoSubmissionLastDateForm, AddSidesForm


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
                rating_count = user_rating.values('project').annotate(
                    count=Count('project'))
                for item in rating_count:
                    if item['count'] >= 10:
                        user_rating_count += 1
                # if for those 5 projects he has got atleast 10 ratings each
                if user_rating_count >= 5:
                    user.membership = CustomUser.PRO
                    user.save()

                    # update notification table
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
        character = get_object_or_404(Character, pk=character_id)
        context['character'] = character
        try:
            sides = Sides.objects.get(
                        Q(project=project) &
                        Q(character=character)
                        )
            context['sides'] = sides
        except Sides.DoesNotExist:
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
        characters = Character.objects.filter(project=project)
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
        character = get_object_or_404(Character, pk=character_id)
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
                audition.status = audition_status
                audition.save()
                response = {'message': "Audition status updated",
                            'status': status.HTTP_200_OK}
                messages.success(self.request, "Audition status updated.")
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
                        Q(status=Audition.CALLBACK)
                        )
        audition_dict = {}

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

            msg = "Rated  "+project.title +" by "+str(rating_obj.rating)+" stars."
            messages.success(self.request, msg)
            response = {'message': "Rating success",
                        'status': status.HTTP_201_CREATED}

        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)
