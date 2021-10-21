
from import_export.resources import ModelResource

from .models import PaymentOptions, Transaction, EmailRecord, ScheduledEmail


class PaymentOptionsResource(ModelResource):

    class Meta:
        model = PaymentOptions


class TransactionResource(ModelResource):

    class Meta:
        model = Transaction


class EmailRecordResource(ModelResource):

    class Meta:
        model = EmailRecord


class ScheduledEmailResource(ModelResource):

    class Meta:
        model = ScheduledEmail
