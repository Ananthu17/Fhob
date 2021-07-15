
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseRedirect

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import HelpSerializer

from .models import Help

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
        messages.success(self.request, "Message received. Will get back to you soon.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
