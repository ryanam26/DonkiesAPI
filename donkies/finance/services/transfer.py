import collections
import decimal
import json
from django.core.exceptions import ValidationError


class TransferService:
    """
    Service that distributes transactions to accounts.
    Init:
        transactions - list of transactions dicts
        [{id: ..., account_id: ..., amount: ...}, ]

        accounts - list of debt accounts dicts
        [{id: ..., share: ...}, ]

        After processing, self.transfer contains
        transfer data.
    """
    def __init__(self, transactions, accounts):
        # Group transactions by debit accounts
        od = collections.OrderedDict()
        for d in transactions:
            aid = d['account_id']
            if aid not in od:
                od[aid] = {}
                od[aid]['amount'] = 0
                od[aid]['amount_transferred'] = 0
                od[aid]['transactions'] = []

            od[aid]['transactions'].append(d['id'])
            od[aid]['amount'] += d['amount']

        self.debits = []
        for k, v in od.items():
            d = {'id': k}
            d.update(v)
            self.debits.append(d)

        self.debts = []
        for d in accounts:
            d['amount_target'] = 0
            d['amount_transferred'] = 0
            self.debts.append(d)

        self.transfer = []

    def get_total(self):
        """
        Returns sum of all transactions amount.
        """
        total = 0
        for d in self.debits:
            total += d['amount']
        return total

    def fill_target(self):
        """
        Fill target amount for each account accordingly to
        account's share.
        """
        total = self.get_total()
        sum = 0
        for d in self.debts:
            target = total * d['share'] / 100
            target = target.quantize(decimal.Decimal('.01'))
            d['amount_target'] = target
            sum += target

        if sum != total:
            s = json.dumps(self.debts)
            raise ValidationError(
                'TransferService: sum != total, {}'.format(s))

    def is_debit_processed(self, d):
        if d['amount'] == d['amount_transferred']:
            return True
        return False

    def is_debt_processed(self, d):
        if d['amount_target'] == d['amount_transferred']:
            return True
        return False

    def get_debit(self):
        """
        Returns first not yet processed debit account
        or None if all debits accounts has been processed.
        """
        for d in self.debits:
            if not self.is_debit_processed(d):
                return d
        return None

    def get_debt(self):
        """
        Returns first not yet processed debt account
        or None if all debts accounts has been processed.
        """
        for d in self.debts:
            if not self.is_debt_processed(d):
                return d
        return None

    def process(self):
        """
        Recursion method, that will process transfers until finish.
        """
        debit = self.get_debit()
        if debit is None:
            return

        debt = self.get_debt()
        target = debt['amount_target']
        transferred = debt['amount_transferred']

        amount_to_transfer = debit['amount'] - debit['amount_transferred']

        if amount_to_transfer > target - transferred:
            amount_to_transfer = target - transferred

        debit['amount_transferred'] += amount_to_transfer
        debt['amount_transferred'] += amount_to_transfer

        result = {}
        result['account_from'] = debit['id']
        result['account_to'] = debt['id']
        result['amount'] = amount_to_transfer
        self.transfer.append(result)

        return self.process()

    def check(self):
        sum1 = 0
        for d in self.debits:
            sum1 += d['amount_transferred']

        sum2 = 0
        for d in self.debits:
            sum2 += d['amount_transferred']

        if sum1 != sum2:
            raise ValidationError(
                'TransferService: transferred amounts not match.')

    def run(self):
        self.fill_target()
        self.process()
        self.check()

        for d in self.transfer:
            print(d)

    @staticmethod
    def mock_transactions():
        """
        Returns transactions for testing.
        """
        return [
            {'id': 1, 'account_id': 1, 'amount': decimal.Decimal('0.55')},
            {'id': 2, 'account_id': 1, 'amount': decimal.Decimal('0.21')},
            {'id': 3, 'account_id': 1, 'amount': decimal.Decimal('0.94')},
            {'id': 4, 'account_id': 2, 'amount': decimal.Decimal('0.32')},
            {'id': 5, 'account_id': 2, 'amount': decimal.Decimal('0.48')},
            {'id': 6, 'account_id': 3, 'amount': decimal.Decimal('0.11')},
            {'id': 7, 'account_id': 3, 'amount': decimal.Decimal('0.51')},
        ]

    @staticmethod
    def mock_accounts():
        """
        Returns accounts for testing.
        Sum of share of all accounts should be equal to 100.
        """
        return [
            {'id': 4, 'share': 57},
            {'id': 5, 'share': 12},
            {'id': 6, 'share': 31},
        ]
