import requests

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from payment.models import Transaction, ScheduledEmail


# class Command(BaseCommand):
#     help = "A description of the command"

#     def handle(self, *args, **options):
#         self.stdout.write("My sample command just ran.")

class Command(BaseCommand):

    def handle(self, *args, **options):
        final_url = settings.ORIGIN_URL + \
            '/payment/paypal/send_remainder_email_receipt/'
        time_threshold = timezone.now() + timedelta(minutes=1)
        sheduled_emails_objs = ScheduledEmail.objects.filter(
            next_run_at__gt=time_threshold)
        if sheduled_emails_objs:
            for sheduled_emails_obj in sheduled_emails_objs:
                transaction_obj = Transaction.objects.get(
                    user=sheduled_emails_obj.user_id)
                data = {'order_id': transaction_obj.paypal_order_id}
                sheduled_remainder_email_response = requests.post(
                                    final_url,
                                    data=data,
                                    headers={'Accept': 'application/json'})
                if sheduled_remainder_email_response.status_code == 200:
                    self.stdout.write("E-mail Reaminders were sent.")
                else:
                    self.stdout.write("Failure in sending remainder email.")
        else:
            self.stdout.write("No E-mail Reaminders to send.")
