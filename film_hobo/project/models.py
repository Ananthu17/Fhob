# import PyPDF2
import datetime
# import requests
# from io import BytesIO
# from django.core import files
# from django.conf import settings
# from ckeditor.widgets import CKEditorWidget
# from ckeditor.fields import RichTextField
# from ckeditor_uploader.fields import RichTextUploadingField
from phonenumber_field.modelfields import PhoneNumberField

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator


class Character(models.Model):
    MALE = 'male'
    FEMALE = 'female'
    OTHERS = 'others'
    FIVE_TO_SEVEN = 'five_to_seven'
    EIGHT_TO_TEN = 'eight_to_ten'
    ELEVEN_TO_FIFTEEN = 'eleven_to_fifteen'
    SIXTEEN_TO_TWENTY = 'sixteen_to_twenty'
    TWENTYONE_TO_THIRTY = 'twentyone_to_thirty'
    THIRTYONE_TO_FOURTY = 'thirtyone_to_fourty'
    FOURTYONE_TO_FIFTY = 'fourtyone_to_fifty'
    FIFTYONE_TO_SIXTY = 'fiftyone_to_sixty'
    SIXTYONE_TO_SEVENTY = 'sixtyone_to_seventy'
    GENDER_CHOICES = [
                    (MALE, 'Male'),
                    (FEMALE, 'Female'),
                    (OTHERS, 'Others'),
                    ]
    AGE_CHOICES = [
                (FIVE_TO_SEVEN, '5 to 7'),
                (EIGHT_TO_TEN, '8 to 10'),
                (ELEVEN_TO_FIFTEEN, '11 to 15'),
                (SIXTEEN_TO_TWENTY, '16 to 20'),
                (TWENTYONE_TO_THIRTY, '21 to 30'),
                (THIRTYONE_TO_FOURTY, '31 to 40'),
                (FOURTYONE_TO_FIFTY, '41 to 50'),
                (FIFTYONE_TO_SIXTY, '51 to 60'),
                (SIXTYONE_TO_SEVENTY, '61 to 70'),
                ]
    name = models.CharField(max_length=1000)
    project = models.ForeignKey('hobo_user.Project',
                                verbose_name=_("Project"),
                                on_delete=models.CASCADE,
                                related_name='project_character')
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
    gender = models.CharField(_("Gender"),
                              choices=GENDER_CHOICES,
                              max_length=150,
                              null=True, blank=True)
    age = models.CharField(_("Age"),
                           choices=AGE_CHOICES,
                           max_length=150,
                           null=True, blank=True)

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
    scenes_combined = models.FileField(
        upload_to='script/', null=True, blank=True)

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
        return str(self.audition.name) + " -rated by " + str(self.team_member.user.get_full_name())

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
    # PASSED = 'passed'
    APPLIED = 'applied'
    STATUS_CHOICES = [
        (ATTACHED, 'Attached'),
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
                              on_delete=models.SET_NULL,
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
                             related_name='attached_crew_member',
                             null=True, blank=True)
    crew = models.ForeignKey('project.ProjectCrew',
                             verbose_name=_("Crew"),
                             on_delete=models.CASCADE)
    crew_status = models.CharField(_("Status"),
                                   choices=STATUS_CHOICES,
                                   max_length=150,
                                   default=ATTACHED)
    name = models.CharField(_("Non FilmHobo member Name"),
                            max_length=150, null=True, blank=True)

    def __str__(self):
        if self.user:
            return str(self.user.get_full_name())
        else:
            return str(self.name)

    class Meta:
        verbose_name = 'Attached Crew Member'
        verbose_name_plural = 'Attached Crew Members'


class ReportVideo(models.Model):
    reported_by_user = models.ForeignKey('hobo_user.CustomUser',
                                         verbose_name=_("Reported by"),
                                         on_delete=models.CASCADE,
                                         related_name='video_reported_by_user',
                                         null=True, blank=True)
    video_url = models.CharField(_("Video URL"),
                                 max_length=250, null=True, blank=True)
    project_id = models.CharField(_("Project id"),
                                  max_length=150, null=True, blank=True)
    project_name = models.CharField(_("Project Name"),
                                    max_length=250, null=True, blank=True)
    reason = models.TextField(_("Reason"), null=True, blank=True)

    def __str__(self):
        return str(self.reported_by_user.get_full_name())

    class Meta:
        verbose_name = 'Report Video'
        verbose_name_plural = 'Report Video'


class ProjectVideoLikeAndDislike(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    LIKE_OR_DISLIKE_CHOICES = [
                                (LIKE, 'Like'),
                                (DISLIKE, 'Dislike'),
                                ]
    user = models.ForeignKey('hobo_user.CustomUser',
                             verbose_name=_("Submitted by"),
                             on_delete=models.CASCADE,
                             related_name='video_like_dislike_by_user',
                             null=True, blank=True)
    project = models.ForeignKey('hobo_user.Project',
                                verbose_name=_("Project"),
                                on_delete=models.CASCADE)
    like_or_dislike = models.CharField(_("Like or Dislike"),
                                       choices=LIKE_OR_DISLIKE_CHOICES,
                                       max_length=150,
                                       default=LIKE)

    def __str__(self):
        return str(self.user.get_full_name())

    class Meta:
        verbose_name = 'Project Video Like And Dislike'
        verbose_name_plural = 'Project Video Likes And Dislikes'


class DraftProject(models.Model):
    """
    A model to store all project related details
    """
    PUBLIC = 'public'
    PRIVATE = 'private'
    VISIBILITY_CHOICES = [
        (PUBLIC, 'Public'),
        (PRIVATE, 'Private'),
    ]
    UPLOADED = 'uploaded'
    POSTED = 'posted'
    NOT_AVAILABLE = 'not_available'
    VIDEO_STATUS_CHOICES = [
        (UPLOADED, 'Uploaded'),
        (POSTED, 'Posted'),
        (NOT_AVAILABLE, 'Not Available'),
    ]
    NATION_WIDE = 'nation_wide'
    LOCAL_ONLY = 'local_only'
    CAST_ATTACHMENT_CHOICES = [
        (NATION_WIDE, 'Nation Wide'),
        (LOCAL_ONLY, 'Local Only'),
    ]
    INDIE_WITH_RATING_1_STAR = 'indie_with_rating_1_star'
    INDIE_WITH_RATING_2_STAR = 'indie_with_rating_2_star'
    INDIE_WITH_RATING_3_STAR = 'indie_with_rating_3_star'
    INDIE_WITH_RATING_4_STAR = 'indie_with_rating_4_star'
    INDIE_WITH_RATING_5_STAR = 'indie_with_rating_5_star'
    PRO_WITH_RATING_1_STAR = 'pro_with_rating_1_star'
    PRO_WITH_RATING_2_STAR = 'pro_with_rating_2_star'
    PRO_WITH_RATING_3_STAR = 'pro_with_rating_3_star'
    PRO_WITH_RATING_4_STAR = 'pro_with_rating_4_star'
    PRO_WITH_RATING_5_STAR = 'pro_with_rating_5_star'
    INDIE_AND_PRO_WITH_RATING_1_STAR = 'indie_and_pro_with_rating_1_star'
    INDIE_AND_PRO_WITH_RATING_2_STAR = 'indie_and_pro_with_rating_2_star'
    INDIE_AND_PRO_WITH_RATING_3_STAR = 'indie_and_pro_with_rating_3_star'
    INDIE_AND_PRO_WITH_RATING_4_STAR = 'indie_and_pro_with_rating_4_star'
    INDIE_AND_PRO_WITH_RATING_5_STAR = 'indie_and_pro_with_rating_5_star'
    CAST_SAMR_CHOICES = [
        (INDIE_WITH_RATING_1_STAR, 'Indie with 1 star rating'),
        (INDIE_WITH_RATING_2_STAR, 'Indie with 2 star rating'),
        (INDIE_WITH_RATING_3_STAR, 'Indie with 3 star rating'),
        (INDIE_WITH_RATING_4_STAR, 'Indie with 4 star rating'),
        (INDIE_WITH_RATING_5_STAR, 'Indie with 5 star rating'),
        (PRO_WITH_RATING_1_STAR, 'Pro with 1 star rating'),
        (PRO_WITH_RATING_2_STAR, 'Pro with 2 star rating'),
        (PRO_WITH_RATING_3_STAR, 'Pro with 3 star rating'),
        (PRO_WITH_RATING_4_STAR, 'Pro with 4 star rating'),
        (PRO_WITH_RATING_5_STAR, 'Pro with 5 star rating'),
        (INDIE_AND_PRO_WITH_RATING_1_STAR, 'Indie and Pro with rating 1 star'),
        (INDIE_AND_PRO_WITH_RATING_2_STAR, 'Indie and Pro with rating 2 star'),
        (INDIE_AND_PRO_WITH_RATING_3_STAR, 'Indie and Pro with rating 3 star'),
        (INDIE_AND_PRO_WITH_RATING_4_STAR, 'Indie and Pro with rating 4 star'),
        (INDIE_AND_PRO_WITH_RATING_5_STAR, 'Indie and Pro with rating 5 star'),
    ]

    CREW_SAMR_CHOICES = [
        (INDIE_WITH_RATING_1_STAR, 'Indie with 1 star rating'),
        (INDIE_WITH_RATING_2_STAR, 'Indie with 2 star rating'),
        (INDIE_WITH_RATING_3_STAR, 'Indie with 3 star rating'),
        (INDIE_WITH_RATING_4_STAR, 'Indie with 4 star rating'),
        (INDIE_WITH_RATING_5_STAR, 'Indie with 5 star rating'),
        (PRO_WITH_RATING_1_STAR, 'Pro with 1 star rating'),
        (PRO_WITH_RATING_2_STAR, 'Pro with 2 star rating'),
        (PRO_WITH_RATING_3_STAR, 'Pro with 3 star rating'),
        (PRO_WITH_RATING_4_STAR, 'Pro with 4 star rating'),
        (PRO_WITH_RATING_5_STAR, 'Pro with 5 star rating'),
        (INDIE_AND_PRO_WITH_RATING_1_STAR, 'Indie and Pro with rating 1 star'),
        (INDIE_AND_PRO_WITH_RATING_2_STAR, 'Indie and Pro with rating 2 star'),
        (INDIE_AND_PRO_WITH_RATING_3_STAR, 'Indie and Pro with rating 3 star'),
        (INDIE_AND_PRO_WITH_RATING_4_STAR, 'Indie and Pro with rating 4 star'),
        (INDIE_AND_PRO_WITH_RATING_5_STAR, 'Indie and Pro with rating 5 star'),
    ]

    No_PAYMENT = 'no_payment'
    NEGOTIABLE = 'payment_is_negotiable'
    ULB = 'SAG_ultra_low_budget'
    MLB = 'SAG_moderate_low_budget'
    LB = 'SAG_low_budget'
    ThB = 'SAG_theatrical_budget'
    ShB = 'SAG_short_film_budget'
    MiB = 'SAG_micro_budget'
    StB = 'SAG_studet_budget'
    CAST_PAY_RATE_CHOICES = [
                    (No_PAYMENT, 'No Payment'),
                    (NEGOTIABLE, 'Payment is Negotiable'),
                    (ULB, 'SAG Ultra Low Budget'),
                    (MLB, 'SAG Moderate Low Budget'),
                    (LB, 'SAG Low Budget'),
                    (ThB, 'SAG Theatrical Budget'),
                    (ShB, 'SAG Short Film Budget'),
                    (MiB, 'SAG Micro Budget'),
                    (StB, 'SAG Studet Budget'),
                    ]
    SCENE = 'SCH'
    SHORTS = 'SHO'
    PILOT = 'PIL'
    FEATURE = 'FTR'
    FORMAT_CHOICES = [
        (SCENE, 'Scene'),
        (SHORTS, 'Shorts'),
        (PILOT, 'Pilot'),
        (FEATURE, 'Feature'),
    ]
    YOUTUBE = 'youtube'
    VIMEO = 'vimeo'
    VIDEO_TYPE_CHOICES = [
        (YOUTUBE, 'Youtube'),
        (VIMEO, 'Vimeo'),
    ]
    SAGAFTRA = 'SAGAFTRA'
    INDIE = 'INDIE'
    PRODUCTION_CHOICES = [
        (SAGAFTRA, 'SAG-AFTRA'),
        (INDIE, 'INDIE'),
    ]

    # ACTION = 'ACT'
    # ADVENTURE = 'ADV'
    ANIMATION = 'ANI'
    BIOGRAPHY = 'BIO'
    COMEDY = 'COM'
    CRIME = 'CRI'
    DOCUMENTARY = 'DOC'
    DRAMA = 'DRA'
    FAMILY = 'FAM'
    FANTASY = 'FAN'
    FILM_NOIR = 'FIL'
    GAME_SHOW = 'GAM'
    HISTORY = 'HIS'
    HORROR = 'HOR'
    LGBTQ = 'LGB'
    MILITARY = 'MIL'
    MUSICAL = 'MUS'
    # MYSTERY = 'MYS'
    REALITY_TV = 'REA'
    ROMANCE = 'ROM'
    SCIENCE_FICTION = 'SCI'
    SPORT = 'SPO'
    TALK_SHOW = 'TAL'
    # THRILLER = 'THR'
    WESTERN = 'WES'
    MYSTERY_THRILLER = 'MYS_THR'
    ACTION_ADVENTURE = 'ACT_ADV'
    GENRE_CHOICES = [
        # (ACTION, 'Action'),
        # (ADVENTURE, 'Adventure'),
        (ANIMATION, 'Animation'),
        (BIOGRAPHY, 'Biography'),
        (COMEDY, 'Comedy'),
        (CRIME, 'Crime'),
        (DOCUMENTARY, 'Documentary'),
        (DRAMA, 'Drama'),
        (FAMILY, 'Family'),
        (FANTASY, 'Fantasy'),
        (FILM_NOIR, 'Film Noir'),
        (GAME_SHOW, 'Game Show'),
        (HISTORY, 'History'),
        (HORROR, 'Horror'),
        (LGBTQ, 'LGBTQ'),
        (MILITARY, 'Military'),
        (MUSICAL, 'Musical'),
        # (MYSTERY, 'Mystery'),
        (REALITY_TV, 'Reality TV'),
        (ROMANCE, 'Romance'),
        (SCIENCE_FICTION, 'Science Fiction'),
        (SPORT, 'Sport'),
        (TALK_SHOW, 'Talk Show'),
        # (THRILLER, 'Thriller'),
        (WESTERN, 'Western'),
        (ACTION_ADVENTURE, 'Action/Adventure'),
        (MYSTERY_THRILLER, 'Mystery/Thriller'),
    ]

    creator = models.ForeignKey('hobo_user.CustomUser',
                                verbose_name=_("Creator"),
                                on_delete=models.CASCADE)
    title = models.CharField(max_length=1000)
    format = models.CharField(_("Format Type"),
                              choices=FORMAT_CHOICES,
                              max_length=150, null=True, blank=True)

    number_of_pages = models.IntegerField(_("Number of Pages"),
                                          null=True, blank=True)
    genre = models.CharField(_("Genre Type"),
                             choices=GENRE_CHOICES,
                             max_length=150, null=True, blank=True)
    rating = models.IntegerField(_("Rating"), validators=[MinValueValidator(0),
                                 MaxValueValidator(5)], null=True, blank=True,
                                 default=0)
    video_rating = models.IntegerField(_("Video Rating"),
                                       validators=[MinValueValidator(0),
                                       MaxValueValidator(5)], null=True, blank=True,
                                       default=0)
    video_url = models.CharField(max_length=1000,
                                 null=True, blank=True)
    video_type = models.CharField(_("Video Type"),
                                  choices=VIDEO_TYPE_CHOICES,
                                  max_length=150, null=True, blank=True)
    last_date = models.DateField(_("Last date for submitting video"),
                                 null=True, blank=True,)
    location = models.ForeignKey("hobo_user.Location",
                                 on_delete=models.SET_NULL,
                                 related_name='draft_project_location',
                                 verbose_name=_("Location"),
                                 null=True, blank=True)
    script = models.FileField(upload_to='script/', null=True, blank=True)
    visibility = models.CharField(_("Visibility"),
                                  choices=VISIBILITY_CHOICES,
                                  max_length=150, default=PRIVATE)
    visibility_password = models.CharField(max_length=12, null=True,
                                           blank=True)
    cast_attachment = models.CharField(_("Cast Attachment"),
                                       choices=CAST_ATTACHMENT_CHOICES,
                                       max_length=150, default=NATION_WIDE)
    cast_pay_rate = models.IntegerField(_("Castpay Rate"),
                                        null=True, blank=True)
    sag_aftra = models.CharField(_("SAG AFTRA"),
                                 choices=CAST_PAY_RATE_CHOICES,
                                 max_length=150, default=NEGOTIABLE)
    cast_samr = models.CharField(_("Cast SAMR"),
                                 choices=CAST_SAMR_CHOICES,
                                 max_length=150,
                                 default=INDIE_AND_PRO_WITH_RATING_1_STAR)
    crew_samr = models.CharField(_("Crew SAMR"),
                                 choices=CREW_SAMR_CHOICES,
                                 max_length=150,
                                 default=INDIE_AND_PRO_WITH_RATING_1_STAR)
    video_status = models.CharField(_("Video Status"),
                                    choices=VIDEO_STATUS_CHOICES,
                                    max_length=150,
                                    default=NOT_AVAILABLE,
                                    null=True, blank=True)
    video_cover_image = models.ImageField(upload_to='thumbnail/',
                                          blank=True, null=True,
                                          help_text="Image size:370 X 248.")
    script_visibility = models.CharField(_("Script Visibility"),
                                         choices=VISIBILITY_CHOICES,
                                         max_length=150,  null=True,
                                         blank=True)
    script_password = models.CharField(max_length=12, null=True,
                                       blank=True)
    team_select_password = models.CharField(max_length=12, null=True,
                                            blank=True)
    cast_audition_password = models.CharField(max_length=12,
                                              null=True, blank=True)
    logline = models.CharField(max_length=1000,  null=True, blank=True)
    project_info = models.TextField(_("Project Info"), null=True, blank=True)
    likes = models.IntegerField(_("Likes"), null=True, blank=True, default=0)
    dislikes = models.IntegerField(_("Dislikes"), null=True, blank=True, default=0)

    timestamp = models.DateField(auto_now_add=True)
    production = models.CharField(_("Production"),
                                  choices=PRODUCTION_CHOICES,
                                  max_length=150, default=SAGAFTRA)
    is_posted = models.BooleanField(
                        default=False,
                        verbose_name=_("Is posted")
                    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Draft Project'
        verbose_name_plural = 'Draft Projects'
