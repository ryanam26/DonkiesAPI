import pytest
from .. import base
from ..factories import TransactionFactory


class TestTransferDonkies(base.Mixin):
    @pytest.mark.django_db
    def test(self):
        pass
