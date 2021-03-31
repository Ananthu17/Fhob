from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from import_export.admin import ImportExportModelAdmin

from .models import CustomUser, Project, ProjectReaction, EthnicAppearance, \
                    EthnicAppearanceInline, AthleticSkill, AthleticSkillInline
from .importexport import EthnicAppearanceResource, AthleticSkillResource


class EthnicAppearanceInlineInline(admin.StackedInline):
    model = EthnicAppearanceInline
    insert_after = 'eyes'


class AthleticSkillInlineInline(admin.StackedInline):
    model = AthleticSkillInline


class CustomUserAdmin(UserAdmin, admin.ModelAdmin):
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        ('User', {'fields': ('first_name', 'middle_name', 'last_name',
                             'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        ('Personal Details', {'fields': ('gender',)}),
        ('Height', {'fields': ('feet', 'inch')}),
        ('Weight', {'fields': ('lbs',)}),
        ('Age-Playing Range', {'fields': ('start_age', 'stop_age')}),
        ('Build', {'fields': ('physique', 'hair_color', 'hair_length',
                              'eyes',)})
    )
    # adding personal details inline
    inlines = [
        EthnicAppearanceInlineInline, AthleticSkillInlineInline
    ]
    change_form_template = 'admin/custom/change_form.html'

    class Media:
        css = {
            'all': (
                'css/admin.css',
            )
        }

    # add_fieldsets = (
    #     (None, {
    #         'classes': ('wide',),
    #         'fields': ('email', 'password1', 'password2',
    #                    'is_staff', 'is_active')}
    #      ),
    # )
    # search_fields = ('email',)
    # ordering = ('email',)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Project)
admin.site.register(ProjectReaction)


@admin.register(EthnicAppearance)
class EthnicAppearanceAdmin(ImportExportModelAdmin):
    resource_class = EthnicAppearanceResource


@admin.register(AthleticSkill)
class AthleticSkillAdmin(ImportExportModelAdmin):
    resource_class = AthleticSkillResource
