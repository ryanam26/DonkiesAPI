import django
import os
import requests
import sys

from os.path import abspath, dirname, join

path = abspath(join(dirname(abspath(__file__)), '..'))
sys.path.append(path)
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', 'donkies.settings.development')
django.setup()
from django.apps import apps
from django.conf import settings
from django.db import transaction


class Tester:
    def send_email(self):
        from web.tasks import send_email
        send_email()

    def update_transactions(self):
        """
        Updates transactions for all items.
        """

        Item = apps.get_model('finance', 'Item')
        Transaction = apps.get_model('finance', 'Transaction')

        for item in Item.objects.all():
            Transaction.objects.create_or_update_transactions(
                item.access_token)

    def debug_transactions_webhook(self):
        """
        Local development server should be running.
        Local Celery should be runnning.
        Look at what happens in Celery.
        Emulating sending webhook to local server.
        """
        Item = apps.get_model('finance', 'Item')
        item = Item.objects.first()
        data = {
            'webhook_code': 'HISTORICAL_UPDATE',
            'webhook_type': 'TRANSACTIONS',
            'error': None,
            'new_transactions': 331
        }
        data['item_id'] = item.plaid_id

        url = 'http://localhost:8000/v1/plaid/webhooks'
        url = 'https://api.donkies.co/v1/plaid/webhooks'
        r = requests.post(url, data=data)
        print(r.status_code)

    def test_transactions_roundup(self):
        Transaction = apps.get_model('finance', 'Transaction')
        qs = Transaction.objects.all().order_by('-date')
        for tr in qs:
            print(tr.amount, tr.calculate_roundup(tr.amount))

    @transaction.atomic
    def fix_transactions_roundup(self):
        Transaction = apps.get_model('finance', 'Transaction')
        Transaction.objects.all().update(is_processed=False)
        qs = Transaction.objects.all()
        for tr in qs:
            print(tr.id)
            tr.save()


if __name__ == '__main__':
    t = Tester()
    # t.test_transactions_roundup()
    t.fix_transactions_roundup()
