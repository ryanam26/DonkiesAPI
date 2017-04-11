"""
Separate Emulator for Dwolla.
"""

import datetime
import random
import uuid
from django.utils import timezone
from django.conf import settings
from finance.models import Account, TransferPrepare
from bank.models import FundingSource, TransferDonkies, TransferDebt
from donkies.tests.services.dwolla.factories import (
    AccountFactory, ItemFactory, TransactionFactory,
    TransferDonkiesFactory, UserFactory)


class Emulator:
    """
    Helper class for testing.
    """

    def __init__(
            self,
            num_debit_accounts=2,
            num_debt_accounts=2,
            num_days=2):
        """
        num_days - generate transactions back for num_days.
        Each day has randomly from 3 to 5 transactions.
        On init fill class with user, items, accounts, transactions.
        """
        self.user = UserFactory.get_user()
        self.num_debit_accounts = num_debit_accounts
        self.num_debt_accounts = num_debt_accounts
        self.num_days = num_days

        self.items = []
        self.debit_accounts = []
        self.debt_accounts = []
        self.transactions = []

    def init(self):
        self.fill_debit_accounts()
        self.fill_debt_accounts()
        self.set_funding_source_dwolla()
        self.set_funding_source_stripe()
        self.fill_transactions()

    def make_transfer_prepare_condition(self):
        """
        TransferPrepare works when user's collected roundup
        is more than settings.TRANSFER_TO_DONKIES_MIN_AMOUNT
        Make this condition True.
        """
        sum = self.user.get_not_processed_roundup_sum()
        settings.TRANSFER_TO_DONKIES_MIN_AMOUNT = sum - 1

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

    def get_dates_range(self, num_days=None):
        """
        Returns list of dates back for NUM_DAYS from today.
        """
        num_days = self.num_days if num_days is None else num_days

        date = datetime.date.today()
        return [
            date - datetime.timedelta(days=x) for x in range(0, num_days)]

    def set_funding_source_dwolla(self):
        """
        For Dwolla tests.
        Set funding source for user.
        """
        account = self.debit_accounts[0]
        dwolla_id = 'some-dwolla-id-{}'.format(random.randint(10000, 99999))
        test_dic = self.get_funding_source_dic(dwolla_id)

        FundingSource.objects.create_funding_source_iav(
            account.id, dwolla_id, test_dic)

        Account.objects.set_funding_source(account.id)

    def set_funding_source_stripe(self):
        """
        For Dwolla tests.
        Set funding source for user.
        """
        account = self.debit_accounts[0]
        Account.objects.set_funding_source(account.id)

    def clear_funding_source(self):
        for a in self.debit_accounts:
            a.is_funding_source_for_transfer = False
            a.save()

    def fill_debit_accounts(self):
        for _ in range(self.num_debit_accounts):
            item = ItemFactory.get_item(user=self.user)
            a = AccountFactory.get_account(item=item, type=Account.DEPOSITORY)

            self.items.append(item)
            self.debit_accounts.append(a)

    def fill_debt_accounts(self):
        for _ in range(self.num_debt_accounts):
            item = ItemFactory.get_item(user=self.user)
            a = AccountFactory.get_account(item=item, type=Account.CREDIT)

            self.items.append(item)
            self.debt_accounts.append(a)

    def fill_transactions(self, is_today=False):
        """
        If is_today - generate transactions for today,
        else generate transactions back for num_days.
        """
        l = self.debit_accounts + self.debt_accounts
        for account in l:
            if is_today:
                for _ in range(5):
                    tr = TransactionFactory.get_transaction(account=account)
                    self.transactions.append(tr)
            else:
                for date in self.get_dates_range():
                    self.create_transaction(account, date)

    def create_transaction(self, account, date):
        num_transactions = random.randint(3, 5)
        for i in range(num_transactions):
            dt = self.get_datetime(date)
            tr = TransactionFactory(account=account, date=dt.date())
            self.transactions.append(tr)

    def emulate_dwolla_transfers(self):
        """
        Emulate that all transfers have been sent to Dwolla
        from TransferDonkies.
        """
        dt = timezone.now() +\
            datetime.timedelta(minutes=random.randint(10, 100))

        qs = TransferDonkies.objects.filter(
            account__item__user=self.user, is_sent=False)
        for td in qs:
            td.status = TransferDonkies.PROCESSED
            td.is_initiated = True
            td.is_sent = True
            td.sent_at = dt
            td.created_at = dt
            td.updated_at = dt
            td.processed_at = dt
            td.dwolla_id = uuid.uuid4().hex
            td.save()

    def emulate_transfers_to_user(self):
        TransferDebt.objects\
            .filter(is_processed=False)\
            .update(is_processed=True, processed_at=timezone.now())

    def create_dwolla_transfers(self, num_days):
        """
        Creates transfers to Dwolla for num_days back from today.
        1 transfer per day.

        Emulating Donkies transfers to dwolla for many days
        takes too much time, therefore this method creates dwolla transfers
        directly in db without emulation. It is OK for testing.
        All transfers are PROCESSED.
        """
        account = self.user.get_funding_source_account()
        for date in self.get_dates_range(num_days):
            dt = self.get_datetime(date)
            dt = timezone.make_aware(dt)
            TransferDonkiesFactory.get_transfer(
                account=account, sent_at=dt)

    def get_total_roundup(self, l):
        """
        Input: list of transactions.
        Returns: the sum of roundup of not processed transactions.
        """
        total = 0
        for tr in l:
            if tr.is_processed is True or tr.is_processed is None:
                continue
            total += tr.roundup
        return total

    def get_funding_source_dic(self, dwolla_id):
        """
        When user creates funding source account in Dwolla (via dwolla.js),
        Dwolla respond with similar dict.
        """
        return {
            'created': '2017-01-16T08:16:07.000Z',
            'removed': False,
            'balance': {
                'currency': 'USD',
                'value': '0.00'
            },
            'id': dwolla_id,
            'type': 'balance',
            'status': 'verified',
            'name': 'Balance'
        }

    @staticmethod
    def run_transfer_prepare():
        """
        Collect not processed roundups to TransferPrepare model.
        """
        TransferPrepare.objects.process_roundups()

    @staticmethod
    def run_transfer_donkies_prepare():
        TransferDonkies.objects.process_prepare()
