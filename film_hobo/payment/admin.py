from django.contrib import admin

from .models import PaymentOptions, Transaction, FilmHoboSenderEmail, \
    EmailRecord, ScheduledEmail
from hobo_user.importexport import FilmHoboSenderEmailResource
from .importexport import PaymentOptionsResource, TransactionResource, \
                           EmailRecordResource, ScheduledEmailResource
from import_export.admin import ImportExportModelAdmin

# Register your models here.

# admin.site.register(PaymentOptions)
# admin.site.register(Transaction)
# admin.site.register(EmailRecord)
# admin.site.register(ScheduledEmail)


@admin.register(Transaction)
class TransactionAdmin(ImportExportModelAdmin):
    resource_class = TransactionResource


@admin.register(EmailRecord)
class EmailRecordAdmin(ImportExportModelAdmin):
    resource_class = EmailRecordResource


@admin.register(PaymentOptions)
class PaymentOptionsAdmin(ImportExportModelAdmin):
    resource_class = PaymentOptionsResource


@admin.register(ScheduledEmail)
class ScheduledEmailAdmin(ImportExportModelAdmin):
    resource_class = ScheduledEmailResource


@admin.register(FilmHoboSenderEmail)
class FilmHoboSenderEmailAdmin(ImportExportModelAdmin):
    resource_class = FilmHoboSenderEmailResource
