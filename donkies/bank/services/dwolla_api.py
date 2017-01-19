import dwollav2
import json
import logging
import os
import uuid
from django.conf import settings


class DwollaApi:
    def __init__(self):
        self.rs = settings.REDIS_DB

        mode = settings.DWOLLA_API_MODE
        if mode not in ['PROD', 'DEV']:
            raise ValueError('Dwolla API mode should be "PROD" or "DEV"')

        environment = 'sandbox' if mode == 'DEV' else 'production'

        self.client_id = getattr(settings, 'DWOLLA_ID_{}'.format(mode))
        self.client_secret = getattr(settings, 'DWOLLA_SECRET_{}'.format(mode))

        # Recepient Donkies LLC bank account's email.
        self.donkies_email = getattr(
            settings, 'DONKIES_DWOLLA_EMAIL_{}'.format(mode))

        self.client = dwollav2.Client(
            id=self.client_id,
            secret=self.client_secret,
            environment=environment)
        self.token = self.client.Auth.client()

    def is_duplicate(self, e):
        if isinstance(e, dwollav2.ValidationError):
            for d in e.body['_embedded']['errors']:
                if d['code'].lower() == 'duplicate':
                    return True
        elif isinstance(e, dwollav2.Error):
            if e.body['code'].lower() == 'duplicateresource':
                return True
        return False

    def set_logs(self, *args):
        logger = logging.getLogger('dwolla')
        s = '-------\n'.join(args)
        logger.error(s)

    def get_api_url(self):
        """
        For RAW requests.
        """
        if settings.DWOLLA_API_MODE == 'PROD':
            return 'https://api.dwolla.com/'
        return 'https://api-uat.dwolla.com/'

    def get_headers(self):
        return {'Idempotency-Key': uuid.uuid4().hex}

    def get_id_from_headers(self, headers):
        return os.path.basename(headers['location'])

    def get_customer_url(self, id):
        return 'customers/{}'.format(id)

    def get_iav_token_url(self, customer_id):
        return 'customers/{}/iav-token'.format(customer_id)

    def get_customer_funding_sources_url(self, customer_id):
        return 'customers/{}/funding-sources'.format(customer_id)

    def get_funding_source_url(self, id):
        return 'funding-sources/{}'.format(id)

    def get_micro_deposit_url(self, id):
        return 'funding-sources/{}/micro-deposits'.format(id)

    def get_transfer_url(self, id):
        return 'transfers/{}'.format(self.id)

    def create_customer(self, data):
        """
        Returns id of created customer or None.
        """
        try:
            r = self.token.post('customers', data)
            if r.status == 201:
                return self.get_id_from_headers(r.headers)
        except dwollav2.Error as e:
            if self.is_duplicate(e):
                res = self.get_customer_by_email(data['email'])
                if res is not None:
                    return res['id']
            self.set_logs(
                'Create customer', json.dumps(data), str(e))
        return None

    def get_customers(self):
        r = self.token.get('customers')
        return r.body['_embedded']['customers']

    def get_customer(self, id):
        """
        Returns customer by id.
        """
        url = self.get_customer_url(id)
        r = self.token.get(url)
        return r.body

    def get_customer_by_email(self, email):
        """
        Returns customer or None.
        """
        r = self.token.get('customers', email=email)
        try:
            return r.body['_embedded']['customers'][0]
        except:
            return None

    def get_iav_token(self, customer_id):
        """
        Returns token or None (if fails)
        """
        url = self.get_iav_token_url(customer_id)
        try:
            r = self.token.post(url)
            token = r.body['token']
        except:
            token = None
        return token

    def update_customer(self, id):
        pass

    def create_funding_source(self, customer_id, data):
        """
        Manual creation via account_number and routing_number.
        Create funding source for customer.
        Returns id of created funding source or None.
        """
        url = self.get_customer_funding_sources_url(customer_id)
        try:
            r = self.token.post(url, data)
            if r.status == 201:
                return self.get_id_from_headers(r.headers)
        except dwollav2.Error as e:
            if self.is_duplicate(e):
                return self.get_funding_source_by_name(
                    customer_id, data['name'])['id']
            self.set_logs(
                'Create funding source',
                'Customer: {}'.format(customer_id),
                json.dumps(data), str(e))
        return None

    def get_funding_sources(self, customer_id):
        """
        Returns customer's funding sources.
        """
        url = self.get_customer_funding_sources_url(customer_id)
        r = self.token.get(url)
        return r.body['_embedded']['funding-sources']

    def get_funding_source(self, id):
        """
        Returns funding source by id.
        """
        r = self.token.get(self.get_funding_source_url(id))
        return r.body

    def get_funding_source_by_name(self, customer_id, name):
        """
        Returns customer's account or None
        """
        for d in self.get_funding_sources(customer_id):
            if d['name'] == name:
                return d
        return None

    def remove_funding_source(self, id):
        self.token.delete(self.get_funding_source_url(id))

    def init_micro_deposits(self, id):
        """
        Initiates micro-deposits verification for funding source.
        """
        url = self.get_micro_deposit_url(id)
        self.token.post(url)

    def get_micro_deposits(self, id):
        """
        Returns dict with status and created for micro-deposits
        for funding source.
        """
        url = self.get_micro_deposit_url(id)
        r = self.token.get(url)
        if r.status == 200:
            return r.body
        return None

    def verify_micro_deposits(
            self, id, amount1, amount2, currency1='USD', currency2='USD'):
        """
        Live method, that calls directly from front-end (not celery)
        Returns status code and error (if status is not 200)
        """
        url = self.get_micro_deposit_url(id)
        d = {
            'amount1': {
                'value': amount1,
                'currency': currency1
            },
            'amount2': {
                'value': amount2,
                'currency': currency2
            }
        }
        try:
            r = self.token(url, d)
            if r.status == 200:
                return r.status, None
            raise dwollav2.Error('Try again later.')
        except dwollav2.Error as e:
            return r.status, str(e)

    def initiate_transfer(self, src_id, amount, currency='USD'):
        """
        Source: funding source.
        Destination: funding source.
        Returns id of created transfer or None.
        """
        src_url = '{}funding-sources/{}'.format(self.get_api_url(), src_id)
        dst_url = 'mailto:{}'.format(self.donkies_email)
        d = {
            '_links': {
                'source': {
                    'href': src_url
                },
                'destination': {
                    'href': dst_url
                }
            },
            'amount': {
                'currency': currency,
                'value': amount
            }
        }
        try:
            r = self.token.post('transfers', d)
            if r.status == 201:
                return self.get_id_from_headers(r.headers)
        except dwollav2.Error as e:
            print(str(e))
            self.set_logs(
                'Initiate transfer fail', json.dumps(d), str(e))
        return None

    def get_transfer_info(self, id):
        """
        Returns transfer by id.
        """
        url = self.get_transfer_url(id)
        r = self.token.get(url)
        return r.body

    def get_transfer_failure_code(self, id):
        """
        Returns 3-letters failure code.
        All codes listed in docs:
        /resources/bank-transfer-workflow/transfer-failures.html
        """
        url = self.get_transfer_url(id)
        url += '/failure'
        try:
            r = self.token.get(url)
            code = r.body['code']
        except:
            code = None
        return code

    def create_test_customer(self):
        d = {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': '{}@nomail.net'.format(uuid.uuid4().hex),
            'type': 'personal',
            'address1': '99-99 33rd St',
            'city': 'Some City',
            'state': 'NY',
            'postalCode': '11101',
            'dateOfBirth': '1970-01-01',
            'ssn': '1234'
        }
        id = self.create_customer(d)
        if id is not None:
            return self.get_customer(id)
        return id

    def create_test_funding_source(self, customer_id):
        data = {
            'routingNumber': '222222226',
            'accountNumber': '123456789',
            'type': 'savings',
            'name': 'My Bank'
        }
        id = self.create_funding_source(customer_id, data)
        if id is not None:
            return self.get_funding_source(id)
        return id
