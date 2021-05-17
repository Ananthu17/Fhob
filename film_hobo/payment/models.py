from django.db import models
from django.utils.translation import ugettext_lazy as _

from solo.models import SingletonModel

# Create your models here.


class PaymentOptions(SingletonModel):
    ON = 'ON'
    OFF = 'OFF'
    RENEW_CHOICES = [
        (ON, 'On'),
        (OFF, 'Off')
    ]

    tax = models.FloatField(_("Tax"),
                            default=0)
    free_evaluation_time = models.IntegerField(_("Free Evaluation Time"),
                                               default=0)
    auto_renew = models.CharField(_("Auto Renew"), choices=RENEW_CHOICES,
                                  max_length=10, default=OFF)

    class Meta:
        verbose_name = 'Payment Option'
        verbose_name_plural = 'Payment Options'
