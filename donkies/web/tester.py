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
        User = apps.get_model('web', 'User')

        user = User.objects.get(email='ryanatp26@yahoo.co.uk')
        dt = user.confirmed_at.date()

        qs = Transaction.objects.filter(
            account__item__user=user, date__gt=dt)
        for tr in qs:
            print(tr.amount, tr.calculate_roundup(tr.amount))

if __name__ == '__main__':
    t = Tester()
    from finance.tasks import fetch_history_transactions

    fetch_history_transactions.apply_async(countdown=10)


    # t.test_transactions_roundup()
    # import datetime
    # from web.models import User
    # from finance.models import Item
    # from finance.services.plaid_api import PlaidApi
    # user = User.objects.get(email='ryanatp26@yahoo.co.uk')
    # item = Item.objects.first()

    # today = datetime.date.today()

    # start_date = today - datetime.timedelta(days=400)
    # end_date = today - datetime.timedelta(days=430)
    # start_date = start_date.strftime('%Y-%m-%d')
    # end_date = end_date.strftime('%Y-%m-%d')

    # pa = PlaidApi()
    # d = pa.client.Transactions.get(
    #     item.access_token,
    #     start_date=start_date,
    #     end_date=end_date
    # )
    # print(d)
