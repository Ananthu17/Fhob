from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Help, EmailUs, ReportProblem
from .importexport import HelpResource, EmailUsResource, ReportProblemResource
# Register your models here.


@admin.register(Help)
class HelpAdmin(ImportExportModelAdmin):
    resource_class = HelpResource


@admin.register(EmailUs)
class EmailUsAdmin(ImportExportModelAdmin):
    resource_class = EmailUsResource


@admin.register(ReportProblem)
class ReportProblemAdmin(ImportExportModelAdmin):
    resource_class = ReportProblemResource


# admin.site.register(Help)
# admin.site.register(EmailUs)
# admin.site.register(ReportProblem)
