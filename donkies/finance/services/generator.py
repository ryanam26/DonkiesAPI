"""
Creates fake Atrium data for admin user.
By default admin users do not connect to Atrium API.

2 bank accounts: chase and mxbank.

Each bank account has 2 years of transactions.
Each day has randomly from 3 to 5 transactions from 10 to 50 USD.
"""

import django
import os
import sys
import uuid

from os.path import abspath, dirname, join
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.apps import apps

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
        print(a.__dict__)

    def create_accounts(self):
        Member = apps.get_model('finance', 'Member')
        for member in Member.objects.filter(user=self.user):
            self.create_account(member)

    def clean(self):
        Member = apps.get_model('finance', 'Member')
        Member.objects.filter(user=self.user).delete()

    @transaction.atomic
    def run(self):
        self.create_members()
        self.create_accounts()


if __name__ == '__main__':
    g = Generator()
    g.run()
    g.clean()
