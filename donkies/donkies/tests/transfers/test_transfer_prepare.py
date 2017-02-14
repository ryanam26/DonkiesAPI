import pytest
from django.db.models import Sum
from .. import base
from donkies.tests.services.emulator import Emulator
from finance.models import TransferPrepare, Transaction


class TestTransferPrepare(base.Mixin):
    @pytest.mark.django_db
    def test01(self):
        """
        If user didn't set funding source, do not process prepare.
        """
        e = Emulator()
        e.init()

        e.clear_funding_source()
        Emulator.run_transfer_prepare()
        assert TransferPrepare.objects.count() == 0

    @pytest.mark.django_db
    def test02(self):
        """
        Test success.
        """
        e = Emulator()
        e.init()
        Emulator.run_transfer_prepare()
        assert len(e.debit_accounts) == TransferPrepare.objects.count()

    @pytest.mark.django_db
    def test03(self):
        """
        Test that amounts are equal.
        """
        e = Emulator()
        e.init()
        total_should_be = e.get_total_roundup(e.transactions)
        assert e.user.get_not_processed_roundup_sum() == total_should_be

        Emulator.run_transfer_prepare()

        sum = TransferPrepare.objects.aggregate(Sum('roundup'))['roundup__sum']
        assert total_should_be == sum

        qs = Transaction.objects.active().filter(is_processed=False)
        assert qs.count() == 0

    @pytest.mark.django_db
    def test04(self):
        """
        Transfers should be made once a day.
        After first transfer prepare, the next
        should not be processed.
        """
        e = Emulator()
        e.init()
        Emulator.run_transfer_prepare()
        assert len(e.debit_accounts) == TransferPrepare.objects.count()

        num_transactions = len(e.transactions)

        # Add more transactions.
        e.fill_transactions()
        assert len(e.transactions) > num_transactions

        # Try to transfer again, but shouldn't process any more today.
        Emulator.run_transfer_prepare()
        assert len(e.debit_accounts) == TransferPrepare.objects.count()
