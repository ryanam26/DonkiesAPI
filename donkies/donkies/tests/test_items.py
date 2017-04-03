import pytest
from finance.models import Account, Transaction
from . import base
from .factories import AccountFactory, MemberFactory, TransactionFactory


class TestItems(base.Mixin):
    @pytest.mark.django_db
    def notest_delete01(self):
        """
        Instead of deleting object should set is_active=False
        """
        m = MemberFactory.get_member()
        assert m.is_active is True

        m.delete()
        m.refresh_from_db()
        assert m.is_active is False

    @pytest.mark.django_db
    def notest_delete02(self):
        """
        Instead of deleting queryset, should set is_active=False
        """
        MemberFactory.get_member()
        MemberFactory.get_member()

        assert Member.objects.count() == 2
        Member.objects.all().delete()
        assert Member.objects.count() == 2

        for m in Member.objects.all():
            assert m.is_active is False

    @pytest.mark.django_db
    def notest_delete03(self):
        """
        Test calling Member.objects.delete_member method.
        All Accounts and Transactions of deleted Member should be set
        to is_active=False
        """
        m = MemberFactory.get_member()

        AccountFactory.get_account(member=m)
        a = AccountFactory.get_account(member=m)

        TransactionFactory.get_transaction(account=a)

        assert Member.objects.count() == 1
        assert Account.objects.count() == 2
        assert Transaction.objects.count() == 1

        Member.objects.delete_member(m.id, is_delete_atrium=False)

        for obj in Member.objects.all():
            assert obj.is_active is False

        for obj in Account.objects.active().all():
            assert obj.is_active is False

        for obj in Transaction.objects.all():
            assert obj.is_active is False

    @pytest.mark.django_db
    def notest_delete04(self):
        """
        Test real deleting. Member should be deleted from database.
        """
        m = MemberFactory.get_member()
        Member.objects.real_delete_member(m.id)

        assert Member.objects.filter(id=m.id).exists() is False