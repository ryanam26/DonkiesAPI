import pytest
from ... import base
from ...factories import TransactionFactory
from finance.models import Transaction


class TestTransaction(base.Mixin):
    @pytest.mark.django_db
    def test_delete01(self):
        """
        Instead of deleting object should set is_active=False
        """
        t = TransactionFactory.get_transaction()
        assert t.is_active is True

        t.delete()
        t.refresh_from_db()
        assert t.is_active is False

    @pytest.mark.django_db
    def test_delete02(self):
        """
        Instead of deleting queryset, should set is_active=False
        """
        TransactionFactory.get_transaction()
        TransactionFactory.get_transaction()

        assert Transaction.objects.count() == 2
        Transaction.objects.all().delete()
        assert Transaction.objects.count() == 2

        for t in Transaction.objects.all():
            assert t.is_active is False
