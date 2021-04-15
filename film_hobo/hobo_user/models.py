
from datetime import date
from phonenumber_field.modelfields import PhoneNumberField

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(username=email, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    HOBO = 'HOB'
    INDIE = 'IND'
    PRO = 'PRO'
    PRODUCTION_COMPANY = 'COM'
    MEMBERSHIP_CHOICES = [
        (HOBO, 'Hobo'),
        (INDIE, 'Indie'),
        (PRO, 'Pro'),
        (PRODUCTION_COMPANY, 'Production Company')
    ]

    MALE = 'MAL'
    FEMALE = 'FEM'
    OTHER = 'OTH'
    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHER, 'Other')
    ]

    ATHLETIC = 'ATH'
    SLENDER = 'SLE'
    MEDIUM = 'MED'
    HEAVY = 'HEA'
    PHYSIQUE_CHOICES = [
        (ATHLETIC, 'Athletic'),
        (SLENDER, 'Slender'),
        (MEDIUM, 'Medium'),
        (HEAVY, 'Heavy')
    ]

    AUBURN_OR_RED = 'AUR'
    BLACK = 'BLA'
    BLONDE = 'BLO'
    BROWN = 'BRO'
    SALT_AND_PEPPER = 'SAP'
    GRAY_OR_WHITE = 'GOW'
    HAIR_COLOR_CHOICES = [
        (AUBURN_OR_RED, 'Auburn/Red'),
        (BLACK, 'Black'),
        (BLONDE, 'Blonde'),
        (BROWN, 'Brown'),
        (SALT_AND_PEPPER, 'Salt and Pepper'),
        (GRAY_OR_WHITE, 'Gray/White')
    ]

    BALD_OR_SHAVED = 'BOS'
    SHORT = 'SHO'
    MEDIUM = 'MED'
    LONG = 'LON'
    CURLY = 'CUR'
    AFRO = 'AFR'
    HAIR_LENGTH_CHOICES = [
        (BALD_OR_SHAVED, 'Bald/Shaved'),
        (SHORT, 'Short'),
        (MEDIUM, 'Medium'),
        (LONG, 'Long'),
        (CURLY, 'Curly'),
        (AFRO, 'Afro')
    ]

    BLACK = 'BLK'
    BROWN = 'BRO'
    BLUE = 'BLU'
    GREEN = 'GRE'
    HASEL = 'HAS'
    EYES_CHOICES = [
        (BLACK, 'Black'),
        (BROWN, 'Brown'),
        (BLUE, 'Blue'),
        (GREEN, 'Green'),
        (HASEL, 'Hasel')
    ]

    first_name = models.CharField(_('First Name'),
                                  max_length=150, null=True, blank=True)
    middle_name = models.CharField(_('Middle Name'),
                                   max_length=150, null=True, blank=True)
    last_name = models.CharField(_('Last Name'),
                                 max_length=150, null=True, blank=True)
    email = models.EmailField(_('Email'), unique=True)
    bio = models.TextField(_("Bio"), null=True, blank=True)
    imdb_url = models.URLField(_("IMDB URL"),
                               null=True,
                               blank=True)
    membership = models.CharField(_("Membership Type"),
                                  choices=MEMBERSHIP_CHOICES,
                                  max_length=150, default=HOBO)
    i_agree = models.BooleanField(
        _('I Agree'),
        default=True,
        help_text=_(
            'Designates whether the user accepted the terms and conditions.'),
    )
    acting_skill = models.FloatField(_("Acting Skill"), null=True, blank=True)
    directional_skill = models.FloatField(_("Directional Skill"), null=True,
                                          blank=True)
    writing_skill = models.FloatField(_("Writing Skill"), null=True,
                                      blank=True)
    production_skill = models.FloatField(_("Production Skill"),
                                         null=True, blank=True)
    gender = models.CharField(_("Gender"), choices=GENDER_CHOICES,
                              max_length=150, null=True, blank=True)
    feet = models.IntegerField(_("Feet"),
                               null=True, blank=True)
    inch = models.IntegerField(_("Inches"),
                               null=True, blank=True)
    lbs = models.IntegerField(_("Lbs"),
                              null=True, blank=True)
    start_age = models.IntegerField(_("From"),
                                    null=True, blank=True)
    stop_age = models.IntegerField(_("To"),
                                   null=True, blank=True)
    physique = models.CharField(_("Physique"),
                                choices=PHYSIQUE_CHOICES,
                                max_length=150,
                                null=True, blank=True)
    hair_color = models.CharField(_("Hair Color"),
                                  choices=HAIR_COLOR_CHOICES,
                                  max_length=150,
                                  null=True, blank=True)
    hair_length = models.CharField(_("Hair Length"),
                                   choices=HAIR_LENGTH_CHOICES,
                                   max_length=150,
                                   null=True, blank=True)
    eyes = models.CharField(_("Eyes"),
                            choices=EYES_CHOICES, max_length=150,
                            null=True, blank=True)
    phone_number = PhoneNumberField(_("Phone Number"),null=True,
                                blank=True, unique=True)
    date_of_birth = models.DateField(_("Date of Birth"),default=date.today,
                                blank=True, null=True)
    address = models.TextField(_("Address"), null=True, blank=True)
    country = models.ForeignKey("hobo_user.Country",
                        on_delete=models.SET_NULL,
                        related_name = 'user_country',
                        verbose_name=_("Country"),
                        blank=True, null=True)
    # address = models.CharField(_("Address"), max_length=1024, null=True,
    #                            blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class EthnicAppearance(models.Model):
    ethnic_appearance = models.CharField(_("Ethnic Appearance"),
                                         max_length=150,
                                         null=True, blank=True)

    def clean(self):
        ethnic_appearance_match = EthnicAppearance.objects.filter(
            ethnic_appearance=self.__dict__['ethnic_appearance'])
        if ethnic_appearance_match:
            raise ValidationError('ethnic appearance already exists')

    def __str__(self):
        return str(self.ethnic_appearance)


class EthnicAppearanceInline(models.Model):
    creator = models.ForeignKey('hobo_user.CustomUser',
                                verbose_name=_("Creator"),
                                on_delete=models.CASCADE)
    ethnic_appearance = models.ForeignKey("hobo_user.EthnicAppearance",
                                          on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Ethnic Appearance'
        verbose_name_plural = 'EthnicAppearances'
        unique_together = [("creator", "ethnic_appearance")]

    def __str__(self):
        return str(self.id)


class AthleticSkill(models.Model):
    athletic_skill = models.CharField(_("Athletic Skills"),
                                      max_length=150,
                                      null=True, blank=True)

    def clean(self):
        athletic_skill_match = AthleticSkill.objects.filter(
            athletic_skill=self.__dict__['athletic_skill'])
        if athletic_skill_match:
            raise ValidationError('athletic skill already exists')

    def __str__(self):
        return str(self.athletic_skill)


class AthleticSkillInline(models.Model):
    creator = models.ForeignKey('hobo_user.CustomUser',
                                verbose_name=_("Creator"),
                                on_delete=models.CASCADE)
    athletic_skill = models.ForeignKey("hobo_user.AthleticSkill",
                                       on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Athletic Skill'
        verbose_name_plural = 'Athletic Skills'
        unique_together = [("creator", "athletic_skill")]

    def __str__(self):
        return str(self.id)


class Project(models.Model):
    """
    A model to store all project related details
    """
    SCENE = 'SCH'
    SHORTS = 'SHO'
    FORMAT_CHOICES = [
        (SCENE, 'Scene'),
        (SHORTS, 'Shorts'),
    ]

    ACTION = 'ACT'
    ADVENTURE = 'ADV'
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
    MYSTERY = 'MYS'
    REALITY_TV = 'REA'
    ROMANCE = 'ROM'
    SCIENCE_FICTION = 'SCI'
    SPORT = 'SPO'
    TALK_SHOW = 'TAL'
    THRILLER = 'THR'
    WESTERN = 'WES'
    GENRE_CHOICES = [
        (ACTION, 'Action'),
        (ADVENTURE, 'Adventure'),
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
        (MYSTERY, 'Mystery'),
        (REALITY_TV, 'Reality TV'),
        (ROMANCE, 'Romance'),
        (SCIENCE_FICTION, 'Science Fiction'),
        (SPORT, 'Sport'),
        (TALK_SHOW, 'Talk Show'),
        (THRILLER, 'Thriller'),
        (WESTERN, 'Western')
    ]

    creator = models.ForeignKey('hobo_user.CustomUser',
                                verbose_name=_("Creator"),
                                on_delete=models.CASCADE)
    title = models.CharField(max_length=1000)
    format = models.CharField(_("Format Type"),
                              choices=FORMAT_CHOICES,
                              max_length=150, null=True, blank=True)
    genre = models.CharField(_("Genre Type"),
                             choices=GENRE_CHOICES,
                             max_length=150, null=True, blank=True)
    rating = models.FloatField(_("Rating"), null=True, blank=True)
    actor = models.ForeignKey('hobo_user.Actor', verbose_name=_("Actor"),
                              on_delete=models.CASCADE)
    writer = models.ForeignKey('hobo_user.Writer', verbose_name=_("Writer"),
                               on_delete=models.CASCADE)
    producer = models.ForeignKey('hobo_user.Producer',
                                 verbose_name=_("Producer"),
                                 on_delete=models.CASCADE)
    director = models.ForeignKey('hobo_user.Director',
                                 verbose_name=_("Director"),
                                 on_delete=models.CASCADE)
    editor = models.ForeignKey('hobo_user.Editor', verbose_name=_("Editor"),
                               on_delete=models.CASCADE)
    makeup = models.ForeignKey('hobo_user.Makeup', verbose_name=_("Makeup"),
                               on_delete=models.CASCADE)


class ProjectReaction(models.Model):
    creator = models.ForeignKey('hobo_user.CustomUser',
                                verbose_name=_("Creator"),
                                on_delete=models.CASCADE)
    project = models.ForeignKey('hobo_user.Project', verbose_name=_("Project"),
                                on_delete=models.CASCADE)
    likes = models.IntegerField(_("Likes"), null=True, blank=True)
    comment = models.TextField(_("Comment"), null=True, blank=True)
    created_time = models.DateTimeField(_('Created Time'), auto_now_add=True,
                                        blank=False)


class PromoCode(models.Model):
    promo_code = models.CharField(max_length=1000)
    created_time = models.DateTimeField(_('Created Time'), auto_now_add=True,
                                        blank=False)


class Team(models.Model):
    team = models.CharField(max_length=1000)


class Actor(models.Model):
    actor = models.CharField(max_length=1000)


class Writer(models.Model):
    writer = models.CharField(max_length=1000)


class Producer(models.Model):
    producer = models.CharField(max_length=1000)


class Director(models.Model):
    director = models.CharField(max_length=1000)


class Editor(models.Model):
    editor = models.CharField(max_length=1000)


class Makeup(models.Model):
    makeup = models.CharField(max_length=1000)


class Country(models.Model):
    name = models.CharField(max_length=1000)

    def __str__(self):
        return str(self.name)
    
    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'