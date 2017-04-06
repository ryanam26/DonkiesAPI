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
        customer = stripe.Customer.create(
            source=bank_token, description=description)
        print(customer)
