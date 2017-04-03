import copy
import pytest
from finance.services.plaid_api import PlaidApi
from finance.models import Account, Institution, Item, Transaction
from .import base
from .factories import InstitutionFactory, ItemFactory, UserFactory


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
    def notest_create_transactions01(self):
        """
        Long test.
        Transactions are not ready instantly.
        """
        item = ItemFactory.get_plaid_item()
        token = item.access_token
        pa = PlaidApi()
        api_data = pa.get_accounts(token)
        Account.objects.create_or_update_accounts(item, api_data)

        l = Transaction.objects.get_plaid_transactions(item)
        Transaction.objects.create_or_update_transactions(copy.deepcopy(l))

        count = Transaction.objects.count()
        assert count > 0

        Transaction.objects.create_or_update_transactions(copy.deepcopy(l))
        assert Transaction.objects.count() == count
