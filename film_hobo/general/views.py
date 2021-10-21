import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseRedirect, FileResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.base import View
from django.conf import settings
from django.template import loader
from django.core.mail import send_mail

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import EmailUs, Help
from .serializers import HelpSerializer, ContactUsSerializer

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
            screenshot = request.data['screenshot']
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
    template_name = 'general/help.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        help_objs = Help.objects.filter(user=user)
        context["help_objs"] = help_objs
        return context

    def post(self, request, *args, **kwargs):
        screenshot = ""
        subject = self.request.POST.get('subject')
        description = self.request.POST.get('description')
        if 'screenshot' in self.request.FILES:
            screenshot = self.request.FILES['screenshot']

        help_obj = Help()
        help_obj.user = self.request.user
        help_obj.subject = subject
        help_obj.description = description
        help_obj.screenshot = screenshot
        help_obj.save()
        messages.success(self.request,
                         "Message received. Will get back to you soon.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class BetaUserAdmin(View):
    """
    Web URL View to load the beta user page
    """
    def get(self, request, *args, **kwargs):
        return render(request, 'beta_user/beta_user_admin.html')


# class AddBetaUserCode(APIView):

#     def post(self, request):
#         return Response(response)


class HelpProject(View):
    """
    Web URL View to load the project help page
    """
    def get(self, request, *args, **kwargs):
        return render(request, 'help/help_project.html')


class HelpGettingStarted(View):
    """
    Web URL View to load the getting started help page
    """
    def get(self, request, *args, **kwargs):
        return render(request, 'help/help_getting_started.html')


class HelpRating(View):
    """
    Web URL View to load the rating help page
    """
    def get(self, request, *args, **kwargs):
        return render(request, 'help/help_rating.html')


class HelpShowcase(View):
    """
    Web URL View to load the showcase help page
    """
    def get(self, request, *args, **kwargs):
        return render(request, 'help/help_showcase.html')


class HelpSAMR(View):
    """
    Web URL View to load the samr help page
    """
    def get(self, request, *args, **kwargs):
        return render(request, 'help/help_samr.html')


class HelpNetworking(View):
    """
    Web URL View to load the networking help page
    """
    def get(self, request, *args, **kwargs):
        return render(request, 'help/help_networking.html')


class HelpCommunityRules(View):
    """
    Web URL View to load the community rules help page
    """
    def get(self, request, *args, **kwargs):
        return render(request, 'help/help_community_rules.html')


class HelpMembership(View):
    """
    Web URL View to load the membership rules help page
    """
    def get(self, request, *args, **kwargs):
        return render(request, 'help/help_membership.html')


class TermsOfService(View):

    def get(self, request, *args, **kwargs):
        filepath = os.path.join('media', 'terms_of_service.pdf')
        return FileResponse(open(filepath, 'rb'),
                            content_type='application/pdf')


class PrivacyPolicy(View):

    def get(self, request, *args, **kwargs):
        filepath = os.path.join('media', 'privacy_policy.pdf')
        return FileResponse(open(filepath, 'rb'),
                            content_type='application/pdf')


class RefundPolicy(View):

    def get(self, request, *args, **kwargs):
        filepath = os.path.join('media', 'refund_policy.pdf')
        return FileResponse(open(filepath, 'rb'),
                            content_type='application/pdf')


class IntellectualPropertyRights(View):

    def get(self, request, *args, **kwargs):
        filepath = os.path.join('media', 'intellectual_property_rights.pdf')
        return FileResponse(open(filepath, 'rb'),
                            content_type='application/pdf')


class Membership(View):

    def get(self, request, *args, **kwargs):
        filepath = os.path.join('media', 'membership.pdf')
        return FileResponse(open(filepath, 'rb'),
                            content_type='application/pdf')


class EmailUsView(LoginRequiredMixin, TemplateView):
    template_name = 'general/email_us.html'
    login_url = '/hobo_user/user_login/'
    redirect_field_name = 'login_url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        return context


class ContactUsAPI(APIView):
    serializer_class = ContactUsSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            to_email = []
            to_email_id = ""
            data_dict = serializer.data
            contact_obj = EmailUs()
            contact_obj.user = self.request.user
            contact_obj.subject = data_dict['subject']
            contact_obj.message = data_dict['message']
            contact_obj.topic = data_dict['topic']
            contact_obj.save()
            response = {'message': "Message send successfully.",
                        'status': status.HTTP_200_OK}
            messages.success(self.request, "Message send successfully.")

            # send email
            if contact_obj.topic == EmailUs.General:
                to_email_id = settings.DEFAULT_GENERAL_MAIL
            if contact_obj.topic == EmailUs.Technical:
                to_email_id = settings.DEFAULT_TECHNICAL_MAIL
            if contact_obj.topic == EmailUs.Sevices:
                to_email_id = settings.DEFAULT_SERVICE_MAIL
            if contact_obj.topic == EmailUs.Abuse:
                to_email_id = settings.DEFAULT_ABUSE_MAIL
            if contact_obj.topic == EmailUs.Business:
                to_email_id = settings.DEFAULT_BUSINESS_MAIL

            to_email.append(to_email_id)
            subject = contact_obj.subject
            message = contact_obj.message
            html_message = loader.render_to_string(
                                'general/contact_mail.html',
                                {
                                    'site_url': settings.ORIGIN_URL,
                                    'from_user': self.request.user,
                                    'message': message,
                                    'topic': contact_obj.get_topic_display,
                                }
                            )
            send_mail(subject, message,
                      settings.EMAIL_FROM,
                      to_email, fail_silently=True,
                      html_message=html_message)
        else:
            print(serializer.errors)
            response = {'errors': serializer.errors, 'status':
                        status.HTTP_400_BAD_REQUEST}
        return Response(response)
