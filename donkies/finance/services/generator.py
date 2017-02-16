"""
Creates fake data for admin user.
python manage.py generator

2 debit bank accounts: Chase and Wells Fargo.
2 debt bank accounts: Chase and Wells Fargo.

user.minimum_transfer_amount = 20

Each day has randomly from 3 to 5 transactions from 3 to 30 USD.
Transfers are made to TransferDonkies every day once a day.

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

from freezegun import freeze_time
from django.db import connection
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.apps import apps
from bank.models import Customer, FundingSource
from finance.models import (
    Account, Member, Transaction, Institution, TransferPrepare,
    TransferPrepareDate, TransferDonkies, TransferUser, TransferDebt)


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
        user = User.objects.filter(is_admin=True).first()
        user.minimum_transfer_amount = 20
        user.save()
        return user

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

    def get_dates_range(self):
        """
        Returns list of dates back for NUM_DAYS from today.
        """
        today = datetime.date.today()
        return [today - datetime.timedelta(days=x) for x in range(0, NUM_DAYS)]

    def create_customer(self):
        c = Customer.objects.create_customer(self.user)
        c.dwolla_id = uuid.uuid4().hex
        c.created_at = timezone.now()
        c.status = Customer.VERIFIED
        c.save()
        self.customer = c

    def create_funding_source(self):
        account = Account.objects.filter(member__user=self.user).first()
        fs = FundingSource(
            account=account,
            dwolla_id=uuid.uuid4().hex,
            status=FundingSource.VERIFIED,
            type=FundingSource.CHECKING,
            typeb=FundingSource.BANK,
            name=account.name,
            created_at=timezone.now(),
            verification_type=FundingSource.IAV
        )
        fs.save()

        Account.objects.set_funding_source(account.id)

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

    def set_accounts_share(self):
        """
        Set share for DEBT accounts: 65% and 35%
        """
        qs = Account.objects.filter(
            member__user=self.user, type_ds=Account.DEBT)

        count = 0
        for account in qs:
            share = 65 if count == 0 else 35
            count += 1
            Account.objects.filter(id=account.id).update(transfer_share=share)

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
        for date in self.get_dates_range():
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

            dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            with freeze_time(dt_str):
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

        TransferUser.objects.process()
        self.emulate_transfers_to_user()

    def emulate_dwolla_transfers(self, dt):
        """
        Emulate that all transfers have been sent to Dwolla
        from TransferDonkies.
        """
        dt = dt + datetime.timedelta(minutes=random.randint(10, 100))
        qs = TransferDonkies.objects.filter(
            account__member__user=self.user, is_sent=False)
        for td in qs:
            td.status = TransferDonkies.PROCESSED
            td.is_initiated = True
            td.is_sent = True
            td.sent_at = timezone.make_aware(dt)
            td.created_at = timezone.make_aware(dt)
            td.updated_at = timezone.make_aware(dt)
            td.processed_at = timezone.make_aware(dt)
            td.dwolla_id = uuid.uuid4().hex
            td.save()

    def emulate_transfers_to_user(self):
        TransferDebt.objects\
            .filter(is_processed=False, account__member__user=self.user)\
            .update(is_processed=True, processed_at=timezone.now())

    def clean(self):
        """
        By default: Member, Account and Transactions are not deleted
        from database, but set is_active=False.
        In clean method they should be really deleted, so use raw queries.
        """
        Customer.objects.filter(user=self.user).delete()
        FundingSource.objects.filter(account__member__user=self.user).delete()
        TransferDebt.objects.filter(
            account__member__user=self.user).delete()
        TransferUser.objects.filter(user=self.user).delete()
        TransferDonkies.objects.filter(
            account__member__user=self.user).delete()
        TransferPrepareDate.objects.filter(user=self.user).delete()
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

    def stat_info(self):
        print(
            'members: ', Member.objects.filter(user=self.user))

        print(
            'accounts: ',
            Account.objects.filter(member__user=self.user).count())

        print(
            'transactions: ',
            Transaction.objects.filter(
                account__member__user=self.user).count())

        print(
            'TransferPrepare: ',
            TransferPrepare.objects.filter(
                account__member__user=self.user).count())

        print(
            'TransferDonkies: ',
            TransferDonkies.objects.filter(
                account__member__user=self.user).count())

        print(
            'TransferUser: ',
            TransferUser.objects.filter(user=self.user).count())

        print(
            'TransferDebt: ',
            TransferDebt.objects.filter(
                account__member__user=self.user).count())

    @transaction.atomic
    def run(self):
        self.clean()
        self.create_members()
        self.create_accounts()
        self.set_accounts_share()
        self.create_customer()
        self.create_funding_source()

        self.generate_transactions()
        self.stat_info()
