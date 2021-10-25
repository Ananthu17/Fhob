from django.contrib import admin

from import_export.admin import ImportExportModelAdmin, \
    ImportExportActionModelAdmin

from .models import Designation, InitialIntrestedUsers
from .importexport import InitialIntrestedUsersResource, DesignationResource


@admin.register(Designation)
class DesignationAdmin(ImportExportModelAdmin):
    resource_class = DesignationResource

# admin.site.register(Designation)


class InitialIntrestedUsersAdmin(ImportExportModelAdmin,
                                 ImportExportActionModelAdmin):
    resource_class = InitialIntrestedUsersResource


admin.site.register(InitialIntrestedUsers, InitialIntrestedUsersAdmin)
