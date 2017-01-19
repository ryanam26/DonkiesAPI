from finance.models import Account
from .factories import (
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
        self.user = UserFactory(email='bob@gmail.com')
        self.num_debit_accounts = num_debit_accounts
        self.num_debt_accounts = num_debt_accounts
        self.num_transactions = num_transactions

        self.members = []
        self.debit_accounts = []
        self.debt_accounts = []
        self.transactions = []
        self.fill()

    def fill(self):
        self.fill_debit_accounts()
        self.fill_debt_accounts()
        self.fill_transactions()
        self.set_funding_source()

    def set_funding_source(self):
        """
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
