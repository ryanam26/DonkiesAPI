import dwollav2
import json
import logging
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

    def get_customer_funding_sources_url(self, customer_id):
        return 'customers/{}/funding-sources'.format(customer_id)

    # def get_application_token(self):
    #     url = '{}oauth/v2/token'.format(self.get_api_url())
    #     dic = {
    #         'client_id': self.client_id,
    #         'client_secret': self.client_secret,
    #         'grant_type': 'client_credentials'
    #     }
    #     headers = {'content-type': 'application/vnd.dwolla.v1.hal+json'}
    #     r = requests.post(url, json=dic, headers=headers)
    #     print(r.text)

    # def init(self):
    #     self.token = self.client.Token(
    #         access_token=self.access_token,
    #         refresh_token=self.refresh_token,
    #         account_id='0a2ea230-5dc7-46e5-815c-98c03de64ec9')

    def create_customer(self, data):
        try:
            self.token.post('customers', data)
        except dwollav2.ValidationError as e:
            self.set_logs(
                'Create customer', json.dumps(data), str(e))

    def get_customers(self):
        r = self.token.get('customers')
        return r.body['_embedded']['customers']

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
        """
        url = self.get_customer_funding_sources_url(customer_id)
        try:
            self.token.post(url, data)
        except dwollav2.ValidationError as e:
            print(str(e))
            self.set_logs(
                'Create funding source',
                'Customer: {}'.format(customer_id),
                json.dumps(data), str(e))

    def get_funding_sources(self, customer_id):
        """
        Returns customer's funding sources.
        """
        url = self.get_customer_funding_sources_url(customer_id)
        r = self.token.get(url)
        return r.body['_embedded']['funding-sources']

    def get_funding_source(self, id):
        url = 'funding-sources/{}'.format(id)
        r = self.token.get(url)
        return r.body

    def get_funding_source_by_name(self, customer_id, name):
        """
        Returns customer's account or None
        """
        for d in self.get_funding_sources(customer_id):
            if d['name'] == name:
                return d
        return None

    def test(self):
        # for c in self.get_customers():
        #     if c['status'] == 'verified':
        #         print(c)
        customer_id = '5d98f995-8f3f-47f6-9d26-f30c1e543673'
        # l = self.get_funding_sources(customer_id)

        # data = {
        #     'routingNumber': '222222226',
        #     'accountNumber': '123456789',
        #     'type': 'checking',
        #     'name': 'My Bank'
        # }
        # self.create_funding_source(customer_id, data)
        fs = self.get_funding_source_by_name(customer_id, 'My Bank')
        print(fs)


if __name__ == '__main__':
    from subprocess import Popen, PIPE

    src = '/home/vlad/dev/web/dj/d/donkies/project/donkies/bank/services/'
    src += 'dwolla_api.py'

    dst = '/home/alex/dj/donkies/donkies/bank/services/'

    cmd = 'alex@159.203.137.132:{}'.format(dst)

    p = Popen(['scp', src, cmd], stdout=PIPE)
    p.communicate()[0]
