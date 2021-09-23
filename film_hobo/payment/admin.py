from django.contrib import admin

from .models import PaymentOptions, Transaction, FilmHoboSenderEmail, \
    EmailRecord

# Register your models here.

admin.site.register(PaymentOptions)
admin.site.register(Transaction)
admin.site.register(FilmHoboSenderEmail)
admin.site.register(EmailRecord)
