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

    def search_institutions(self, name=None, code=None):
        d = {}
        if name:
            d['name'] = name
        if code:
            d['code'] = code
        query = self.api.getInstitutions(queryParams=d)
        print(query)

    def get_credentials(self, code):
        """
        Get all credentials for particular institution.
        """
        return self.api.getCredentials(code)

    def get_members(self, user_guid):
        return self.api.getMembers(user_guid)

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

    def get_member(self, user_guid, member_guid):
        """
        TODO: processing errors.
        """
        return self.api.getMemberStatus(user_guid, member_guid)

    def resume_member(self, user_guid, member_guid, challenges=[]):
        d = {}
        if challenges:
            d['challenges'] = challenges
        return self.api.resumeMemberAgg(user_guid, member_guid, payload=d)

    def get_accounts(self, user_guid):
        """
        TODO: processing errors.
              processing paginations.
              add query params.
        """
        return self.api.getAccounts(user_guid)

    def get_transactions(self, user_guid):
        """
        TODO: processing errors.
              processing paginations.
              add query params.
        """
        return self.api.getTransactions(user_guid)
