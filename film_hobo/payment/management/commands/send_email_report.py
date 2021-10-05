import requests

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone

from payment.models import Transaction, ScheduledEmail


class Command(BaseCommand):

    def handle(self, *args, **options):
        final_url = settings.ORIGIN_URL + \
            '/payment/paypal/send_remainder_email_receipt/'
        sheduled_emails_objs = ScheduledEmail.objects.all()
        if sheduled_emails_objs:
            for sheduled_emails_obj in sheduled_emails_objs:
                sheduled_time = sheduled_emails_obj.next_run_at.replace(
                    microsecond=0, second=0)
                current_time = timezone.now().replace(microsecond=0, second=0)
                if sheduled_time == current_time:
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
        else:
            self.stdout.write("No E-mail Reaminders to send.")
