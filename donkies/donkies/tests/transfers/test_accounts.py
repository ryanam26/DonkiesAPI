import pytest
from .. import base
from ..factories import AccountFactory, MemberFactory, TransactionFactory
from finance.models import Account, Transaction


class TestAccount(base.Mixin):
    @pytest.mark.django_db
    def test_delete01(self):
        """
        Instead of deleting object should set is_active=False
        """
        a = AccountFactory.get_account()
        assert a.is_active is True

        a.delete()
        a.refresh_from_db()
        assert a.is_active is False

    @pytest.mark.django_db
    def test_delete02(self):
        """
        Instead of deleting queryset, should set is_active=False
        """
        AccountFactory.get_account()
        AccountFactory.get_account()

        assert Account.objects.count() == 2
        Account.objects.all().delete()
        assert Account.objects.count() == 2

        for a in Account.objects.all():
            assert a.is_active is False

    @pytest.mark.django_db
    def test_delete03(self):
        """
        Test calling Account.objects.delete_account method.
        All Transactions of deleted Account should be set
        to is_active=False
        """
        a = AccountFactory.get_account()
        TransactionFactory.get_transaction(account=a)
        TransactionFactory.get_transaction(account=a)

        assert Account.objects.count() == 1
        assert Transaction.objects.count() == 2

        Account.objects.delete_account(a.id)

        for obj in Account.objects.all():
            assert obj.is_active is False

        for obj in Transaction.objects.all():
            assert obj.is_active is False
