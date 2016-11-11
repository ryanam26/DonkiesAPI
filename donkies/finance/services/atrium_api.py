import json
import requests
from django.conf import settings
from atrium import Api


class AtriumApi:
    def __init__(self):
        mode = settings.ATRIUM_API_MODE
        if mode not in ['PROD', 'DEV']:
            raise ValueError('Atrium API mode should be "PROD" or "DEV"')

        self.client_id = getattr(settings, 'ATRIUM_CLIENT_ID_{}'.format(mode))
        self.api_key = getattr(settings, 'ATRIUM_KEY_{}'.format(mode))

        self.api = Api(key=self.api_key, client_id=self.client_id)
        self.api.root = self.get_root_url()

    def get_root_url(self):
        if settings.ATRIUM_API_MODE == 'PROD':
            return 'https://atrium.mx.com/'
        return 'https://vestibule.mx.com/'

    def get_headers(self):
        """
        Pytrium API does not support all methods.
        Returns headers to call API manually.
        """
        d = {}
        d['Accept'] = 'application/vnd.mx.atrium.v1+json'
        d['MX-API-Key'] = self.api_key
        d['MX-Client-ID'] = self.client_id
        return d

    def get_users(self):
        """
        Resource is not available (404): How to get all users?
        """
        url = self.get_root_url() + 'users'
        res = requests.get(url, headers=self.get_headers())
        print(res)

    def create_user(self, identifier, metadata=None):
        """
        Returns guid of created user.
        TODO: processing errors.
        """
        d = {'identifier': identifier}
        if metadata is not None:
            d['metadata'] = json.dumps(metadata)
        res = self.api.createUser(payload=d)
        return res.guid

    def get_credentials(self, code):
        """
        Get all credentials for particular institution.
        """
        return self.api.getCredentials(code)

    def create_member(self, user_guid, code, credentials):
        """
        credentials is the list of dicts: {guid:..., value:...}
        TODO: processing errors.
        """
        member = self.api.createMember(user_guid, payload={
            "institution_code": code,
            "credentials": credentials
        })
        return member

    def get_member_status(self, user_guid, member_guid):
        """
        TODO: processing errors.
        """
        status = self.api.getMemberStatus(user_guid, member_guid)
        return status
