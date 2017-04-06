import pytest
from django.conf import settings
from ach.services.stripe_api import StripeApi
from finance.services.plaid_api import PlaidApi
from .import base
from .factories import ItemFactory, UserFactory


class TestStripe(base.Mixin):
    def get_stripe_token(self):
        """
        In order not to create token each time,
        store in Redis.
        """
        rs = settings.REDIS_DB

        token = rs.get('stripe_token')
        if token is None:
            item = ItemFactory.get_plaid_item()
            access_token = item.access_token

            pa = PlaidApi()
            res = pa.get_accounts(access_token)
            accounts = res['accounts']
            accounts = [acc for acc in accounts if acc['type'] == 'depository']
            acc = accounts[0]

            token = pa.get_stripe_token(access_token, acc['account_id'])
            rs.set('stripe_token', token)
        else:
            token = token.decode()
        return token

    @pytest.mark.django_db
    def test_01(self):
        """
        To get Stripe token: Plaid account and Stripe account
        should be linked via Plaid dashboard.
        We need access_token and account_id.
        """
        token = self.get_stripe_token()
        sa = StripeApi()
        customer = sa.create_customer(token, 'some description')
        print(customer)