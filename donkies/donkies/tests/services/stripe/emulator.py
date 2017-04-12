import calendar
import datetime
import random
from django.utils import timezone
from django.conf import settings
from finance.models import Account, TransferPrepare
from ach.models import TransferDebt, TransferUser
from donkies.tests.factories import (
    AccountFactory, ItemFactory, TransactionFactory,
    TransferStripeFactory, UserFactory)


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
        self.set_funding_source()
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

    def is_last_day_of_the_month(self, dt):
        _, last = calendar.monthrange(dt.year, dt.month)
        if last == dt.day:
            return True
        return False

    def set_funding_source(self):
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

    def create_stripe_transfers(self, num_days):
        """
        Creates transfers to Stripe for num_days back from today.
        Current requirement: transfer is created in the last day
        of the month. Create directly in db without full flow emulation.
        Requirements in spec are changing constantly.
        So, we loop by days, but create only at the last day of the month.
        """
        account = self.user.get_funding_source_account()

        for date in self.get_dates_range(num_days):
            if not self.is_last_day_of_the_month(date):
                continue
            dt = self.get_datetime(date)
            dt = timezone.make_aware(dt)
            TransferStripeFactory.get_transfer(
                account=account, created_at=dt)

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

    @staticmethod
    def run_transfer_prepare():
        """
        Collect not processed roundups to TransferPrepare model.
        """
        TransferPrepare.objects.process_roundups()

    @staticmethod
    def run_process_users():
        """
        All user's payments from debit accounts to Stripe,
        delegate to TransferUser and then to TransferDebt.
        """
        TransferUser.objects.process_users()

    @staticmethod
    def emulate_transfers_to_users(self):
        """
        All transfers have been sent to user's debt accounts.
        """
        TransferDebt.objects\
            .filter(is_processed=False)\
            .update(is_processed=True, processed_at=timezone.now())
