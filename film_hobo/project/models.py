from django.db import models
from django.utils.translation import ugettext_lazy as _
from ckeditor.widgets import CKEditorWidget
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField


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
    scene_1 = RichTextField(_("Scene Description"),
                            null=True, blank=True)
    scene_2 = RichTextField(_("Scene Description"),
                            null=True, blank=True)
    scene_3 = RichTextField(_("Scene Description"),
                            null=True, blank=True)

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
        (CALLBACK, 'Callback'),
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
    status = models.CharField(_("Status"),
                              choices=STATUS_CHOICES,
                              max_length=150,
                              default=APPLIED)
    cover_image = models.ImageField(upload_to='thumbnail/',
                                    blank=True, null=True,
                                    help_text="Image size:370 X 248.")

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
