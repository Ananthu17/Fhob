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
