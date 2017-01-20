import pytest
from django.db.models import Sum
from .. import base
from ..emulator import Emulator
from finance.models import (
    TransferPrepare, TransferDonkies, TransferDonkiesFailed)


class TestTransferDonkies(base.Mixin):
    @pytest.mark.django_db
    def test01(self):
        e = Emulator()
        e.init()
        e.run_transfer_prepare()
        e.clear_funding_source()
        e.run_transfer_donkies_process_prepare()

        assert TransferDonkies.objects.count() == 0

    @pytest.mark.django_db
    def test02(self):
        e1 = Emulator()
        e1.init()
        e1.run_transfer_prepare()
        e1.run_transfer_donkies_process_prepare()

        e2 = Emulator()
        e2.init()
        e2.run_transfer_prepare()
        e2.run_transfer_donkies_process_prepare()

        assert TransferDonkies.objects.count() == 2

    @pytest.mark.django_db
    def test03(self):
        e = Emulator()
        e.init()
        e.run_transfer_prepare()

        sum = TransferPrepare.objects.filter(is_processed=False)\
            .aggregate(Sum('roundup'))['roundup__sum']

        e.run_transfer_donkies_process_prepare()
        assert TransferDonkies.objects.first().amount == sum
        assert TransferDonkies.objects.count() == 1

    @pytest.mark.django_db
    def test04(self):
        e = Emulator()
        e.init()
        e.run_transfer_prepare()
        e.run_transfer_donkies_process_prepare()

        qs = TransferPrepare.objects.filter(is_processed=False)
        assert qs.count() == 0

    @pytest.mark.django_db
    def test05(self):
        e = Emulator(num_debit_accounts=1)
        e.init()
        e.run_transfer_prepare()
        e.run_transfer_donkies_process_prepare()

        tds = TransferDonkies.objects.first()
        tds.failure_code = 'R99'
        tds.is_failed = True
        tds.save()

        TransferDonkies.objects.move_failed(tds.id)

        tdf = TransferDonkiesFailed.objects.first()

        assert tds.dwolla_id == tdf.dwolla_id
        assert tds.amount == tdf.amount
        assert tds.status == tdf.status
        assert tds.created_at == tdf.created_at
        assert tds.initiated_at == tdf.initiated_at
        assert tds.updated_at == tdf.updated_at
        assert tds.failure_code == tdf.failure_code
        assert tds.is_initiated == tdf.is_initiated
        assert tds.is_failed == tdf.is_failed
        assert tds.account == tdf.account

        assert TransferDonkies.objects.filter(id=tds.id).exists() is False
