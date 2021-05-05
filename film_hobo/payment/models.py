from django.db import models

# Create your models here.


class MembershipFee(models.Model):
    monthyly_hobo = models.IntegerField()
    monthyly_indie = models.IntegerField()
    monthyly_pro = models.IntegerField()
    monthyly_company = models.IntegerField()
    annual_hobo = models.IntegerField()
    annual_indie = models.IntegerField()
    annual_pro = models.IntegerField()
    annual_company = models.IntegerField()
