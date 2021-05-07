from django.contrib import admin

from import_export.admin import ImportExportActionModelAdmin

from .models import Designation, InitialIntrestedUsers
from .importexport import InitialIntrestedUsersResource

admin.site.register(Designation)


class InitialIntrestedUsersAdmin(ImportExportActionModelAdmin):
    resource_class = InitialIntrestedUsersResource


admin.site.register(InitialIntrestedUsers, InitialIntrestedUsersAdmin)
