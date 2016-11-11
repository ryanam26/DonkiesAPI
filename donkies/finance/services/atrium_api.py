import json
from django.conf import settings
from atrium import Api


class AtriumApi:
    def __init__(self):
        mode = settings.ATRIUM_API_MODE
        if mode not in ['PROD', 'DEV']:
            raise ValueError('Atrium API mode should be "PROD" or "DEV"')

        client_id = getattr(settings, 'ATRIUM_CLIENT_ID_{}'.format(mode))
        key = getattr(settings, 'ATRIUM_KEY_{}'.format(mode))

        self.api = Api(key=key, client_id=client_id)
        self.api.root = self.get_root_url()

    def get_root_url(self):
        if settings.ATRIUM_API_MODE == 'PROD':
            return 'https://atrium.mx.com/'
        return 'https://vestibule.mx.com/'

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
