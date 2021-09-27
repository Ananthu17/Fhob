from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from solo.models import SingletonModel

from hobo_user.models import CustomUser

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
    PAYPAL_ACCOUNT = 'paypal_account'
    CARD_PAYMENT = 'card_payment'
    PAYMENT_METHOD_CHOICES = [
        (PAYPAL_ACCOUNT, 'PayPal Account'),
        (CARD_PAYMENT, 'Card Payment')
    ]
    MONTHLY = 'monthly'
    ANNUALLY = 'annually'
    PAYMENT_PLAN_CHOICES = [
        (MONTHLY, 'Monthly'),
        (ANNUALLY, 'Annually')
    ]
    ADMIN = 'ADMIN'
    HOBO = 'HOB'
    INDIE = 'IND'
    PRO = 'PRO'
    PRODUCTION_COMPANY = 'COM'
    MEMBERSHIP_CHOICES = [
        (ADMIN, 'Admin'),
        (HOBO, 'Hobo'),
        (INDIE, 'Indie'),
        (PRO, 'Pro'),
        (PRODUCTION_COMPANY, 'Production Company')
    ]

    user = models.ForeignKey('hobo_user.CustomUser',
                             verbose_name=_("User"),
                             on_delete=models.CASCADE)
    payment_method = models.CharField(_("Payment Method"),
                                      choices=PAYMENT_METHOD_CHOICES,
                                      max_length=150,
                                      null=True)
    paypal_order_id = models.CharField(_("Paypal Order ID"),
                                       null=True, blank=True, max_length=150)
    date = models.DateTimeField(auto_now_add=True)
    days_free = models.IntegerField(_("Days Free"), null=True, blank=True)
    membership = models.CharField(_("Membership Type"),
                                  choices=MEMBERSHIP_CHOICES,
                                  max_length=150, default=HOBO)
    payment_plan = models.CharField(_("Payment Plan"),
                                    choices=PAYMENT_PLAN_CHOICES,
                                    max_length=150,
                                    null=True)
    initial_amount = models.FloatField(_("Initial Amount"))
    tax_applied = models.FloatField(_("Tax"), null=True, blank=True)
    promocodes_applied = models.ForeignKey(
        'hobo_user.Promocode', verbose_name=_("Promocodes Applied"),
        null=True, blank=True, on_delete=models.CASCADE)
    promotion_amount = models.FloatField(_("Promotion Amount"),
                                         null=True, blank=True)
    final_amount = models.FloatField(_("Final Amount"))
    paid = models.BooleanField(default=False)

    def __str__(self):
        return "{}:{}".format(self.id, self.user.email)


class FilmHoboSenderEmail(models.Model):
    """
    Model to store all the sender emails.
    """
    email = models.EmailField(_('Email'))

    class Meta:
        verbose_name = 'Sender Email'
        verbose_name_plural = 'Sender Emails'

    def __str__(self):
        return "{}:{}".format(self.id, self.email)


class EmailRecord(models.Model):
    """
    Model to store all the outgoing emails.
    """

    when = models.DateTimeField(null=False, auto_now_add=True)
    sender = models.ForeignKey(
        FilmHoboSenderEmail,
        related_name="sent_messages",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    recipient = models.ForeignKey(
        CustomUser,
        related_name="recv_messages",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    email = models.EmailField(null=False, blank=False)
    subject = models.CharField(null=False, max_length=128)
    sent = models.BooleanField(null=False, default=False)


def change_registration_complete_to_true(sender, instance, **kwargs):
    paid_user_obj = CustomUser.objects.get(email=instance.user.email)
    paid_user_obj.registration_complete = True
    paid_user_obj.save()


post_save.connect(change_registration_complete_to_true, sender=Transaction)
