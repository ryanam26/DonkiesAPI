import pytest
from .. import base
from ..factories import TransactionFactory


class TestTransferUser(base.Mixin):
    @pytest.mark.django_db
    def test(self):
        pass
