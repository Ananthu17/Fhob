
from import_export.resources import ModelResource

from .models import Help, EmailUs, ReportProblem


class HelpResource(ModelResource):

    class Meta:
        model = Help


class EmailUsResource(ModelResource):

    class Meta:
        model = EmailUs


class ReportProblemResource(ModelResource):

    class Meta:
        model = ReportProblem
