from django.db import models
from django.utils.translation import ugettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField


class Designation(models.Model):
    title = models.CharField(max_length=30)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class InitialIntrestedUsers(models.Model):
    """
    database table to store basic details of initial intrested users
    """
    first_name = models.CharField(_('First Name'), max_length=150)
    middle_name = models.CharField(_('Middle Name'),
                                   max_length=150, blank=True)
    last_name = models.CharField(_('Last Name'), max_length=150)
    email = models.EmailField(_('Email Address'), unique=True)
    phone = PhoneNumberField(_('Contact Phone Number'), unique=True,
                             blank=True)
    designation = models.ManyToManyField(Designation,
                                         verbose_name=_('Designations'),
                                         blank=True,
                                         related_name="user_designation"
                                         )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email
