from django.contrib import admin

from import_export.admin import ImportExportModelAdmin

from .models import Designation, InitialIntrestedUsers
from .importexport import InitialIntrestedUsersResource

admin.site.register(Designation)


class InitialIntrestedUsersAdmin(ImportExportModelAdmin):
    resource_class = InitialIntrestedUsersResource


admin.site.register(InitialIntrestedUsers, InitialIntrestedUsersAdmin)
