import json
import pytest
from finance.services.plaid_api import PlaidApi
from finance.models import Institution, Item
from .import base
from .factories import (
    InstitutionFactory, ItemFactory, UserFactory)


class TestPlaid(base.Mixin):
    USERNAME = 'user_good'
    PASSWORD_GOOD = 'pass_good'

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
        user = UserFactory.get_user()
        i = InstitutionFactory.get_institution()
        pa = PlaidApi()
        api_data = pa.create_item(
            self.USERNAME, self.PASSWORD_GOOD, i.plaid_id)

        item = Item.objects.create_item(user, api_data)
        assert isinstance(item, Item) is True

    @pytest.mark.django_db
    def test_01(self):
        item = ItemFactory.get_item()
        token = item.access_token

        pa = PlaidApi()
        api_data = pa.get_accounts(token)
        print(api_data)
        
        




        # res = pa.get_balance(token)
        # print('Balance: ---')
        # print(res)
        # print('')

        # res = pa.get_accounts_info(token)
        # print('Accounts Info: ---')
        # print(res)
        # print('')

        # res = pa.get_credit_details(token)
        # print('Credit Details: ---')
        # print(res)
        # print('')

        # res = pa.rotate_access_token(token)
        # print('Rotate access token: ---')
        # print(res)
        # print('')
