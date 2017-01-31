import pytest
from .. import base
from ..emulator import Emulator
from finance.models import TransferUser


class TestTransferUser(base.Mixin):
    @pytest.mark.django_db
    def test_process_to_model(self):
        e = Emulator()
        e.init()
        e.run_transfer_prepare()
        e.run_transfer_donkies_prepare()

        Emulator.emulate_dwolla_transfers()

        TransferUser.objects.process_to_model()
