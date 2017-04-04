import pytest
from decimal import Decimal
from .import base
from .factories import AccountFactory, TransactionFactory


class TestTransactions(base.Mixin):
    """
    User has setting "is_even_roundup" (False by default).
    If setting is true, then amounts with x.00 rounded up to $1
    If setting is false, skip this roundup.
    """
    @pytest.mark.django_db
    def test_roundup01(self, client):
        t = TransactionFactory.get_transaction()
        assert t.calculate_roundup(Decimal('10.22')) == Decimal('0.78')
        assert t.calculate_roundup(Decimal('10.01')) == Decimal('0.99')
        assert t.calculate_roundup(Decimal('10.90')) == Decimal('0.10')

    @pytest.mark.django_db
    def test_roundup02(self, client):
        """
        Test user with is_even_roundup = True
        """
        t = TransactionFactory.get_transaction()
        user = t.account.item.user
        user.is_even_roundup = True
        user.save()

        t.refresh_from_db()
        assert t.calculate_roundup(Decimal('10.00')) == Decimal('1.00')

    @pytest.mark.django_db
    def test_roundup03(self, client):
        """
        Test user with is_even_roundup = False
        """
        t = TransactionFactory.get_transaction()
        user = t.account.item.user
        user.is_even_roundup = False
        user.save()

        t.refresh_from_db()
        assert t.calculate_roundup(Decimal('10.00')) == Decimal('0.00')

    @pytest.mark.django_db
    def test_roundup04(self, client):
        """
        Test zero value.
        Roundup should be zero.
        """
        t = TransactionFactory.get_transaction()
        assert t.calculate_roundup(Decimal('0.00')) == Decimal('0.00')

    @pytest.mark.django_db
    def test_get_transactions(self, client):
        """
        Test API endpoint.
        """
        account = AccountFactory.get_account()
        for _ in range(5):
            TransactionFactory.get_transaction(account=account)

        client = self.get_auth_client(account.item.user)
        url = '/v1/transactions'
        response = client.get(url)
        assert response.status_code == 200
