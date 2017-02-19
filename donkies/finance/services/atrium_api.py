import json
from django.conf import settings
from web.services.helpers import catch_exception
from atrium import Api


class AtriumApi:
    def __init__(self):
        mode = settings.ATRIUM_API_MODE
        if mode not in ['PROD', 'DEV']:
            raise ValueError('Atrium API mode should be "PROD" or "DEV"')

        self.client_id = getattr(settings, 'ATRIUM_CLIENT_ID_{}'.format(mode))
        self.api_key = getattr(settings, 'ATRIUM_KEY_{}'.format(mode))

        self.api = Api(
            key=self.api_key, client_id=self.client_id,
            root=self.get_root_url())

    def get_root_url(self):
        if settings.ATRIUM_API_MODE == 'PROD':
            return 'https://atrium.mx.com/'
        return 'https://vestibule.mx.com/'

    @catch_exception
    def get_users(self):
        return self.api.getUsers()

    @catch_exception
    def get_user(self, guid):
        return self.api.readUser(guid)

    @catch_exception
    def delete_user(self, guid):
        self.api.deleteUser(guid)
        print('Atrium user has been deleted')

    @catch_exception
    def create_user(self, identifier, metadata=None):
        """
        Returns guid of created user.
        """
        d = {'identifier': identifier}
        if metadata is not None:
            d['metadata'] = json.dumps(metadata)
        res = self.api.createUser(payload=d)
        return res.guid

    @catch_exception
    def search_institutions(self, **kw):
        return self.api.getInstitutions(queryParams=kw)

    @catch_exception
    def get_credentials(self, code):
        """
        Get all credentials for particular institution.
        """
        return self.api.getCredentials(code)

    @catch_exception
    def get_members(self, user_guid, **kw):
        return self.api.getMembers(user_guid, queryParams=kw)

    @catch_exception
    def create_member(self, user_guid, code, credentials):
        """
        credentials is the list of dicts: {guid:..., value:...}
        Note:
            When we create member in Atrium twice, for same
            user guid, same institution and even same credentials,
            Atrium consider it as new member and creates new member.
        """
        member = self.api.createMember(user_guid, payload={
            "institution_code": code,
            "credentials": credentials
        })
        return member

    @catch_exception
    def get_member(self, user_guid, member_guid):
        """
        Provides the status of the member's
        most recent aggregation.

        Result contains:
            aggregated_at
            successfully_aggregated_at
            status
            guid
            has_processed_transactions
            has_processed_accounts
        """
        return self.api.getMemberStatus(user_guid, member_guid)

    @catch_exception
    def read_member(self, user_guid, member_guid):
        """
        Result contains:
            aggregated_at
            successfully_aggregated_at
            institution_code
            status
            guid
            user_guid
            name
            identifier
        """
        return self.api.readMember(user_guid, member_guid)

    @catch_exception
    def aggregate_member(self, user_guid, member_guid):
        return self.api.startMemberAgg(user_guid, member_guid)

    @catch_exception
    def resume_member(self, user_guid, member_guid, challenges=[]):
        d = {}
        if challenges:
            d['challenges'] = challenges
        return self.api.resumeMemberAgg(user_guid, member_guid, payload=d)

    @catch_exception
    def delete_member(self, user_guid, member_guid):
        self.api.deleteMember(user_guid, member_guid)

    @catch_exception
    def get_accounts(self, user_guid, **kw):
        return self.api.getAccounts(user_guid, queryParams=kw)

    @catch_exception
    def get_transactions(self, user_guid, **kw):
        return self.api.getTransactions(user_guid, queryParams=kw)
