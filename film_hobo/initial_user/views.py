from django.contrib import messages
from django.utils.html import format_html
from django.shortcuts import render
from django.views import View

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


class InitialUserDetailSavePage(View):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'landing_pages/landing_home.html'

    def get(self, request):
        form = InitialUserForm()
        return render(request, 'landing_pages/landing_home.html',
                      {'form': form})

    def post(self, request):
        form = InitialUserForm(request.POST)
        if form.is_valid():
            form.save()
            message = format_html("You are in! <br> <br> Thank you for your " +
                                  "interest and for supporting our " +
                                  "brainchild. We can't wait for you to" +
                                  " see the final product. We are working " +
                                  "diligently to get this site to 136% " +
                                  "this coming summer! <br> <br>" +
                                  "However, do not sit back and relax… " +
                                  "Finesse those scripts, reels, projects " +
                                  " and talent of yours to dive right " +
                                  "into the mix and ride that wave into " +
                                  " the future. <br> <br>" +
                                  "For live updates, please follow us at " +
                                  "<a href='https://www.facebook.com/filmhobo'>" +
                                  "https://www.facebook.com/filmhobo</a>" +
                                  "<br> <br> Sincerely,<br>" +
                                  "The Film Hobo Team")
            messages.success(request, message)
            return render(request, 'landing_pages/landing_home.html',
                          {'form': form})
        else:
            return render(request, 'landing_pages/landing_home.html',
                          {'form': form})
