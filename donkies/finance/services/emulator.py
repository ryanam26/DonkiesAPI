import random
from faker import Faker
from django.utils import timezone
from finance.models import Account, TransferPrepare, TransferDonkies
from bank.models import FundingSource
from donkies.tests.factories import (
    AccountFactory, MemberFactory, TransactionFactory, UserFactory)


class Emulator:
    """
    Helper class for testing.
    """
    def __init__(
            self,
            num_debit_accounts=2,
            num_debt_accounts=2,
            num_transactions=50):
        """
        num_transactions - Number of transactions for each account.
        On init fill class with user, members, accounts, transactions.

        """
        self.user = UserFactory(email=Faker().email())
        self.num_debit_accounts = num_debit_accounts
        self.num_debt_accounts = num_debt_accounts
        self.num_transactions = num_transactions

        self.members = []
        self.debit_accounts = []
        self.debt_accounts = []
        self.transactions = []

    def init(self):
        self.fill()
        self.set_funding_source()

    def fill(self):
        self.fill_debit_accounts()
        self.fill_debt_accounts()
        self.fill_transactions()

    def set_funding_source(self):
        """
        Set funding source for user.
        """
        account = self.debit_accounts[0]
        dwolla_id = 'some-dwolla-id-{}'.format(random.randint(10000, 99999))
        test_dic = self.get_funding_source_dic(dwolla_id)

        FundingSource.objects.create_funding_source_iav(
            account.id, dwolla_id, test_dic)

        Account.objects.set_funding_source(account.id)

    def clear_funding_source(self):
        for a in self.debit_accounts:
            a.is_funding_source_for_transfer = False
            a.save()

    def fill_debit_accounts(self):
        for _ in range(self.num_debit_accounts):
            m = MemberFactory.get_member(user=self.user)
            a = AccountFactory.get_account(member=m, type=Account.CHECKING)

            self.members.append(m)
            self.debit_accounts.append(a)

    def fill_debt_accounts(self):
        for _ in range(self.num_debt_accounts):
            m = MemberFactory.get_member(user=self.user)
            a = AccountFactory.get_account(member=m, type=Account.LOAN)

            self.members.append(m)
            self.debt_accounts.append(a)

    def fill_transactions(self):
        l = self.debit_accounts + self.debt_accounts
        for a in l:
            for _ in range(self.num_transactions):
                tr = TransactionFactory.get_transaction(account=a)
                self.transactions.append(tr)

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

    @staticmethod
    def emulate_dwolla_transfers():
        """
        Emulate that all transfers have been sent to Dwolla
        from TransferDonkies.
        """
        for td in TransferDonkies.objects.all():
            td.status = TransferDonkies.PROCESSED
            td.is_sent = True
            td.sent_at = timezone.now()
            td.created_at = timezone.now()
            td.updated_at = timezone.now()
            td.processed_at = timezone.now()
            td.dwolla_id = 'some-dwolla-id'
            td.save()
