"""
Creates fake Atrium data for admin user.
By default admin users do not connect to Atrium API.

2 bank accounts: chase and mxbank.

Each bank account has 2 years of transactions.
Each day has randomly from 3 to 5 transactions from 3 to 30 USD.
"""

import datetime
import decimal
import django
import os
import random
import sys
import uuid

from os.path import abspath, dirname, join
from django.db import transaction
from django.utils import timezone
from django.apps import apps
from faker import Faker

path = abspath(join(dirname(abspath(__file__)), '..', '..'))
sys.path.append(path)
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', 'donkies.settings.development')
django.setup()


class Generator:
    institutions = ['chase', 'mxbank']

    def __init__(self):
        self.user = self.get_user()

    def get_user(self):
        User = apps.get_model('web', 'User')
        return User.objects.filter(is_admin=True).first()

    def create_member(self, institution_code):
        Institution = apps.get_model('finance', 'Institution')
        Member = apps.get_model('finance', 'Member')

        m = Member(user=self.user)
        m.institution = Institution.objects.get(code=institution_code)
        m.guid = uuid.uuid4().hex
        m.identifier = uuid.uuid4().hex
        m.name = institution_code
        m.status = Member.COMPLETED
        m.aggregated_at = timezone.now()
        m.successfully_aggregated_at = timezone.now()
        m.is_created = True
        m.save()

    def create_members(self):
        for code in self.institutions:
            self.create_member(code)

    def create_account(self, member):
        Account = apps.get_model('finance', 'Account')
        a = Account(member=member)
        a.guid = uuid.uuid4().hex
        a.uid = uuid.uuid4().hex
        a.name = 'Debit {}'.format(member.name)
        a.type_ds = Account.DEBIT
        a.updated_at = timezone.now()
        a.save()

    def create_accounts(self):
        Member = apps.get_model('finance', 'Member')
        for member in Member.objects.filter(user=self.user):
            self.create_account(member)

    def generate_amount(self):
        """
        Generate amount from 3 to 30 USD.
        """
        dollars = random.randint(3, 30)
        cents = random.randint(0, 99)
        return decimal.Decimal('{}.{}'.format(dollars, cents))

    def generate_transactions(self):
        Account = apps.get_model('finance', 'Account')
        for account in Account.objects.filter(member__user=self.user):
            self.create_transactions(account)

    def create_transactions(self, account):
        """
        Create transactions for account for 2 years.
        """
        today = datetime.date.today()
        l = [today - datetime.timedelta(days=x) for x in range(0, 730)]
        for date in l:
            self.create_transaction(account, date)

    def create_transaction(self, account, date):
        Transaction = apps.get_model('finance', 'Transaction')

        dt = datetime.datetime(
            date.year,
            date.month,
            date.day,
            random.randint(0, 23),
            random.randint(0, 59),
            random.randint(0, 59))

        t = Transaction(account=account)
        t.guid = uuid.uuid4().hex
        t.uid = uuid.uuid4().hex
        t.date = date
        t.created_at = timezone.make_aware(dt)
        t.amount = self.generate_amount()
        t.is_expense = True
        t.description = Faker().sentence()
        t.save()

    def clean(self):
        Member = apps.get_model('finance', 'Member')
        Member.objects.filter(user=self.user).delete()

    @transaction.atomic
    def run(self):
        self.create_members()
        self.create_accounts()
        self.generate_transactions()


if __name__ == '__main__':
    g = Generator()
    g.run()
    g.clean()
