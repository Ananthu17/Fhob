import ast
import io
import json
import requests
import boto3

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
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect

from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import (UpdateAPIView,
                                     get_object_or_404)

from hobo_user.models import Team, ProjectMemberRating, CustomUser, \
     UserRating, UserRatingCombined, UserNotification, Project
from .models import Character, Sides
from .serializers import RateUserSkillsSerializer, ProjectVideoURLSerializer, \
      CharacterSerializer, UpdateCharacterSerializer, \
      ProjectLastDateSerializer, SidesSerializer
from hobo_user.utils import notify
from .forms import VideoSubmissionLastDateForm

s3_client = boto3.client(
                "s3",
                region_name="us-east-2",
                aws_access_key_id=settings.AWS_CLIENT_ID,
                aws_secret_access_key=settings.AWS_CLIENT_SECRET
            )


class ProjectVideoPlayerView(LoginRequiredMixin, TemplateView):
    template_name = 'project/videoplayer.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('id')
        project = Project.objects.get(id=project_id)
        rating_dict = {}
        team_members = Team.objects.filter(project=project_id)
        project_members_rating = ProjectMemberRating.objects.filter(
                                 project=project_id)
        for obj in project_members_rating:
            team_objs = obj.user.team_user.all()
            key_obj = team_objs.filter(
                    Q(project=obj.project) &
                    Q(job_type=obj.job_type)
                ).first()
            key = key_obj.id
            rating_dict[key] = obj.rating*20
        context["rating_dict"] = rating_dict
        context["team_members"] = team_members
        context["project"] = project

        if project.video_type == Project.UPLOAD_VIDEO:
            bucket_prefix = ""
            bucket_name = settings.S3_BUCKET_NAME
            path = f"{bucket_prefix}{project.creator.id}/{project.title}/{project_id}.mp4"
            s3_url = project.generate_s3_signed_url(
                s3_client, path, bucket_name)
            context['s3_url'] = s3_url
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
                            project_member_obj.user.get_full_name),
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
        context['project'] = project
        context['video_types'] = Project.VIDEO_TYPE_CHOICES
        return context

    # DON'T DELETE
    # def post(self, request, *args, **kwargs):
    #     bucket_prefix = ""
    #     project_id = self.kwargs.get('id')
    #     project = Project.objects.get(id=project_id)
    #     video = self.request.FILES['video']
    #     bucket_name = settings.S3_BUCKET_NAME
    #     path = f"{bucket_prefix}{self.request.user.id}/{project.title}/{project.id}.mp4"
    #     response = s3_client.put_object(
    #                     Bucket=bucket_name,
    #                     Body=video,
    #                     Key=path,
    #                     ServerSideEncryption="AES256",
    #                 )
    #     print("response", response)
    #     messages.success(self.request, "Video Uploaded")
    #     return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class SaveProjectVideoUrlAPI(APIView):
    serializer_class = ProjectVideoURLSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            data_dict = serializer.data
            print(data_dict)
            id = data_dict['id']
            video_url = data_dict['video_url']
            video_type = data_dict['video_type']
            try:
                project = Project.objects.get(pk=id)
                project.video_type = video_type
                project.video_url = video_url
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
                # character_obj.password = make_password(data_dict['password'])
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
        count = len(names)
        key = Token.objects.get(user=user).key
        token = 'Token '+key

        for i in range(count):
            json_dict['name'] = names[i]
            json_dict['description'] = descriptions[i]
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
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class CastApplyAuditionView(LoginRequiredMixin, TemplateView):
    template_name = 'project/cast-apply-audition.html'
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

    def post(self, request, *args, **kwargs):
        user = self.request.user
        # data_dict = {}
        # json_response = json.dumps(request.POST)
        # data_dict = ast.literal_eval(json_response)
        # project_id = self.kwargs.get('id')
        # character_id = self.request.POST.get('character_id')
        # data_dict['project'] = project_id
        # data_dict['character'] = character_id
        # key = Token.objects.get(user=user).key
        # token = 'Token '+key
        # user_response = requests.post(
        #             'http://127.0.0.1:8000/project/add-sides-api/',
        #             data=json.dumps(data_dict),
        #             headers={'Content-type': 'application/json',
        #                      'Authorization': token})
        # byte_str = user_response.content
        # dict_str = byte_str.decode("UTF-8")
        # response = ast.literal_eval(dict_str)
        # response = dict(response)
        # if 'status' in response:
        #     if response['status'] != 200:
        #         if 'errors' in response:
        #             errors = response['errors']
        #             print(errors)
        #             messages.warning(
        #                 self.request, "Failed to update scenes !!")
        #             return HttpResponseRedirect(
        #                 request.META.get('HTTP_REFERER', '/'))
        messages.success(self.request, "Sides updated successfully")
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



