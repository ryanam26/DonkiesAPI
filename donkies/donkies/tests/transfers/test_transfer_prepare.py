import pytest
from .. import base
from ..emulator import Emulator
from ..factories import TransactionFactory
from finance.models import TransferPrepare


class TestTransferPrepare(base.Mixin):
    @pytest.mark.django_db
    def test(self):
        e = Emulator()
        print(e.transactions)
