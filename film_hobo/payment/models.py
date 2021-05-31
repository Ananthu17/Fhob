from django.db import models
from django.utils.translation import ugettext_lazy as _

from solo.models import SingletonModel

from hobo_user.models import PromoCode

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


class Transaction(models.Model):
    MONTHLY = 'monthly'
    ANNUALLY = 'annually'
    PAYMENT_PLAN_CHOICES = [
        (MONTHLY, 'Monthly'),
        (ANNUALLY, 'Annually')
    ]

    user = models.ForeignKey('hobo_user.CustomUser',
                             verbose_name=_("User"),
                             on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    payment_plan = models.CharField(_("Payment Plan"),
                                    choices=PAYMENT_PLAN_CHOICES,
                                    max_length=150,
                                    null=True)
    initial_amount = models.FloatField(_("Initial Amount"))
    promocodes_applied = models.OneToOneField(
        PromoCode, on_delete=models.CASCADE)
    promotion_amount = models.FloatField(_("Promotion Amount"))
    final_amount = models.FloatField(_("Final Amount"))
    paid = models.BooleanField(default=False)

    def __str__(self):
        return "{}:{}".format(self.id, self.user.email)
