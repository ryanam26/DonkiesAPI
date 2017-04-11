import pytest
from django.conf import settings
from ach.services.stripe_api import StripeApi
from finance.services.plaid_api import PlaidApi
from ach.models import TransferStripe
from donkies.tests.factories import AccountFactory, ItemFactory
from donkies.tests import base


class TestStripe(base.Mixin):
    """
    After obtaining stripe_token for account: there are 2 ways.
    1) We can create customer using this token and then associate
       customer with charges.
    2) We can use this stripe token as "source" to charges.
       Stripe token can be used only once.
       Using this method in the app.
    """
    def init(self):
        """
        In order not to create access_token each time,
        store in Redis.
        """
        pa = PlaidApi()
        rs = settings.REDIS_DB

        access_token = rs.get('access_token')
        if access_token is None:
            item = ItemFactory.get_plaid_item()
            access_token = item.access_token
            rs.set('access_token', access_token)

            res = pa.get_accounts(access_token)
            accounts = res['accounts']
            accounts = [acc for acc in accounts if acc['type'] == 'depository']
            acc = accounts[0]
            rs.set('account_id', acc['account_id'])

        access_token = rs.get('access_token').decode()
        account_id = rs.get('account_id').decode()

        self.account = AccountFactory.get_account()
        self.account.access_token = access_token
        self.account.plaid_id = account_id
        self.account.save()

    @pytest.mark.django_db
    def test_create_customer01(self):
        """
        Debug.
        To get Stripe token: Plaid account and Stripe account
        should be linked via Plaid dashboard.
        We need access_token and account_id.
        """
        return
        self.init()
        token = self.account.get_stripe_token()
        sa = StripeApi()
        customer = sa.create_customer(token, 'some description')
        print(customer)

    @pytest.mark.django_db
    def test_create_charge01(self):
        """
        Debug.
        Test Stripe's API.
        """
        return
        self.init()
        token = self.account.get_stripe_token()
        sa = StripeApi()
        stripe_charge = sa.create_charge('10.20', token)
        print(stripe_charge)

    @pytest.mark.django_db
    def test_create_charge02(self):
        """
        Test manager's method.
        """
        self.init()
        ts = TransferStripe.objects.create_charge(
            self.account, '10.56')
        print(ts.__dict__)
