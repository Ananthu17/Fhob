import ast
import json
import requests

from django.contrib import messages
from django.shortcuts import render

from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import InitialUserForm
from .serializers import InitialIntrestedUsersSerializer


class InitialUserDetailSaveAPI(APIView):
    def post(self, request):
        serializer = InitialIntrestedUsersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        message = "Thank you for your help and consideration! " \
                  "We will be in contact when the site is up and ready. " \
                  "Sincerely, Film Hobo team."
        return Response([{"status": message}], status=status.HTTP_201_CREATED)


class InitialUserDetailSavePage(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'landing_pages/landing_home.html'

    def get(self, request):
        form = InitialUserForm()
        return render(request, 'landing_pages/landing_home.html',
                      {'form': form})

    def post(self, request):
        form = InitialUserForm(request.POST)
        if form.is_valid():
            json_response = json.dumps(request.POST)
            json_dict = ast.literal_eval(json_response)
            designation_id_response = form.cleaned_data['designation_id']
            destination_ids = []
            for designation_id in designation_id_response:
                destination_ids.append(str(designation_id.id))
            json_dict["designation_id"] = destination_ids

            user_response = requests.post(
             'http://127.0.0.1:8000/initial_user/landing_home_api/',
             data=json.dumps(json_dict),
             headers={'Content-type': 'application/json'})
            if user_response.status_code == 201:
                message = "Thank you for your help and consideration! " \
                 "We will be in contact when the site is up and ready. " \
                 "Sincerely, Film Hobo team."
                messages.success(request, message)
            else:
                error_messages = ast.literal_eval(user_response.text)
                _, message = error_messages.popitem()
                messages.error(request, message[0])
        else:
            return render(request, 'landing_pages/landing_home.html',
                          {'form': form})
