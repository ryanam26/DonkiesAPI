import dwollav2
import requests
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
            return 'https://api-uat.dwolla.com/'
        return 'https://api.dwolla.com/'

    @property
    def application_token_url(self):
        return '{}oauth/v2/token'.format(self.get_api_url())

    def get_application_token(self):
        """
        Not working.
        """
        dic = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        headers = {'content-type': 'application/json'}
        r = requests.post(
            self.application_token_url, json=dic, headers=headers)
        print(r.text)

    def init(self):
        self.token = self.client.Token(
            access_token=self.access_token,
            refresh_token=self.refresh_token)

    def test(self):
        self.init()
        print(self.access_token)
        print(self.refresh_token)
