import pytest
from django.db.models import Sum
from django.conf import settings
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
        Test success transfer.
        Collected roundup should be more than
        settings.TRANSFER_TO_DONKIES_MIN_AMOUNT
        """
        e = Emulator()
        e.init()
        sum = e.user.get_not_processed_roundup_sum()

        settings.TRANSFER_TO_DONKIES_MIN_AMOUNT = sum - 1
        Emulator.run_transfer_prepare()
        assert len(e.debit_accounts) == TransferPrepare.objects.count()

    @pytest.mark.django_db
    def test03(self):
        """
        Test case where collected roundup is less than
        settings.TRANSFER_TO_DONKIES_MIN_AMOUNT
        Should not send transfers to Donkies.
        """
        e = Emulator()
        e.init()
        sum = e.user.get_not_processed_roundup_sum()

        settings.TRANSFER_TO_DONKIES_MIN_AMOUNT = sum + 1
        Emulator.run_transfer_prepare()
        assert TransferPrepare.objects.count() == 0

    @pytest.mark.django_db
    def test04(self):
        """
        Test that amounts are equal.
        """
        e = Emulator()
        e.init()
        total_should_be = e.get_total_roundup(e.transactions)
        sum = e.user.get_not_processed_roundup_sum()
        assert sum == total_should_be

        # Success case for transfer.
        settings.TRANSFER_TO_DONKIES_MIN_AMOUNT = sum - 1
        Emulator.run_transfer_prepare()

        sum = TransferPrepare.objects.aggregate(Sum('roundup'))['roundup__sum']
        assert total_should_be == sum

        qs = Transaction.objects.active().filter(is_processed=False)
        assert qs.count() == 0
