from django.contrib import admin
from .models import Help, EmailUs, ReportProblem
# Register your models here.

admin.site.register(Help)
admin.site.register(EmailUs)
admin.site.register(ReportProblem)
