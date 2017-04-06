import pytest
from finance.services.plaid_api import PlaidApi
from finance.models import Account, Institution, Item, Transaction
from .import base
from .factories import InstitutionFactory, ItemFactory, UserFactory


class TestPlaid(base.Mixin):
    USERNAME = 'user_good'
    PASSWORD_GOOD = 'pass_good'

    @pytest.mark.django_db
    def test_get_stripe_token(self):
        """
        To get Stripe token: Plaid account and Stripe account
        should be linked via Plaid dashboard.
        We need access_token and account_id.
        """
        item = ItemFactory.get_plaid_item()
        access_token = item.access_token

        pa = PlaidApi()
        res = pa.get_accounts(access_token)
        accounts = res['accounts']
        accounts = [acc for acc in accounts if acc['type'] == 'depository']
        acc = accounts[0]

        token = pa.get_stripe_token(access_token, acc['account_id'])
        assert token is not None
        assert isinstance(token, str)

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
    def notest_create_update_accounts01(self):
        """
        Test model's manager method.
        """
        item = ItemFactory.get_plaid_item()
        token = item.access_token
        Account.objects.create_or_update_accounts(token)
        count = Account.objects.count()
        assert count > 0
        Account.objects.create_or_update_accounts(token)
        assert Account.objects.count() == count

    @pytest.mark.django_db
    def notest_create_update_transactions01(self):
        """
        Long test.
        Transactions are not ready instantly.
        """
        item = ItemFactory.get_plaid_item()
        token = item.access_token
        Account.objects.create_or_update_accounts(token)
        Transaction.objects.create_or_update_transactions(token)

        count = Transaction.objects.count()
        assert count > 0

        Transaction.objects.create_or_update_transactions(token)
        assert Transaction.objects.count() == count
