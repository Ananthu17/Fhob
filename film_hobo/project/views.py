# from django.shortcuts import render
import os
import json
import requests
import boto3
from braces.views import JSONResponseMixin

from django.conf import settings
from django.db.models import Count, Sum
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.db.models import Sum
from django.template.loader import render_to_string

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


from hobo_user.models import Team, ProjectMemberRating, CustomUser, \
     UserRating, JobType, UserRatingCombined, UserNotification, Project
from .serializers import RateUserSkillsSerializer, ProjectVideoURLSerializer
from hobo_user.utils import notify, get_notifications_time

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

        bucket_prefix = ""
        bucket_name = settings.S3_BUCKET_NAME
        path = f"{bucket_prefix}{self.request.user.id}/{project.title}/{project_id}.mp4"
        s3_url = project.generate_s3_signed_url(s3_client, path, bucket_name)
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
