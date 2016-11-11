import pytest
import time
from django.conf import settings
from rest_framework.test import APIClient
from web.models import User, Token
from finance.models import Credentials, Member
from .import base


@pytest.fixture(scope='session')
def django_db_setup():
    pass


class TestAtrium(base.Mixin):
    """
    Test calls to atrium API.
    Tests on real database (only getting).
    New results do not saved.
    """
    def init(self):
        self.email = settings.TEST_USER_EMAIL
        self.password = settings.TEST_USER_PASSWORD

    def get_auth_client(self, user):
        client = APIClient()
        token = Token.objects.get(user_id=user.id)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        return client

    def get_credentials(self):
        """
        Mock Chase Bank credentials for creating member.
        """
        login = Credentials.objects.get(
            institution__code='chase', field_name='LOGIN')
        password = Credentials.objects.get(
            institution__code='chase', field_name='PASSWORD')
        return [
            {'guid': login.guid, 'value': 'Bob1111'},
            {'guid': password.guid, 'value': '11111111'},
        ]

    def real_response(self):
        """
        Real response from atrium when create new member.
        """
        return {
            'guid': 'MBR-c8920871-c461-0a06-8ece-c4bc33e95855',
            'successfully_aggregated_at': None,
            'status': 'INITIATED',
            'institution_code': 'chase',
            'metadata': None,
            'identifier': None,
            'aggregated_at': '2016-11-11T17:12:36+00:00',
            'user_guid': 'USR-bbd4be28-38bd-f870-5c77-6241952bfb36',
            'name': 'Chase Bank'
        }

    @pytest.mark.django_db
    def test_user(self, client):
        """
        When user created in django, by celery it should register
        in atrium.
        """
        self.init()
        user = User.objects.get(email=self.email)
        assert user.guid is not None
        assert user.is_atrium_created is True

    @pytest.mark.django_db
    def test_member(self, client):
        """
        Create member for test user and "chase" institution.
        """
        self.init()
        user = User.objects.get(email=self.email)

        d = {
            'user_guid': user.guid,
            'code': 'chase',
            'credentials': self.get_credentials()
        }

        m = Member.objects.get_or_create_member(**d)
        print(m.status)
        for _ in range(5):
            status = Member.objects.get_status(m)
            print(status)
            time.sleep(1)
