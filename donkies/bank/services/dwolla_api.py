import dwollav2
import json
import logging
import os
import time
import uuid
from django.conf import settings


class DwollaApi:
    """
    Set manually DONKIES_ACCESS_TOKEN and DONKIES_REFRESH_TOKEN
    to Redis. Tokens are received in dashboard.
    Then refresh tokens by celery every half hour.
    """

    def __init__(self):
        self.rs = settings.REDIS_DB

        mode = settings.DWOLLA_API_MODE
        if mode not in ['PROD', 'DEV']:
            raise ValueError('Dwolla API mode should be "PROD" or "DEV"')

        environment = 'sandbox' if mode == 'DEV' else 'production'

        self.client_id = getattr(settings, 'DWOLLA_ID_{}'.format(mode))
        self.client_secret = getattr(settings, 'DWOLLA_SECRET_{}'.format(mode))

        self.client = dwollav2.Client(
            id=self.client_id,
            secret=self.client_secret,
            environment=environment)
        self.token = self.client.Auth.client()

    @property
    def access_token(self):
        return self.rs.get('DONKIES_ACCESS_TOKEN')

    @property
    def refresh_token(self):
        return self.rs.get('DONKIES_REFRESH_TOKEN')

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

    def get_customer_funding_sources_url(self, customer_id):
        return 'customers/{}/funding-sources'.format(customer_id)

    def get_funding_source_url(self, id):
        return 'funding-sources/{}'.format(id)

    def create_customer(self, data):
        """
        Returns id or None.
        """
        try:
            r = self.token.post('customers', data)
            if r.status == 201:
                return self.get_id_from_headers(r.headers)
        except dwollav2.ValidationError as e:
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
        r = self.token.get('customers', search=email)
        try:
            return r.body['_embedded']['customers'][0]
        except:
            return None

    def update_customer(self, id):
        pass

    def create_funding_source(self, customer_id, data):
        """
        Create funding source for customer.
        Returns id or None.
        """
        url = self.get_customer_funding_sources_url(customer_id)
        try:
            r = self.token.post(url, data)
            if r.status == 201:
                return self.get_id_from_headers(r.headers)
        except dwollav2.ValidationError as e:
            print(str(e))
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
        r = self.token.delete(self.get_funding_source_url(id))
        print(r.status)

    def test_create_customer(self):
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
        print('Created customer id', id)
        print('---')
        if id is not None:
            c = self.get_customer(id)
            print(c)
        return id

    def test_create_funding_source(self, customer_id):
        data = {
            'routingNumber': '222222226',
            'accountNumber': '123456789',
            'type': 'checking',
            'name': 'My Bank'
        }
        id = self.create_funding_source(customer_id, data)
        print('Created funding source id:', id)
        print('---')
        if id is not None:
            fs = self.get_funding_source(id)
            print(fs)
        return id

    def test(self):
        customer_id = self.test_create_customer()
        print('---')
        self.test_create_funding_source(customer_id)

if __name__ == '__main__':
    from subprocess import Popen, PIPE

    src = '/home/vlad/dev/web/dj/d/donkies/project/donkies/bank/services/'
    src += 'dwolla_api.py'

    dst = '/home/alex/dj/donkies/donkies/bank/services/'

    cmd = 'alex@159.203.137.132:{}'.format(dst)

    p = Popen(['scp', src, cmd], stdout=PIPE)
    p.communicate()[0]
