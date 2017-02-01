"""
Creates fake data for admin user.
python manage.py generator

2 debit bank accounts: Chase and Wells Fargo.
2 debt bank accounts: Chase and Wells Fargo.

user.minimum_transfer_amount = 20

Each day has randomly from 3 to 5 transactions from 3 to 30 USD.
Transfers are made, each time when roundup sum
more than minimum_transfer_amount.

Atrium users are not created for admin users.
(User.objects.create_atrium_user)

Atrium data is not updated for admin users.
(tasks.update_user)

All admin's Atrium data is fake.

Dwolla customers are not created for admin users.
(Customer.objects.create_dwolla_customer)

Dwolla transfers are not initiated for admin users.
(TransferDonkies().can_initiate)

All admin's Dwolla data is fake.
"""

import datetime
import decimal
import random
import uuid

from django.db import connection
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.apps import apps
from finance.models import (
    Account, Member, Transaction, Institution, TransferPrepare,
    TransferDonkies, TransferUser)


NUM_DAYS = 100


class Generator:
    institutions = ['chase', 'wells_fargo']

    def __init__(self):
        self.user = self.get_user()
        self.data_folder = '{}/donkies/finance/services/data'.format(
            settings.BASE_DIR)
        self.categories = self.get_categories()
        self.descriptions = self.get_descriptions()

    def get_categories(self):
        path = '{}/categories.txt'.format(self.data_folder)
        l = []
        with open(path) as f:
            for line in f:
                l.append(line.strip())
        return l

    def get_descriptions(self):
        path = '{}/descriptions.txt'.format(self.data_folder)
        l = []
        with open(path) as f:
            for line in f:
                l.append(line.strip())
        return l

    def get_user(self):
        User = apps.get_model('web', 'User')
        return User.objects.filter(is_admin=True).first()

    def get_category(self):
        return random.choice(self.categories)

    def get_description(self):
        return random.choice(self.descriptions)

    def get_datetime(self, date):
        """
        Returns datetime from date, where hours, minutes and seconds
        are random.
        """
        return datetime.datetime(
            date.year,
            date.month,
            date.day,
            random.randint(0, 23),
            random.randint(0, 59),
            random.randint(0, 59))

    def create_customer(self):
        pass

    def create_funding_source(self):
        pass

    def create_member(self, institution_code):
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

    def create_account(self, member, account_type):
        """
        account_type: debit/debt
        """
        if account_type == 'debit':
            name = 'Debit {}'.format(member.name)
            acc_type = Account.CHECKING
            balance = random.randint(300, 2000)
        else:
            name = 'Credit {}'.format(member.name)
            acc_type = Account.LOAN
            balance = -random.randint(50000, 100000)

        a = Account(member=member)
        a.guid = uuid.uuid4().hex
        a.uid = uuid.uuid4().hex
        a.name = name
        a.type = acc_type
        a.updated_at = timezone.now()
        a.balance = balance
        a.available_balance = a.balance
        a.save()

    def create_accounts(self):
        for member in Member.objects.active().filter(user=self.user):
            self.create_account(member, 'debit')
            self.create_account(member, 'debt')

    def generate_amount(self):
        """
        Generate amount from 3 to 30 USD.
        """
        dollars = random.randint(3, 30)
        cents = random.randint(0, 99)
        return decimal.Decimal('{}.{}'.format(dollars, cents))

    def generate_transactions(self):
        """
        Generate transactions only for Debit accounts.
        """
        for account in Account.objects.active().filter(
                member__user=self.user, type_ds=Account.DEBIT):
            self.create_transactions(account)

    def create_transactions(self, account):
        """
        Create transactions for account back for NUM_DAYS.
        """
        today = datetime.date.today()
        l = [today - datetime.timedelta(days=x) for x in range(0, NUM_DAYS)]
        for date in l:
            self.create_transaction(account, date)

    def create_transaction(self, account, date):
        num_transactions = random.randint(3, 5)
        for i in range(num_transactions):
            dt = self.get_datetime(date)
            t = Transaction(account=account)
            t.guid = uuid.uuid4().hex
            t.uid = uuid.uuid4().hex
            t.date = date
            t.created_at = timezone.make_aware(dt)
            t.updated_at = timezone.make_aware(dt)
            t.transacted_at = timezone.make_aware(dt)
            t.posted_at = timezone.make_aware(dt)
            t.amount = self.generate_amount()
            t.is_expense = True
            t.category = self.get_category()
            t.description = self.get_description()
            t.save()

            self.make_transfers(dt)

    def make_transfers(self, dt):
        """
        Run transfers logic after every transaction.
        Transfers should be made when collected roundup
        equal or more user.minimum_transfer_amount
        """
        TransferPrepare.objects.process_roundups()
        TransferDonkies.objects.process_prepare()

        self.emulate_dwolla_transfers(dt)

        TransferUser.objects.process_to_model()

    def emulate_dwolla_transfers(self, dt):
        """
        Emulate that all transfers have been sent to Dwolla
        from TransferDonkies.
        """
        dt = dt + datetime.timedelta(minutes=random.randint(10, 100))
        qs = TransferDonkies.objects.filter(account__member__user=self.user)
        for td in qs:
            td.status = TransferDonkies.PROCESSED
            td.is_sent = True
            td.sent_at = timezone.make_aware(dt)
            td.created_at = timezone.make_aware(dt)
            td.updated_at = timezone.make_aware(dt)
            td.processed_at = timezone.make_aware(dt)
            td.dwolla_id = uuid.uuid4().hex
            td.save()

    def clean(self):
        """
        By default: Member, Account and Transactions are not deleted
        from database, but set is_active=False.
        In clean method they should be really deleted, so use raw queries.
        """
        TransferUser.objects.filter(
            account__member__user=self.user).delete()
        TransferDonkies.objects.filter(
            account__member__user=self.user).delete()
        TransferPrepare.objects.filter(
            account__member__user=self.user).delete()

        l = Transaction.objects.filter(
            account__member__user=self.user).values_list('id', flat=True)
        if l:
            cur = connection.cursor()
            query = 'delete from finance_transaction where id IN (%s)'\
                % ','.join(map(lambda x: '%s', l))
            cur.execute(query, l)

        l = Account.objects.filter(
            member__user=self.user).values_list('id', flat=True)
        if l:
            cur = connection.cursor()
            query = 'delete from finance_account where id IN (%s)'\
                % ','.join(map(lambda x: '%s', l))
            cur.execute(query, l)

        l = Member.objects.filter(user=self.user).values_list('id', flat=True)
        if l:
            cur = connection.cursor()
            query = 'delete from finance_member where id IN (%s)'\
                % ','.join(map(lambda x: '%s', l))
            cur.execute(query, l)

    @transaction.atomic
    def run(self):
        self.create_members()
        self.create_accounts()
        self.generate_transactions()
        print(Member.objects.filter(user=self.user))
        print(Account.objects.filter(member__user=self.user).count())
        print(Transaction.objects.filter(
            account__member__user=self.user).count())
