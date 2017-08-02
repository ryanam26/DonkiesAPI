import datetime
import time
from django.conf import settings
from web.services.helpers import catch_exception
from plaid import Client
from plaid.errors import PlaidError


class PlaidApi:
    """
    Documentation for Plaid API:
    https://plaid.github.io/plaid-python/index.html
    https://github.com/plaid/plaid-python
    """

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
        api_data = self.client.Item.create(
            credentials=dict(username=username, password=password),
            institution_id=institution_plaid_id,
            initial_products=initial_products,
            webhook='https://example.com/webhook')
        d = api_data['item']
        d['access_token'] = api_data['access_token']
        return d

    def get_item(self, access_token):
        api_data = self.client.Item.get(access_token)
        d = api_data['item']
        d['request_id'] = api_data['request_id']
        d['access_token'] = access_token
        return d

    def delete_item(self, access_token):
        self.client.Item.delete(access_token)

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
        d = self.client.Institutions.get_by_id(plaid_id)
        return d['institution']

    def get_accounts(self, access_token):
        """
        Returns accounts for particular item.
        """
        return self.client.Accounts.get(access_token)

    def get_accounts_info(self, access_token):
        """
        Returns extended accounts with account's numbers.
        """
        return self.client.Auth.get(access_token)

    def get_balances(self, access_token):
        """
        Returns accounts with balances.
        """
        return self.client.Accounts.balance.get(access_token)

    def create_public_token(self, access_token):
        """
        Returns public_token (string).
        """
        d = self.client.Item.public_token.create(access_token)
        return d['public_token']

    def dwolla_processor_token(self, access_token, account_id):
        url = settings.DWOLLA_PROCESSOR_TOKEN_CREATE

        return self.client.post(url, {"client_id": settings.PLAID_CLIENT_ID,
                                      "secret": settings.PLAID_SECRET,
                                      "access_token": access_token,
                                      "account_id": account_id})

    def exchange_public_token(self, public_token, account_id):
        """
        Frontend Link returns public_token.
        We need to exchange it for access token.
        Returns access_token (string).
        """
        exchange_token_response = self.client.Item.public_token.exchange(public_token)

        dwolla_token = self.dwolla_processor_token(exchange_token_response['access_token'],
                                    account_id)

        return exchange_token_response['access_token']

    def rotate_access_token(self, access_token):
        """
        Updates access token.
        Returns access_token (string).
        """
        d = self.client.Item.access_token.invalidate(access_token)
        return d['new_access_token']

    def get_stripe_token(self, access_token, account_id):
        d = self.client.Processor.stripeBankAccountTokenCreate(
            access_token, account_id)
        return d['stripe_bank_account_token']

    def update_webhook(self, access_token, webhook):
        self.client.update(access_token, webhook)

    def get_identity(self, access_token):
        """
        Requires additional permissions.
        In Sandbox raises error.
        """
        return self.client.Identity.get(access_token)

    def get_income(self, access_token):
        """
        Requires additional permissions.
        In Sandbox raises error.
        """
        return self.client.Income.get(access_token)

    def get_credit_details(self, access_token):
        """
        Requires additional permissions.
        In Sandbox raises error.
        """
        return self.client.CreditDetails.get(access_token)

    def reset_login(self, access_token):
        """
        Sandbox only.
        Put an item into an ITEM_LOGIN_REQUIRED error state.
        """
        self.client.Sandbox.item.reset_login(access_token)

    def get_transactions(self, access_token, start_date=None, end_date=None):
        """
        If start_date is None: set 2 weeks ago.
        If end_date is None: set today.

        "start_date" and "end_date" can be passed as
        Date or DateTime objects.

        If transactions are not ready yet, raises ItemError.
        """
        if start_date is None:
            start_date = datetime.date.today() - datetime.timedelta(days=14)

        if end_date is None:
            end_date = datetime.date.today()

        start_date = start_date.strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d')

        while True:
            try:
                d = self.client.Transactions.get(
                    access_token, start_date=start_date, end_date=end_date)
                break
            except PlaidError as e:
                if e.code == 'PRODUCT_NOT_READY':
                    print('Transactions not ready')
                    time.sleep(20)
                    continue
                raise Exception(e)
        transactions = d['transactions']

        while len(transactions) < d['total_transactions']:
            d = self.client.Transactions.get(
                access_token,
                start_date=start_date,
                end_date=end_date,
                offset=len(transactions)
            )
            transactions.extend(d['transactions'])
        return transactions
