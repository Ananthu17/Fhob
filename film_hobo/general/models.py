from django.db import models
from hobo_user.models import CustomUser
from django.utils.translation import ugettext_lazy as _


class Help(models.Model):
    user = models.ForeignKey("hobo_user.CustomUser",
                             on_delete=models.CASCADE,
                             related_name='help_user',
                             verbose_name=_("User"),
                             null=True)
    subject = models.CharField(_('Subject'),
                               max_length=150)
    description = models.TextField(_("Description"))
    screenshot = models.ImageField(upload_to='gallery/help',
                                   blank=True, null=True,
                                   help_text="Attach screenshot to describe your problem.")
    timestamp = models.DateTimeField(_('Created Time'), auto_now_add=True,
                                     blank=False)

    class Meta:
        verbose_name = 'Help'
        verbose_name_plural = 'Help'

    def __str__(self):
        title = str(self.user.get_full_name())+"-"+str(self.subject)
        return str(title)


class EmailUs(models.Model):
    General = 'general'
    Technical = 'technical'
    Sevices = 'services'
    Abuse = 'abuse'
    Business = 'business'
    TOPIC_CHOICES = [
                    (General, 'General'),
                    (Technical, 'Technical'),
                    (Abuse, 'Abuse'),
                    (Sevices, 'Sevices'),
                    (Business, 'Business'),
                    ]
    topic = models.CharField(_("Topic"),
                             choices=TOPIC_CHOICES,
                             max_length=150,
                             null=True, blank=True)
    user = models.ForeignKey("hobo_user.CustomUser",
                             on_delete=models.CASCADE,
                             related_name='email_from_user',
                             verbose_name=_("User"),
                             null=True)
    subject = models.CharField(_('Subject'),
                               max_length=150)
    message = models.TextField(_("Message"))

    class Meta:
        verbose_name = 'Email'
        verbose_name_plural = 'Emails'

    def __str__(self):
        return str(self.user)


class ReportProblem(models.Model):
    user_email = models.EmailField(_('Email'))
    name = models.CharField(_('Name'),
                            max_length=150, null=True, blank=True)
    user_phone = models.CharField(_("Phone Number"),
                                     max_length=16, null=True,
                                      blank=False)
    user_problem = models.TextField(_("User Problem"), blank=True, null=True)

    timestamp = models.DateTimeField(_('Created Time'), auto_now_add=True,
                                     blank=False)

    class Meta:
        verbose_name = 'ReportProblem'
        verbose_name_plural = 'ReportProblems'

