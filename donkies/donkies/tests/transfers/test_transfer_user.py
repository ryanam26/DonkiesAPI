import pytest
from .. import base
from ..factories import TransactionFactory
from django.conf import settings


class TestTransferUser(base.Mixin):
    @pytest.mark.django_db
    def test(self):
        pass
