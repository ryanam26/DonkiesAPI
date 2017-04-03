import pytest
from finance.models import Account, Item, Transaction
from .factories import AccountFactory, ItemFactory, TransactionFactory
from . import base


class TestItems(base.Mixin):
    @pytest.mark.django_db
    def test_delete01(self):
        """
        Instead of deleting object should set is_active=False
        """
        item = ItemFactory.get_item()
        assert item.is_active is True

        item.delete()
        item.refresh_from_db()
        assert item.is_active is False

    @pytest.mark.django_db
    def test_delete02(self):
        """
        Instead of deleting queryset, should set is_active=False
        """
        ItemFactory.get_item()
        ItemFactory.get_item()

        assert Item.objects.count() == 2
        Item.objects.all().delete()
        assert Item.objects.count() == 2

        for m in Item.objects.all():
            assert m.is_active is False

    @pytest.mark.django_db
    def test_delete03(self):
        """
        Test calling Item.objects.delete_item method.
        All Accounts and Transactions of deleted Item should be set
        to is_active=False
        """
        item = ItemFactory.get_item()

        AccountFactory.get_account(item=item)
        a = AccountFactory.get_account(item=item)

        TransactionFactory.get_transaction(account=a)

        assert Item.objects.count() == 1
        assert Account.objects.count() == 2
        assert Transaction.objects.count() == 1

        Item.objects.delete_item(item.id, is_delete_plaid=False)

        for obj in Item.objects.all():
            assert obj.is_active is False

        for obj in Account.objects.active().all():
            assert obj.is_active is False

        for obj in Transaction.objects.all():
            assert obj.is_active is False
