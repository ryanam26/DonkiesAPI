import json
import pytest
from finance.models import Account, Item, Transaction
from finance.services.plaid_api import PlaidApi
from .factories import (
    AccountFactory, ItemFactory, TransactionFactory, UserFactory)
from . import base


class TestItems(base.Mixin):
    def get_item_api_data(self):
        pa = PlaidApi()
        return pa.create_item(
            ItemFactory.USERNAME, ItemFactory.PASSWORD_GOOD, 'ins_109508')

    def get_public_token(self):
        pa = PlaidApi()
        data = pa.create_item(
            ItemFactory.USERNAME, ItemFactory.PASSWORD_GOOD, 'ins_109508')
        return pa.create_public_token(data['access_token'])

    @pytest.mark.django_db
    def test_create_item01(self):
        """
        Test model's manager's method
        "create_item_by_public_token".
        """
        public_token = self.get_public_token()
        user = UserFactory.get_user()
        item = Item.objects.create_item_by_public_token(user, public_token)
        assert isinstance(item, Item) is True

    @pytest.mark.django_db
    def test_create_item02(self):
        """
        Test create_item API endpoint by public_token.
        """
        public_token = self.get_public_token()
        user = UserFactory.get_user()
        client = self.get_auth_client(user)

        url = '/v1/items'
        dic = {'public_token': public_token}

        data = json.dumps(dic)
        response = client.post(url, data, content_type='application/json')
        assert response.status_code == 201
        assert Item.objects.count() == 1

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

        Item.objects.delete_item(item.id)

        for obj in Item.objects.all():
            assert obj.is_active is False

        for obj in Account.objects.active().all():
            assert obj.is_active is False

        for obj in Transaction.objects.all():
            assert obj.is_active is False
