from django.db import models
from django.utils.translation import ugettext_lazy as _


class Character(models.Model):
    name = models.CharField(max_length=1000)
    project = models.ForeignKey('hobo_user.Project',
                                verbose_name=_("Project"),
                                on_delete=models.CASCADE)
    description = models.TextField(_("Description"), null=True, blank=True)
    password = models.CharField(max_length=50, null=True, blank=True)

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
    scene_1 = models.TextField(_("Scene Description"),
                               null=True, blank=True)
    scene_2 = models.TextField(_("Scene Description"),
                               null=True, blank=True)
    scene_3 = models.TextField(_("Scene Description"),
                               null=True, blank=True)

    def __str__(self):
        return self.project.title+" - "+self.character.name+" - sides"

    class Meta:
        verbose_name = 'Sides'
        verbose_name_plural = 'Sides'
