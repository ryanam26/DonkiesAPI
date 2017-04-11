import decimal
import logging
import stripe
from django.conf import settings

logger = logging.getLogger('app')


class StripeApi:
    def __init__(self):
        mode = settings.STRIPE_API_MODE
        if mode not in ['PROD', 'DEV']:
            raise ValueError('Stripe API mode should be "PROD" or "DEV"')

        if mode == 'PROD':
            stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
        else:
            stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

    def create_customer(self, bank_token, description):
        return stripe.Customer.create(
            source=bank_token, description=description)

    def create_charge(self, amount, stripe_token, description=None):
        """
        "amount" - string or decimal. We convert it to cents, as Stripe
                   accepts Integer cents.
        "stripe_token" - one-time token obtained by Plaid API.
                         Token related to Account.
        """
        if isinstance(amount, str):
            amount = decimal.Decimal(amount)

        amount = int(amount * 100)

        d = dict(
            amount=amount,
            currency='usd',
            source=stripe_token
        )
        if description is not None:
            d['description'] = description

        return stripe.Charge.create(**d)

    def get_charge(self, stripe_id):
        return stripe.Charge.retrieve(stripe_id)
