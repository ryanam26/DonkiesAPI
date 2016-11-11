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
    TEST_CODE = 'mxbank'
    TEST_USERNAME = 'test_atrium'
    # Using any password:
    # INITIATED -> AUTHENTICATED -> TRANSFERRED -> COMPLETED
    TEST_PASSWORD = 'any'

    # Passwords for particular scenario.
    TEST_CHALLENGE = 'challenge'
    TEST_OPTIONS = 'options'
    TEST_IMAGE = 'image'
    TEST_BAD_REQUEST = 'BAD_REQUEST'
    TEST_UNAUTHORIZED = 'UNAUTHORIZED'
    TEST_INVALID = 'INVALID'
    TEST_LOCKED = 'LOCKED'
    TEST_DISABLED = 'DISABLED'
    TEST_SERVER_ERROR = 'SERVER_ERROR'
    TEST_UNAVAILABLE = 'UNAVAILABLE'

    TEST_CORRECT_ANSWER = 'correct'

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
        Mock MXBank credentials for creating member.
        """
        login = Credentials.objects.get(
            institution__code=self.TEST_CODE, field_name='LOGIN')
        password = Credentials.objects.get(
            institution__code=self.TEST_CODE, field_name='PASSWORD')
        return [
            {'guid': login.guid, 'value': self.TEST_USERNAME},
            {'guid': password.guid, 'value': self.TEST_PASSWORD},
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
        When user created in django, by celery it should be
        registered in atrium.
        """
        self.init()
        user = User.objects.get(email=self.email)
        assert user.guid is not None
        assert user.is_atrium_created is True

    @pytest.mark.django_db
    def test_member(self, client):
        """
        Create member for test user and "mxbank" institution.
        """
        self.init()
        user = User.objects.get(email=self.email)

        d = {
            'user_guid': user.guid,
            'code': self.TEST_CODE,
            'credentials': self.get_credentials()
        }

        m = Member.objects.get_or_create_member(**d)
        print(m.status)
        for _ in range(5):
            status = Member.objects.get_status(m)
            print(status)
            time.sleep(1)
