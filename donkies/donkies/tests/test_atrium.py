import pytest
from django.conf import settings
from rest_framework.test import APIClient
from web.models import User, Token
from .import base


@pytest.fixture(scope='session')
def django_db_setup():
    pass


class TestAtrium(base.Mixin):
    """
    Test calls to atrium API.
    Tests on real database (on getting).
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
        Create member for test user and chase institution.
        """
        self.init()
        user = User.objects.get(email=self.email)

        