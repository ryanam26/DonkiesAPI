import pytest
from .. import base
from ..factories import AccountFactory, MemberFactory, TransactionFactory
from finance.models import Account, Transaction


class TestAccount(base.Mixin):
    @pytest.mark.django_db
    def notest_delete01(self):
        """
        Instead of deleting object should set is_active=False
        """
        a = AccountFactory.get_account()
        assert a.is_active is True

        a.delete()
        a.refresh_from_db()
        assert a.is_active is False

    @pytest.mark.django_db
    def notest_delete02(self):
        """
        Instead of deleting queryset, should set is_active=False
        """
        AccountFactory.get_account()
        AccountFactory.get_account()

        assert Account.objects.count() == 2
        Account.objects.active().all().delete()
        assert Account.objects.count() == 2

        for a in Account.objects.active().all():
            assert a.is_active is False

    @pytest.mark.django_db
    def notest_delete03(self):
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

        Account.objects.delete_account(a.id, is_test=True)

        for obj in Account.objects.active().all():
            assert obj.is_active is False

        for obj in Transaction.objects.all():
            assert obj.is_active is False

    @pytest.mark.django_db
    def notest_delete04(self):
        """
        When delete account, if account's member has only this account,
        member also should be deleted.
        """
        a = AccountFactory.get_account()
        m = a.member

        assert a.is_active is True
        assert m.is_active is True

        Account.objects.delete_account(a.id, is_test=True)
        a.refresh_from_db()
        m.refresh_from_db()

        assert a.is_active is False
        assert m.is_active is False

    @pytest.mark.django_db
    def test_delete05(self):
        """
        When delete account, if account's member has multiple accounts,
        member still should be available.
        """
        m = MemberFactory.get_member()
        a1 = AccountFactory.get_account(member=m)
        a2 = AccountFactory.get_account(member=m)

        for obj in (m, a1, a2):
            assert getattr(obj, 'is_active') is True

        Account.objects.delete_account(a1.id, is_test=True)
        a1.refresh_from_db()
        m.refresh_from_db()

        assert a1.is_active is False
        assert m.is_active is True
