import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _


class UserMessage(models.Model):
    from_user = models.ForeignKey('hobo_user.CustomUser',
                                  verbose_name=_("From"),
                                  related_name='message_from_user',
                                  on_delete=models.CASCADE)
    to_user = models.ForeignKey('hobo_user.CustomUser',
                                verbose_name=_("To"),
                                related_name='message_to_user',
                                on_delete=models.CASCADE)
    subject = models.CharField(_("Subject"),
                               max_length=1000,
                               null=True, blank=True)
    message = models.TextField(_("Message"))
    created_time = models.DateTimeField(_('Created Time'),
                                        default=datetime.datetime.now,
                                        blank=False)

    def __str__(self):
        return self.to_user.get_full_name()

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
