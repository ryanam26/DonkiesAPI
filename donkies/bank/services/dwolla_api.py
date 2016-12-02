import dwollav2
import requests
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

    def get_api_url(self):
        """
        For RAW requests.
        """
        if settings.DWOLLA_API_MODE == 'PROD':
            return 'https://api.dwolla.com/'
        return 'https://api-uat.dwolla.com/'

    def get_headers(self):
        return {'Idempotency-Key': uuid.uuid4().hex}

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

    def get_customers(self):
        r = self.token.get('customers')
        return r.body['_embedded']['customers']

    def get_customer_by_email(self, email):
        """
        Returns customer or None
        """
        r = self.token.get('customers', search=email)
        try:
            return r.body['_embedded']['customers'][0]
        except:
            return None

    def create_customer(self, data):
        r = self.token.post('customers', data)
        if r.status == 201:
            return True
        return False

    def update_customer(self):
        pass

    def test(self):
        # res = self.token.get('/')
        # print(res.body)
        # self.create_cutomer()
        # return
        self.get_customer_by_email('jd2@doe.com')
        return

        for c in self.get_customers():
            # c.pop('_links')
            print(c)
            print('---')

if __name__ == '__main__':
    from subprocess import Popen, PIPE

    src = '/home/vlad/dev/web/dj/d/donkies/project/donkies/bank/services/'
    src += 'dwolla_api.py'

    dst = '/home/alex/dj/donkies/donkies/bank/services/'

    cmd = 'alex@159.203.137.132:{}'.format(dst)

    p = Popen(['scp', src, cmd], stdout=PIPE)
    p.communicate()[0]
