import django
import os
import sys

from os.path import abspath, dirname, join

path = abspath(join(dirname(abspath(__file__)), '..'))
sys.path.append(path)
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', 'donkies.settings.development')
django.setup()
from django.apps import apps


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


if __name__ == '__main__':
    t = Tester()
    t.update_transactions()
