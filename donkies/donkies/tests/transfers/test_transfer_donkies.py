import pytest
from django.db.models import Sum
from .. import base
from ..emulator import Emulator
from finance.models import TransferPrepare, TransferDonkies


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
