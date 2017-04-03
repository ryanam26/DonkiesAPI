from django.conf import settings
from web.services.helpers import catch_exception
from plaid import Client


class PlaidApi:
    def __init__(self):
        env = settings.PLAID_ENV
        if env not in ['production', 'development', 'sandbox']:
            raise ValueError('Incorrect value for PLAID_ENV in settings.')

        self.client = Client(
            client_id=settings.PLAID_CLIENT_ID,
            secret=settings.PLAID_SECRET,
            public_key=settings.PLAID_PUBLIC_KEY,
            environment=env)

    @catch_exception
    def create_item(
            self, username, password, institution_plaid_id,
            initial_products=None):
        """
        Used for tests in sandbox environment.
        In development and production mode Items created
        by Plaid Link via frontend.
        """
        if initial_products is None:
            initial_products = ['transactions', 'auth']
        return self.client.Item.create(
            credentials=dict(username=username, password=password),
            institution_id=institution_plaid_id,
            initial_products=initial_products,
            webhook='https://example.com/webhook')
