import pytest
from .. import base
from ..factories import TransactionFactory
from finance.models import TransferPrepare


class TestTransferInternal(base.Mixin):
    """
    Test transfers to internal models: TransferPrepare, Transfer.
    """
    @pytest.mark.django_db
    def test(self):
        print(TransferPrepare.objects.get_transfer_date())
