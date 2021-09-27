from django.contrib import admin

from .models import PaymentOptions, Transaction, FilmHoboSenderEmail, \
    EmailRecord
from hobo_user.importexport import FilmHoboSenderEmailResource
from import_export.admin import ImportExportModelAdmin

# Register your models here.

admin.site.register(PaymentOptions)
admin.site.register(Transaction)
admin.site.register(EmailRecord)


@admin.register(FilmHoboSenderEmail)
class FilmHoboSenderEmailAdmin(ImportExportModelAdmin):
    resource_class = FilmHoboSenderEmailResource
