import datetime
import json
import pytest
from finance.services.plaid_api import PlaidApi
from finance.models import Account, Institution, Item
from .import base
from .factories import (
    AccountFactory, InstitutionFactory, ItemFactory, UserFactory)


class TestPlaid(base.Mixin):
    USERNAME = 'user_good'
    PASSWORD_GOOD = 'pass_good'

    @pytest.mark.django_db
    def notest_echange_token(self):
        """
        Exchange public_token for access token.
        """
        item = ItemFactory.get_plaid_item()
        access_token = item.access_token

        pa = PlaidApi()
        public_token = pa.create_public_token(access_token)
        access_token = pa.exchange_public_token(public_token)
        assert access_token is not None
        assert isinstance(access_token, str)

    @pytest.mark.django_db
    def notest_create_institution(self):
        """
        Test model's manager.
        If institution does not exist in database, query it from API.
        """
        plaid_id = 'ins_109508'
        i = Institution.objects.get_or_create_institution(plaid_id)
        assert isinstance(i, Institution) is True
        assert Institution.objects.count() == 1

    @pytest.mark.django_db
    def notest_create_item01(self):
        """
        Test to create Item in plaid.
        Factory method "get_plaid_item" do the same.
        """
        user = UserFactory.get_user()
        i = InstitutionFactory.get_institution()
        pa = PlaidApi()
        api_data = pa.create_item(
            self.USERNAME, self.PASSWORD_GOOD, i.plaid_id)

        item = Item.objects.create_item(user, api_data)
        assert isinstance(item, Item) is True

    @pytest.mark.django_db
    def notest_create_accounts01(self):
        """
        Test model's manager method.
        """
        item = ItemFactory.get_plaid_item()
        token = item.access_token
        pa = PlaidApi()
        api_data = pa.get_accounts(token)
        Account.objects.create_or_update_accounts(item, api_data)
        count = Account.objects.count()
        assert count > 0
        Account.objects.create_or_update_accounts(item, api_data)
        assert Account.objects.count() == count

    @pytest.mark.django_db
    def test_01(self):
        # a = AccountFactory.get_account()
        # print(a.__dict__)

        item = ItemFactory.get_plaid_item()
        token = item.access_token
        pa = PlaidApi()
        
        import time
        time.sleep(20)
        res = pa.get_transactions(token)
        print(res)

"""
    'payment_meta': {
        'ppd_id': None,
        'by_order_of': None,
        'reference_number': None,
        'payment_method': None,
        'payee': None,
        'reason': None,
        'payment_processor': None,
        'payer': None
    },
    'location': {
        'state': None,
        'zip': None,
        'address': None,
        'store_number': None,
        'lon': None,
        'city': None,
        'lat': None
    },

    'account_id': 'lKq9RqjWQmIlpw1zpeKGUw7wkD8EbaSp9RzMb',
    'pending': False,
    'pending_transaction_id': None,
    'category': None,
    'transaction_type': 'unresolved',
    'amount': 5.4,
    'date': '2017-04-01',
    'name': 'Uber 063015 SF**POOL**',
    'category_id': None,
    'transaction_id': 'nzBM6BepQRiKmjp3mZzGce4oD454RniAxQ7J4'
"""