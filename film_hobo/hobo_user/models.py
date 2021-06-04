
import datetime

from phonenumber_field.modelfields import PhoneNumberField

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from solo.models import SingletonModel


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
        extra_fields.setdefault('membership', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    PRODUCTION = 'production'
    AGENCY_MANGEMENT = 'agency_management'
    AGENCY = 'agency'
    MANGEMENT = 'management'
    NA = ''
    ADMIN = 'ADMIN'
    HOBO = 'HOB'
    INDIE = 'IND'
    PRO = 'PRO'
    PRODUCTION_COMPANY = 'COM'
    COMPANY_TYPE_CHOICES = [
        (PRODUCTION, 'Production'),
        (AGENCY_MANGEMENT, 'Agency/Management'),
        (NA, 'NA'),
    ]
    AGENCY_MANGEMENT_TYPE_CHOICES = [
        (AGENCY, 'Agency'),
        (MANGEMENT, 'Management'),
        (NA, 'NA'),
    ]
    MEMBERSHIP_CHOICES = [
        (ADMIN, 'Admin'),
        (HOBO, 'Hobo'),
        (INDIE, 'Indie'),
        (PRO, 'Pro'),
        (PRODUCTION_COMPANY, 'Company')
    ]
    MONTHLY = 'monthly'
    ANNUALLY = 'annually'
    FREE = ''
    PAYMENT_PLAN_CHOICES = [
        (MONTHLY, 'Monthly'),
        (ANNUALLY, 'Annually'),
        (FREE, '-------')
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
    # bio = models.TextField(_("Bio"), null=True, blank=True)
    # imdb_url = models.URLField(_("IMDB URL"),
    #                            null=True,
    #                            blank=True)
    membership = models.CharField(_("Membership Type"),
                                  choices=MEMBERSHIP_CHOICES,
                                  max_length=150, default=HOBO)
    company_type = models.CharField(_("Company Type"),
                                    choices=COMPANY_TYPE_CHOICES,
                                    max_length=150, default=NA,
                                    null=True, blank=True)
    agency_management_type = models.CharField(
                            _("Agency/Management Type"),
                            choices=AGENCY_MANGEMENT_TYPE_CHOICES,
                            max_length=150, default=NA,
                            null=True, blank=True)
    i_agree = models.BooleanField(
        _('I Agree'),
        default=True,
        help_text=_(
            'Designates whether the user accepted the terms and conditions.'),
    )
    registration_complete = models.BooleanField(
        _('Registration Complete'),
        default=False,
        help_text=_(
            'Designates whether the user fully completed the registration.'),
    )
    company_name = models.CharField(_("Company Name"), max_length=500,
                                    null=True, blank=True)
    # company_address = models.TextField(_("Address"), null=True, blank=True)
    company_address = models.CharField(_("Company Address"),
                                       max_length=250,
                                       null=True, blank=True)
    company_website = models.URLField(_("Company Website"),
                                      null=True,
                                      blank=True,)
    company_phone = PhoneNumberField(_("Phone Number"), null=True,
                                     unique=True)
    title = models.CharField(_('Title'),
                             max_length=150, null=True, blank=True)
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
    phone_number = PhoneNumberField(_("Phone Number"), null=True,
                                    unique=True)
    date_of_birth = models.DateField(_("Date of Birth"),
                                     null=True)
    date_of_joining = models.DateField(_("Date of Joining"),
                                       default=datetime.date.today,
                                       null=True)
    # address = models.TextField(_("Address"), null=True)
    address = models.CharField(_("Address"),
                               max_length=250,
                               null=True)
    country = models.ForeignKey("hobo_user.Country",
                                on_delete=models.SET_NULL,
                                related_name='user_country',
                                verbose_name=_("Country"),
                                null=True)
    guild_membership = models.ManyToManyField('hobo_user.GuildMembership',
                                              blank=True,
                                              related_name='guild_membership',
                                              verbose_name=_("Guild Membership"
                                                             )
                                              )
    payment_plan = models.CharField(_("Payment Plan"),
                                    choices=PAYMENT_PLAN_CHOICES,
                                    max_length=150,
                                    null=True,
                                    default=FREE)
    # athletic_skills = models.ManyToManyField('hobo_user.AthleticSkill',
    #                                          blank=True,
    #                                          related_name='user_athletic_skills',
    #                                          verbose_name=_("Athletic Skills"
    #                                                         )
    #                                          )
    ethnic_appearance = models.ForeignKey('hobo_user.EthnicAppearance',
                                          on_delete=models.SET_NULL,
                                          related_name='user_ethnic_appearance',
                                          verbose_name=_("Ethnic Appearance"),
                                          null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        if self.is_superuser:
            name = "Admin"
        elif self.middle_name:
            name = self.first_name+" "+self.middle_name+" "+self.last_name
        else:
            name = self.first_name+" "+self.last_name
        return name

    def get_height_in_meters(self):
        if self.feet:
            feet = self.feet
            inch = (self.inch)/12
            in_feet = feet+inch
            in_meter = round(float(in_feet/3.281), 2)
        return in_meter

    def get_profile_photo(self):
        photo_obj = Photo.objects.filter(user=self).order_by('position').first()
        if photo_obj:
            image = photo_obj.image.url
            return image
        return ""

    @property
    def group_name(self):
        """
        Returns a group name based on the user's id to be used by Django Channels.
        """
        return "user_%s" % self.id


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
                                related_name="user_athletic_skills",
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
    FLAT_AMOUNT = 'flat_amount'
    PERCENTAGE = 'percentage'
    AMOUNT_TYPE = [
        (FLAT_AMOUNT, 'Flat Amount'),
        (PERCENTAGE, 'Percentage'),
    ]
    ADMIN = 'ADMIN'
    HOBO = 'HOB'
    INDIE = 'IND'
    PRO = 'PRO'
    PRODUCTION_COMPANY = 'COM'
    USER_TYPE_CHOICES = [
        (ADMIN, 'Admin'),
        (HOBO, 'Hobo'),
        (INDIE, 'Indie'),
        (PRO, 'Pro'),
        (PRODUCTION_COMPANY, 'Production Company')
    ]
    promo_code = models.CharField(max_length=1000, unique=True)
    created_time = models.DateTimeField(_('Created Time'), auto_now_add=True,
                                        blank=False)
    valid_from = models.DateTimeField(_('Valid From'), null=True, blank=True)
    valid_to = models.DateTimeField(_('Valid To'),
                                    null=True, blank=True)
    life_span = models.IntegerField(_('Valid for days'), null=True, blank=True)
    amount_type = models.CharField(_("Amount Type"),
                                   choices=AMOUNT_TYPE,
                                   max_length=150, default=FLAT_AMOUNT)
    amount = models.IntegerField(_('Amount'))
    user_type = models.CharField(_("User Type"),
                                 choices=USER_TYPE_CHOICES,
                                 max_length=150, default=HOBO)

    def __str__(self):
        return str(self.promo_code)


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

    def clean(self):
        country_match = Country.objects.filter(
            name=self.__dict__['name'])
        if country_match:
            raise ValidationError('country already exists')

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'


class GuildMembership(models.Model):
    membership = models.CharField(_("Membership Type"), max_length=250)

    def __str__(self):
        return str(self.membership)


class HoboPaymentsDetails(SingletonModel):
    free_days = models.CharField(_('First free days'), max_length=250,
                                 null=True, blank=True)
    annual_amount = models.FloatField(_('Annual billing amount'))
    annual_amount_with_tax = models.FloatField(
        _('Annual billing amount (with tax)'))
    monthly_amount = models.FloatField(_('Monthly billing amount'))
    monthly_amount_with_tax = models.FloatField(
        _('Monthly billing amount (with tax)'))
    estimated_tax = models.FloatField(_('Estimated Tax'))

    class Meta:
        verbose_name = 'Hobo Members Payment Detail'
        verbose_name_plural = 'Hobo Members Payment Details'

    def save(self, *args, **kwargs):
        self.annual_amount = round(self.annual_amount, 2)
        self.monthly_amount = round(self.monthly_amount, 2)
        self.estimated_tax = round(self.estimated_tax, 2)
        super(HoboPaymentsDetails, self).save(*args, **kwargs)


class IndiePaymentDetails(SingletonModel):
    free_days = models.CharField(_('First free days'), max_length=250)
    annual_amount = models.FloatField(_('Annual billing amount'))
    annual_amount_with_tax = models.FloatField(
        _('Annual billing amount (with tax)'))
    monthly_amount = models.FloatField(_('Monthly billing amount'))
    monthly_amount_with_tax = models.FloatField(
        _('Monthly billing amount (with tax)'))
    estimated_tax = models.FloatField(_('Estimated Tax'))

    class Meta:
        verbose_name = 'Indie Members Payment Detail'
        verbose_name_plural = 'Indie Members Payment Details'

    def save(self, *args, **kwargs):
        self.annual_amount = round(self.annual_amount, 2)
        self.monthly_amount = round(self.monthly_amount, 2)
        self.estimated_tax = round(self.estimated_tax, 2)
        super(IndiePaymentDetails, self).save(*args, **kwargs)


class ProPaymentDetails(SingletonModel):
    free_days = models.CharField(_('First free days'), max_length=250)
    annual_amount = models.FloatField(_('Annual billing amount'))
    annual_amount_with_tax = models.FloatField(
        _('Annual billing amount (with tax)'), )
    monthly_amount = models.FloatField(_('Monthly billing amount'))
    monthly_amount_with_tax = models.FloatField(
        _('Monthly billing amount (with tax)'))
    estimated_tax = models.FloatField(_('Estimated Tax'))

    class Meta:
        verbose_name = 'Pro Members Payment Detail'
        verbose_name_plural = 'Pro Members Payment Details'

    def save(self, *args, **kwargs):
        self.annual_amount = round(self.annual_amount, 2)
        self.monthly_amount = round(self.monthly_amount, 2)
        self.estimated_tax = round(self.estimated_tax, 2)
        super(ProPaymentDetails, self).save(*args, **kwargs)


class CompanyPaymentDetails(SingletonModel):
    free_days = models.CharField(_('First free days'), max_length=250)
    annual_amount = models.FloatField(_('Annual billing amount'))
    annual_amount_with_tax = models.FloatField(
        _('Annual billing amount (with tax)'))
    monthly_amount = models.FloatField(_('Monthly billing amount'))
    monthly_amount_with_tax = models.FloatField(
        _('Monthly billing amount (with tax)'))
    estimated_tax = models.FloatField(_('Estimated Tax'))

    class Meta:
        verbose_name = 'Company Payment Detail'
        verbose_name_plural = 'Company Payment Details'

    def save(self, *args, **kwargs):
        self.annual_amount = round(self.annual_amount, 2)
        self.monthly_amount = round(self.monthly_amount, 2)
        self.estimated_tax = round(self.estimated_tax, 2)
        super(CompanyPaymentDetails, self).save(*args, **kwargs)


class DisabledAccount(models.Model):
    REASON1 = 'reason1'
    REASON2 = 'reason2'
    REASON3 = 'reason3'
    REASON4 = 'reason4'
    REASON5 = 'reason5'
    REASON_CHOICES = [
        (REASON1, "I don't get any values from the network"),
        (REASON2, "I lost my interest"),
        (REASON3, "I have a privacy concern"),
        (REASON4, "It is too expensive for me"),
        (REASON5, "Other")
    ]
    user = models.ForeignKey("hobo_user.CustomUser",
                             on_delete=models.CASCADE,
                             related_name='disabled_user',
                             verbose_name=_("User"),
                             null=True)

    reason = models.CharField(_("Reason"),
                              choices=REASON_CHOICES,
                              max_length=150, default=REASON1)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'Disabled Account'
        verbose_name_plural = 'Disabled Accounts'


class CustomUserSettings(models.Model):
    ENABLED = 'enabled'
    DISABLED = 'disabled'

    MEMBERS_WITH_RATING_1_STAR = 'members_with_rating_1_star'
    MEMBERS_WITH_RATING_2_STAR = 'members_with_rating_2_star'
    MEMBERS_WITH_RATING_3_STAR = 'members_with_rating_3_star'
    MEMBERS_WITH_RATING_4_STAR = 'members_with_rating_4_star'
    MEMBERS_WITH_RATING_5_STAR = 'members_with_rating_5_star'
    PROS_AND_COMPANIES_ONLY = 'pros_and_companies_only'
    NO_ONE = 'no_one'
    ALL_MEMBERS = 'all_members'
    PROS_AND_COMPANIES_ONLY = 'pros_and_companies_only'

    ACCOUNT_STATUS_CHOICES = [
        (ENABLED, 'Enabled'),
        (DISABLED, 'Disabled'),
    ]

    PROFILE_VISIBILITY_CHOICES = [
        (ALL_MEMBERS, 'All Members'),
        (PROS_AND_COMPANIES_ONLY, 'Pros and Companies Only'),
        (MEMBERS_WITH_RATING_1_STAR, 'Members with rating 1 star'),
        (MEMBERS_WITH_RATING_2_STAR, 'Members with rating 2 star'),
        (MEMBERS_WITH_RATING_3_STAR, 'Members with rating 3 star'),
        (MEMBERS_WITH_RATING_4_STAR, 'Members with rating 4 star'),
        (MEMBERS_WITH_RATING_5_STAR, 'Members with rating 5 star'),
        (NO_ONE, 'No One'),
    ]

    CONTACT_CHOICES = [
        (MEMBERS_WITH_RATING_1_STAR, 'Members with rating 1 star'),
        (MEMBERS_WITH_RATING_2_STAR, 'Members with rating 2 star'),
        (MEMBERS_WITH_RATING_3_STAR, 'Members with rating 3 star'),
        (MEMBERS_WITH_RATING_4_STAR, 'Members with rating 4 star'),
        (MEMBERS_WITH_RATING_5_STAR, 'Members with rating 5 star'),
        (PROS_AND_COMPANIES_ONLY, 'Pros and Companies Only'),
        (NO_ONE, 'No One'),
    ]

    TRACKING_CHOICES = [
        (ALL_MEMBERS, 'All Members'),
        (MEMBERS_WITH_RATING_1_STAR, 'Members with rating 1 star'),
        (MEMBERS_WITH_RATING_2_STAR, 'Members with rating 2 star'),
        (MEMBERS_WITH_RATING_3_STAR, 'Members with rating 3 star'),
        (MEMBERS_WITH_RATING_4_STAR, 'Members with rating 4 star'),
        (MEMBERS_WITH_RATING_5_STAR, 'Members with rating 5 star'),
        (PROS_AND_COMPANIES_ONLY, 'Pros and Companies Only'),
        (NO_ONE, 'No One'),
    ]

    account_status = models.CharField(_("Account Status"),
                                      choices=ACCOUNT_STATUS_CHOICES,
                                      max_length=150, default=ENABLED)
    user = models.ForeignKey("hobo_user.CustomUser",
                             on_delete=models.CASCADE,
                             related_name='user_settings',
                             verbose_name=_("User"),
                             null=True)
    profile_visibility = models.CharField(_("Who can see my Profile"),
                                          choices=PROFILE_VISIBILITY_CHOICES,
                                          max_length=150, default=ALL_MEMBERS)
    who_can_contact_me = models.CharField(_("Who can contact me"),
                                          choices=CONTACT_CHOICES,
                                          max_length=150,
                                          default=MEMBERS_WITH_RATING_1_STAR)
    who_can_track_me = models.CharField(_("Who can track me"),
                                        choices=TRACKING_CHOICES,
                                        max_length=150,
                                        default=ALL_MEMBERS)
    blocked_members = models.ManyToManyField('hobo_user.CustomUser',
                                             blank=True,
                                             related_name="blocked_users",
                                             verbose_name=_("Blocked Members"))
    someone_tracks_me = models.BooleanField(
        default=True,
        verbose_name=_("If someone tracks me")
        )
    change_in_my_or_project_rating = models.BooleanField(
        default=True,
        verbose_name=_("If there was a change in my or my project’s rating")
        )
    review_for_my_work_or_project = models.BooleanField(
        default=True,
        verbose_name=_("If someone posted a review for my work or my project")
        )
    new_project = models.BooleanField(
        default=True,
        verbose_name=_("If someone I track has started a new project or got attached to a project")
        )
    friend_request = models.BooleanField(
        default=True,
        verbose_name=_("If someone sends me a friend request")
        )
    match_for_my_Interest = models.BooleanField(
        default=True,
        verbose_name=_("If I’ve got a match for my Interest")
        )

    class Meta:
        verbose_name = 'Custom User Settings'
        verbose_name_plural = 'Custom User Settings'

    def __str__(self):
        return str(self.user)


class JobType(models.Model):
    title = models.CharField(max_length=1000)

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = 'Job Type'
        verbose_name_plural = 'Job Types'


class NewJobType(models.Model):
    title = models.CharField(max_length=1000)

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = 'New Job Type'
        verbose_name_plural = 'New Job Types'


class UserProfile(models.Model):
    user = models.ForeignKey("hobo_user.CustomUser",
                             on_delete=models.CASCADE,
                             related_name='user_profile',
                             verbose_name=_("User"),
                             null=True)
    job_types = models.ManyToManyField('hobo_user.JobType',
                                       blank=True,
                                       related_name="user_job_types",
                                       verbose_name=_("Job Types")
                                       )
    company = models.CharField(_('Company'),
                               max_length=150,
                               null=True,
                               blank=True
                               )
    company_position = models.CharField(_('Company Position'),
                                        max_length=150,
                                        null=True,
                                        blank=True
                                        )
    company_website = models.CharField(_('Company Website'),
                                       max_length=150,
                                       null=True,
                                       blank=True
                                       )
    imdb = models.CharField(_("IMDB"),
                            max_length=150,
                            null=True,
                            blank=True
                            )
    bio = models.TextField(_("Bio/Info"), null=True, blank=True)

    def __str__(self):
        return str(self.user.email)

    def update_job_type(self, job_id):
        job_types = self.job_types.all()
        job_types = list(job_types)
        job = JobType.objects.get(id=job_id)
        if job not in job_types:
            job_types.append(job)
            self.job_types.set(job_types)
        return str(self.user.email)

    def remove_job_type(self, job_id):
        job_types = self.job_types.all()
        job_types = list(job_types)
        job = JobType.objects.get(id=job_id)
        if job in job_types:
            job_types.remove(job)
            self.job_types.set(job_types)
        return str(self.user.email)


class CompanyProfile(models.Model):
    MEMBERS_WITH_RATING_1_STAR = 'members_with_rating_1_star'
    MEMBERS_WITH_RATING_2_STAR = 'members_with_rating_2_star'
    MEMBERS_WITH_RATING_3_STAR = 'members_with_rating_3_star'
    MEMBERS_WITH_RATING_4_STAR = 'members_with_rating_4_star'
    MEMBERS_WITH_RATING_5_STAR = 'members_with_rating_5_star'
    PROS_AND_COMPANIES_ONLY = 'pros_and_companies_only'
    SAMR_CHOICES = [
                        (MEMBERS_WITH_RATING_1_STAR, 'Members with rating 1 star'),
                        (MEMBERS_WITH_RATING_2_STAR, 'Members with rating 2 star'),
                        (MEMBERS_WITH_RATING_3_STAR, 'Members with rating 3 star'),
                        (MEMBERS_WITH_RATING_4_STAR, 'Members with rating 4 star'),
                        (MEMBERS_WITH_RATING_5_STAR, 'Members with rating 5 star'),
                        (PROS_AND_COMPANIES_ONLY, 'Pros and Companies Only')
                    ]
    user = models.ForeignKey("hobo_user.CustomUser",
                             on_delete=models.CASCADE,
                             related_name='company_profile',
                             verbose_name=_("User"),
                             null=True)
    imdb = models.CharField(_("IMDB"),
                            max_length=150,
                            null=True,
                            blank=True
                            )
    bio = models.TextField(_("Bio/Info"), null=True, blank=True)
    submission_policy_SAMR = models.CharField(_("SAMR"),
                                              choices=SAMR_CHOICES,
                                              max_length=150,
                                              default=PROS_AND_COMPANIES_ONLY)

    def __str__(self):
        return str(self.user.email)

    class Meta:
        verbose_name = 'Company Profile'
        verbose_name_plural = 'Company Profiles'


class CoWorker(models.Model):
    user = models.ForeignKey("hobo_user.CustomUser",
                             on_delete=models.CASCADE,
                             related_name='coworker',
                             verbose_name=_("User"),
                             null=True)
    company = models.ForeignKey("hobo_user.CustomUser",
                                on_delete=models.CASCADE,
                                related_name='company',
                                verbose_name=_("Company"),
                                null=True)
    name = models.CharField(_('Name'),
                            max_length=150,
                            null=True,
                            blank=True
                            )
    email = models.EmailField(_("Staff's email address"),
                              null=True,
                              blank=True)
    position = models.ForeignKey("hobo_user.JobType",
                                 on_delete=models.CASCADE,
                                 related_name='coworker',
                                 verbose_name=_("Position"),
                                 null=True)

    def __str__(self):
        return str(self.company.company_name)

    class Meta:
        verbose_name = 'Coworker'
        verbose_name_plural = 'Coworkers'


class CompanyClient(models.Model):
    user = models.ForeignKey("hobo_user.CustomUser",
                             on_delete=models.CASCADE,
                             related_name='client_user',
                             verbose_name=_("User"),
                             null=True, blank=True)
    company = models.ForeignKey("hobo_user.CustomUser",
                                on_delete=models.CASCADE,
                                related_name='company_agency_management_client',
                                verbose_name=_("Company"),
                                null=True)
    name = models.CharField(_('Name'),
                            max_length=150,
                            null=True,
                            blank=True
                            )
    email = models.EmailField(_("Staff's email address"),
                              null=True,
                              blank=True)
    position = models.ForeignKey("hobo_user.JobType",
                                 on_delete=models.SET_NULL,
                                 related_name='client_position',
                                 verbose_name=_("Position"),
                                 null=True)
    # new_position = models.ForeignKey("hobo_user.NewJobType",
    #                                  on_delete=models.SET_NULL,
    #                                  related_name='client_new_position',
    #                                  verbose_name=_("New Position"),
    #                                  null=True)
    new_position = models.CharField(_('New Position'),
                                    max_length=150,
                                    null=True,
                                    blank=True
                                    )

    def __str__(self):
        return str(self.company.company_name)

    class Meta:
        verbose_name = 'Company Client'
        verbose_name_plural = 'Company Clients'


class Location(models.Model):
    city = models.CharField(max_length=1000, verbose_name='City', null=True)
    state = models.CharField(max_length=1000, verbose_name='State', null=True)
    country = models.CharField(max_length=1000, verbose_name='Country', null=True)

    def __str__(self):
        location = self.city+","+self.state+","+self.country
        return str(location)

    class Meta:
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'


class UserInterest(models.Model):
    SCENE = 'scene'
    SHORT = 'short'
    PILOT = 'pilot'
    FEATURE = 'feature'
    FORMAT_CHOICES = [
                    (SCENE, 'Scene'),
                    (SHORT, 'Short Film'),
                    (PILOT, 'Pilot'),
                    (FEATURE, 'Feature'),
                    ]
    user = models.ForeignKey("hobo_user.CustomUser",
                             on_delete=models.CASCADE,
                             related_name='user_interest',
                             verbose_name=_("User"),
                             null=True)
    position = models.ForeignKey("hobo_user.JobType",
                                 on_delete=models.SET_NULL,
                                 related_name='user_interest_position',
                                 verbose_name=_("User"),
                                 null=True)
    format = models.CharField(_("Format"),
                              choices=FORMAT_CHOICES,
                              max_length=150,
                              default=SCENE, null=True)
    location = models.ForeignKey("hobo_user.Location",
                                 on_delete=models.SET_NULL,
                                 related_name='user_interest_location',
                                 verbose_name=_("Location"),
                                 null=True)


class UserRatingCombined(models.Model):
    user = models.ForeignKey("hobo_user.CustomUser",
                             on_delete=models.CASCADE,
                             related_name='user_rating',
                             verbose_name=_("User"),
                             null=True)
    job_type = models.ForeignKey('hobo_user.JobType',
                                 on_delete=models.CASCADE,
                                 related_name="user_job_type_rating_combined",
                                 verbose_name=_("Job Types")
                                 )
    rating = models.IntegerField(_("Rating"), null=True, blank=True)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'User Rating Combined'
        verbose_name_plural = 'User Rating Combined'


class UserRating(models.Model):
    user = models.ForeignKey("hobo_user.CustomUser",
                             on_delete=models.CASCADE,
                             related_name='user_rating_combined',
                             verbose_name=_("User"),
                             null=True)
    rated_by = models.ForeignKey("hobo_user.CustomUser",
                                 on_delete=models.CASCADE,
                                 related_name='rated_by_user',
                                 verbose_name=_("Rated by"),
                                 null=True)
    job_type = models.ForeignKey('hobo_user.JobType',
                                 on_delete=models.CASCADE,
                                 related_name="user_job_type_rating",
                                 verbose_name=_("Job Types")
                                 )
    rating = models.IntegerField(_("Rating"), null=True, blank=True)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'User Rating'
        verbose_name_plural = 'User Rating'


class UserTacking(models.Model):
    user = models.ForeignKey("hobo_user.CustomUser",
                             on_delete=models.CASCADE,
                             related_name='user_tracking',
                             verbose_name=_("User"),
                             null=True)
    tracked_by = models.ManyToManyField('hobo_user.CustomUser',
                                        blank=True,
                                        related_name="tracked_by",
                                        verbose_name=_("Tracked by")
                                        )

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'User Tracking'
        verbose_name_plural = 'User Tracking'


class FriendRequest(models.Model):
    ACCEPTED = 'accepted'
    REQUEST_SEND = 'request_send'
    STATUS_CHOICES = [
        (ACCEPTED, 'Accepted'),
        (REQUEST_SEND, 'Request Send'),
    ]
    status = models.CharField(_("Account Status"),
                              choices=STATUS_CHOICES,
                              max_length=150, default=REQUEST_SEND)
    user = models.ForeignKey("hobo_user.CustomUser",
                             on_delete=models.CASCADE,
                             related_name='user_friend_request',
                             verbose_name=_("User"),
                             null=True)
    requested_by = models.ForeignKey("hobo_user.CustomUser",
                                     on_delete=models.CASCADE,
                                     related_name='requested_by',
                                     verbose_name=_("Requested by"),
                                     null=True)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'Friend Request'
        verbose_name_plural = 'Friend Requests'


class UserAgentManager(models.Model):
    AGENT = 'agent'
    MANAGER = 'manager'
    AGENT_TYPE_CHOICES = [
        (AGENT, 'Agent'),
        (MANAGER, 'Manager'),
    ]
    agent_type = models.CharField(_("Agent Type"),
                                  choices=AGENT_TYPE_CHOICES,
                                  max_length=150, default=AGENT)
    user = models.ForeignKey("hobo_user.CustomUser",
                             on_delete=models.CASCADE,
                             related_name='user_agent',
                             verbose_name=_("User"),
                             null=True)
    agent_name = models.CharField(_('Name'),
                                  max_length=150,
                                  null=True,
                                  blank=True
                                  )
    agent_phone = PhoneNumberField(_("Agent's phone number"),
                                   null=True,
                                   blank=True
                                   )
    agent_email = models.EmailField(_("Agent's email address"),
                                    null=True,
                                    blank=True)
    agent_job_type = models.CharField(_('Agent Job Type'),
                                      max_length=150,
                                      null=True,
                                      blank=True
                                      )

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'User Agent/Manager'
        verbose_name_plural = 'User Agents/Managers'


class Photo(models.Model):
    user = models.ForeignKey("hobo_user.CustomUser",
                             on_delete=models.CASCADE,
                             related_name='user_photo',
                             verbose_name=_("User"),
                             null=True)
    position = models.IntegerField(_("Position"), null=True, blank=True)
    image = models.ImageField(upload_to='gallery/',
                              blank=True, null=True,
                              help_text="Image size:370 X 248.")

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'


class UserNotification(models.Model):
    TRACKING = 'tracking'
    FRIEND_REQUEST = 'friend_request'
    USER_RATING = 'user_rating'
    READ = 'read'
    UNREAD = 'unread'
    NOTIFICATION_TYPE_CHOICES = [
                                (TRACKING, 'Tracking'),
                                (FRIEND_REQUEST, 'Friend Request'),
                                (USER_RATING, 'User Rating'),
                               ]
    STATUS_CHOICES = [
                    (READ, 'Read'),
                    (UNREAD, 'Unread'),
                    ]
    user = models.ForeignKey("hobo_user.CustomUser",
                             on_delete=models.CASCADE,
                             related_name='notification_to',
                             verbose_name=_("User"),
                             null=True)
    notification_type = models.CharField(_("Notification Type"),
                                         choices=NOTIFICATION_TYPE_CHOICES,
                                         max_length=150, default=TRACKING)
    from_user = models.ForeignKey("hobo_user.CustomUser",
                                  on_delete=models.CASCADE,
                                  related_name='notification_from',
                                  verbose_name=_("Notifications from"),
                                  null=True)
    status_type = models.CharField(_("Status Type"),
                                   choices=STATUS_CHOICES,
                                   max_length=150, default=UNREAD)
    created_time = models.DateTimeField(_('Created Time'), auto_now_add=True,
                                        blank=False)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'User Notification'
        verbose_name_plural = 'User Notifications'