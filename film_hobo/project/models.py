import PyPDF2
import datetime
import requests
from io import BytesIO
from django.core import files
from django.conf import settings
from ckeditor.widgets import CKEditorWidget
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from phonenumber_field.modelfields import PhoneNumberField

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator


class Character(models.Model):
    name = models.CharField(max_length=1000)
    project = models.ForeignKey('hobo_user.Project',
                                verbose_name=_("Project"),
                                on_delete=models.CASCADE)
    description = models.TextField(_("Description"), null=True, blank=True)
    password = models.CharField(max_length=12, null=True, blank=True)
    sort_order = models.IntegerField(blank=True, null=True)
    attached_user = models.ForeignKey('hobo_user.CustomUser',
                                      verbose_name=_("Attached User"),
                                      related_name='attached_user',
                                      on_delete=models.SET_NULL, null=True,
                                      blank=True)
    requested_user = models.ForeignKey('hobo_user.CustomUser',
                                       verbose_name=_("Requested User"),
                                       related_name='requested_user',
                                       on_delete=models.SET_NULL, null=True,
                                       blank=True)
    attached_user_name = models.CharField(_("Attached User Name"),
                                          max_length=1000,
                                          null=True, blank=True)
    created_time = models.DateTimeField(_('Created Time'),
                                        default=datetime.datetime.now,
                                        blank=False)

    def __str__(self):
        return self.project.title+" - "+self.name

    class Meta:
        verbose_name = 'Character'
        verbose_name_plural = 'Characters'


class Sides(models.Model):
    project = models.ForeignKey('hobo_user.Project',
                                verbose_name=_("Project"),
                                on_delete=models.CASCADE)
    character = models.ForeignKey(Character,
                                  verbose_name=_("Character"),
                                  on_delete=models.CASCADE)
    # scene_1 = RichTextUploadingField(_("Scene Description"),
    #                                  null=True, blank=True)
    # scene_2 = RichTextUploadingField(_("Scene Description"),
    #                                  null=True, blank=True)
    # scene_3 = RichTextUploadingField(_("Scene Description"),
    #                                  null=True, blank=True)
    scene_1_pdf = models.FileField(upload_to='script/', null=True, blank=True)
    scene_2_pdf = models.FileField(upload_to='script/', null=True, blank=True)
    scene_3_pdf = models.FileField(upload_to='script/', null=True, blank=True)
    scenes_combined = models.FileField(upload_to='script/', null=True, blank=True)

    def __str__(self):
        return self.project.title+" - "+self.character.name+" - sides"

    class Meta:
        verbose_name = 'Sides'
        verbose_name_plural = 'Sides'


class Audition(models.Model):
    YOUTUBE = 'youtube'
    VIMEO = 'vimeo'
    # FACEBOOK = 'facebook'

    VIDEO_TYPE_CHOICES = [
        (YOUTUBE, 'Youtube'),
        (VIMEO, 'Vimeo'),
        # (FACEBOOK, 'Facebook'),
    ]
    ATTACHED = 'attached'
    PASSED = 'passed'
    APPLIED = 'applied'
    CALLBACK = 'callback'
    STATUS_CHOICES = [
        (ATTACHED, 'Attached'),
        (PASSED, 'Passed'),
        (APPLIED, 'Applied'),
        (CALLBACK, 'Chemistry Room'),
    ]
    project = models.ForeignKey('hobo_user.Project',
                                verbose_name=_("Project"),
                                on_delete=models.CASCADE)
    character = models.ForeignKey('project.Character',
                                  verbose_name=_("Character"),
                                  on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    user = models.ForeignKey('hobo_user.CustomUser',
                             verbose_name=_("User"),
                             on_delete=models.CASCADE,
                             related_name='audition_user')
    agent_name = models.CharField(max_length=250, null=True, blank=True)
    agent_email = models.EmailField(_('Email'), null=True, blank=True)
    agent = models.ForeignKey('hobo_user.CustomUser',
                              verbose_name=_("Agent"),
                              on_delete=models.CASCADE,
                              null=True, blank=True,
                              related_name='audition_user_agent')
    location = models.ForeignKey("hobo_user.Location",
                                 on_delete=models.SET_NULL,
                                 related_name='audition_user_location',
                                 verbose_name=_("Location"),
                                 null=True, blank=True)
    video_url = models.CharField(max_length=1000,
                                 null=True, blank=True)
    video_type = models.CharField(_("Video Type"),
                                  choices=VIDEO_TYPE_CHOICES,
                                  max_length=150, null=True,
                                  default=VIMEO)
    audition_status = models.CharField(_("Status"),
                                       choices=STATUS_CHOICES,
                                       max_length=150,
                                       default=APPLIED)
    cover_image = models.ImageField(upload_to='thumbnail/',
                                    blank=True, null=True,
                                    help_text="Image size:370 X 248.")
    status_update_date = models.DateField(_("Status updated on"),
                                          null=True, blank=True,)
    i_agree = models.BooleanField(
                _('I Agree'),
                default=True,
                help_text=_(
                    'Designates whether the user accepted the terms and conditions.'),
            )

    def __str__(self):
        return self.project.title+" - "+self.character.name+"-"+self.name

    class Meta:
        verbose_name = 'Audition'
        verbose_name_plural = 'Audition'


class ProjectTracking(models.Model):
    project = models.ForeignKey("hobo_user.Project",
                                on_delete=models.CASCADE,
                                related_name='project_tracking',
                                verbose_name=_("User"),
                                null=True)
    tracked_by = models.ManyToManyField('hobo_user.CustomUser',
                                        blank=True,
                                        related_name="project_tracked_by",
                                        verbose_name=_("Tracked by")
                                        )

    def __str__(self):
        return str(self.project)

    class Meta:
        verbose_name = 'Project Tracking'
        verbose_name_plural = 'Project Tracking'


class AuditionRating(models.Model):
    team_member = models.ForeignKey("hobo_user.Team",
                                    on_delete=models.CASCADE,
                                    related_name='audition_rating_team_member',
                                    verbose_name=_("Team Member"),
                                    null=True)
    audition = models.ForeignKey("project.Audition",
                                 on_delete=models.CASCADE,
                                 related_name='audition',
                                 verbose_name=_("Audition"),
                                 null=True)
    rating = models.IntegerField(_("Rating"),
                                 validators=[MinValueValidator(0),
                                 MaxValueValidator(5)], null=True)
    review = models.TextField(_("Review"), null=True, blank=True)

    def __str__(self):
        return str(self.audition.name) + " -rated by " +str(self.team_member.user.get_full_name())

    class Meta:
        verbose_name = 'Audition Rating'
        verbose_name_plural = 'Audition Ratings'


class AuditionRatingCombined(models.Model):
    audition = models.ForeignKey("project.Audition",
                                 on_delete=models.CASCADE,
                                 related_name='audition_rating_combined',
                                 verbose_name=_("User"),
                                 null=True)
    rating = models.FloatField(_("Rating"), null=True, blank=True)

    def __str__(self):
        return str(self.audition.name)

    class Meta:
        verbose_name = 'Audition Ratings Combined'
        verbose_name_plural = 'Audition Ratings Combined'


class ProjectRating(models.Model):
    rated_by = models.ForeignKey("hobo_user.CustomUser",
                                 on_delete=models.CASCADE,
                                 related_name='project_rated_by_user',
                                 verbose_name=_("User"),
                                 null=True)
    project = models.ForeignKey("hobo_user.Project",
                                on_delete=models.CASCADE,
                                related_name='rating_project',
                                verbose_name=_("Project"),
                                null=True)
    rating = models.IntegerField(_("Rating"),
                                 validators=[MinValueValidator(0),
                                 MaxValueValidator(5)], null=True)
    reason = models.TextField(_("Reason"), null=True, blank=True)

    def __str__(self):
        return str(self.rated_by)

    class Meta:
        verbose_name = 'Project Rating'
        verbose_name_plural = 'Project Ratings'


class Comment(models.Model):
    user = models.ForeignKey("hobo_user.CustomUser",
                             on_delete=models.CASCADE,
                             related_name='commented_user',
                             verbose_name=_("User"),
                             null=True)
    project = models.ForeignKey("hobo_user.Project",
                                on_delete=models.CASCADE,
                                related_name='project_comment',
                                verbose_name=_("Project"),
                                null=True)
    comment_txt = models.TextField(_("Comment"), null=True, blank=True)
    reply_to = models.ForeignKey("self",
                                 on_delete=models.SET_NULL,
                                 related_name='comment_reply',
                                 verbose_name=_("Reply"),
                                 null=True, blank=True)
    created_time = models.DateTimeField(_('Created Time'), auto_now_add=True,
                                        blank=False)

    def __str__(self):
        return str(self.project.title+" commented by "+self.user.get_full_name())

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'


class SceneImages(models.Model):
    SCENE_1 = 'scene_1'
    SCENE_2 = 'scene_2'
    SCENE_3 = 'scene_3'

    SCENE_CHOICES = [
        (SCENE_1, 'Scene 1'),
        (SCENE_2, 'Scene 2'),
        (SCENE_3, 'Scene 3'),
    ]
    project = models.ForeignKey("hobo_user.Project",
                                on_delete=models.CASCADE,
                                related_name='project_scene_image',
                                verbose_name=_("Project"),
                                null=True)
    character = models.ForeignKey("project.Character",
                                  on_delete=models.CASCADE,
                                  related_name='character_scene_image',
                                  verbose_name=_("Character"),
                                  null=True)
    image = models.ImageField(upload_to='scene/',
                              null=True,
                              help_text="Image size:370 X 248.")
    scene = models.CharField(_("Video Type"),
                             choices=SCENE_CHOICES,
                             max_length=150, null=True,
                             default=SCENE_1)
    created_time = models.DateTimeField(_('Created Time'), auto_now_add=True,
                                        blank=False)

    def __str__(self):
        return str(self.project.title+" - "+str(self.get_scene_display()))

    class Meta:
        verbose_name = 'Scene Image'
        verbose_name_plural = 'Scene Images'


class ProjectCrew(models.Model):
    project = models.ForeignKey("hobo_user.Project",
                                on_delete=models.CASCADE,
                                related_name='project_crew_member',
                                verbose_name=_("Project"),
                                null=True)
    job_type = models.ForeignKey("hobo_user.JobType",
                                 on_delete=models.CASCADE,
                                 related_name='project_crew_job_type',
                                 verbose_name=_("Job Type"),
                                 null=True)
    count = models.IntegerField(blank=True, null=True)
    qualification = models.TextField(_("Qualification"), null=True, blank=True)
    created_time = models.DateTimeField(_('Created Time'), auto_now_add=True,
                                        blank=False)

    def __str__(self):
        return str(self.project.title+" - "+str(self.job_type.title))

    class Meta:
        verbose_name = 'Project Crew'
        verbose_name_plural = 'Project Crew'


class CrewApplication(models.Model):
    ATTACHED = 'attached'
    PASSED = 'passed'
    APPLIED = 'applied'
    STATUS_CHOICES = [
        (ATTACHED, 'Attached'),
        (PASSED, 'Passed'),
        (APPLIED, 'Applied'),
    ]
    project = models.ForeignKey('hobo_user.Project',
                                verbose_name=_("Project"),
                                on_delete=models.CASCADE)
    crew = models.ForeignKey('project.ProjectCrew',
                             verbose_name=_("Crew"),
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    user = models.ForeignKey('hobo_user.CustomUser',
                             verbose_name=_("User"),
                             on_delete=models.CASCADE,
                             related_name='crew_apply_user')
    agent_name = models.CharField(max_length=250, null=True, blank=True)
    agent_email = models.EmailField(_('Email'), null=True, blank=True)
    agent = models.ForeignKey('hobo_user.CustomUser',
                              verbose_name=_("Agent"),
                              on_delete=models.CASCADE,
                              null=True, blank=True,
                              related_name='crew_apply_user_agent')
    location = models.ForeignKey("hobo_user.Location",
                                 on_delete=models.SET_NULL,
                                 related_name='crew_apply_user_location',
                                 verbose_name=_("Location"),
                                 null=True, blank=True)
    application_status = models.CharField(_("Status"),
                                          choices=STATUS_CHOICES,
                                          max_length=150,
                                          default=APPLIED)
    phone_number = PhoneNumberField(_("Phone Number"), null=True,
                                    blank=True)
    cover_letter = models.FileField(upload_to='script/', null=True, blank=True)
    status_update_date = models.DateField(_("Status updated on"),
                                          null=True, blank=True, auto_now_add=True)
    i_agree = models.BooleanField(
                _('I Agree'),
                default=True,
                help_text=_(
                    'Designates whether the user accepted the terms and conditions.'),
            )

    def __str__(self):
        return str(self.project.title+" - "+str(self.crew.job_type.title)+" - "+self.user.get_full_name())

    class Meta:
        verbose_name = 'Crew Application'
        verbose_name_plural = 'Crew Applications'


class AttachedCrewMember(models.Model):
    ATTACHED = 'attached'
    REQUESTED = 'requested'
    STATUS_CHOICES = [
        (ATTACHED, 'Attached'),
        (REQUESTED, 'Requested'),
    ]
    user = models.ForeignKey('hobo_user.CustomUser',
                             verbose_name=_("User"),
                             on_delete=models.CASCADE,
                             related_name='attached_crew_member')
    crew = models.ForeignKey('project.ProjectCrew',
                             verbose_name=_("Crew"),
                             on_delete=models.CASCADE)
    crew_status = models.CharField(_("Status"),
                                   choices=STATUS_CHOICES,
                                   max_length=150,
                                   default=ATTACHED)

    def __str__(self):
        return str(self.user.get_full_name())

    class Meta:
        verbose_name = 'Attached Crew Member'
        verbose_name_plural = 'Attached Crew Members'
