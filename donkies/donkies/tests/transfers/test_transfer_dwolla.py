import pytest
from .. import base
from ..factories import TransactionFactory


class TestTransferDwolla(base.Mixin):
    """
    Test transfers from finance.Transfer model to Dwolla.
    """

    @pytest.mark.django_db
    def test(self):
        pass
