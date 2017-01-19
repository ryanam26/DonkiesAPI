import pytest
from django.db.models import Sum
from .. import base
from ..emulator import Emulator
from finance.models import TransferPrepare, Transaction


class TestTransferPrepare(base.Mixin):
    @pytest.mark.django_db
    def test01(self):
        e = Emulator()
        TransferPrepare.objects.process_roundups(is_test=True)
        assert len(e.debit_accounts) == TransferPrepare.objects.count()

    @pytest.mark.django_db
    def test02(self):
        e = Emulator()
        total_should_be = e.get_total_roundup(e.transactions)
        TransferPrepare.objects.process_roundups(is_test=True)
        sum = TransferPrepare.objects.aggregate(Sum('roundup'))['roundup__sum']
        assert total_should_be == sum

        qs = Transaction.objects.active().filter(is_processed=False)
        assert qs.count() == 0
