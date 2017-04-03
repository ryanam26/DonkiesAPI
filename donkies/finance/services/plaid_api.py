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

    def get_categories(self):
        return self.client.Categories.get()

    def get_institutions(self, count, offset=0):
        """
        Example response:
        {
            'total': 9147,
            'request_id': 'U7KD1',
            'institutions': [
                {
                    'has_mfa': True,
                    'name': 'Bank of America',
                    'credentials': [
                        {
                            'type': 'text',
                            'label': 'Online ID',
                            'name': 'username'
                        },
                        {
                            'type': 'password',
                            'label': 'Password',
                            'name': 'password'
                        }
                    ],
                    'products': ['auth', 'balance'],
                    'institution_id': 'ins_1',
                    'mfa': ['questions(3)']
                },
                ...
            ]
        }
        """
        return self.client.Institutions.get(count, offset)

    def get_institution(self, plaid_id):
        return self.client.Institutions.get_by_id(plaid_id)
