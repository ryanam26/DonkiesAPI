import dwollav2
import json
import requests
from django.conf import settings


class DwollaApi:
    def __init__(self):
        mode = settings.DWOLLA_API_MODE
        if mode not in ['PROD', 'DEV']:
            raise ValueError('Dwolla API mode should be "PROD" or "DEV"')

        environment = 'sandbox' if mode == 'DEV' else 'live'

        api_key = getattr(settings, 'DWOLLA_KEY_{}'.format(mode))
        api_secret = getattr(settings, 'DWOLLA_SECRET_{}'.format(mode))

        self.client = dwollav2.Client(
            id=api_key,
            secret=api_secret,
            environment=environment)

    def get_root_url(self):
        """
        For RAW requests.
        """
        if settings.DWOLLA_API_MODE == 'PROD':
            return 'https://api-uat.dwolla.com/'
        return 'https://api.dwolla.com/'

    def test(self):
        token = self.client.Auth.client()
        print(token)
