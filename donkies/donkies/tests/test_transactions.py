import pytest
from decimal import Decimal
from .import base
from finance.models import Transaction


class TestTransactions(base.Mixin):
    @pytest.mark.django_db
    def test_roundup(self, client):
        t = Transaction()
        assert t.calculate_roundup(Decimal('10.22')) == Decimal('0.78')
        assert t.calculate_roundup(Decimal('10.01')) == Decimal('0.99')
        assert t.calculate_roundup(Decimal('10.90')) == Decimal('0.10')
